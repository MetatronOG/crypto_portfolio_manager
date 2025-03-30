import logging
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env file exists
dotenv_path = Path(__file__).parent.parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Import exchange modules
from .exchanges import BinanceExchange, BybitExchange

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, config, whale_detector=None):
        """Initialize the trade executor with configuration"""
        self.config = config
        self.whale_detector = whale_detector
        self.exchanges = {}
        self.init_exchanges()
        
        # Trading state
        self.active_orders = {}
        self.trading_paused = False
        self.pause_until = None
        
        # Risk adjustment state
        self.risk_adjustment = 1.0  # 1.0 = normal, 0.5 = reduced by 50%, 0.0 = paused
        
    def init_exchanges(self):
        """Initialize exchange connections using our exchange implementations"""
        # Check if exchanges are configured in config
        exchange_configs = self.config.get("exchanges", {})
        
        # Initialize Binance if configured
        if "binance" in exchange_configs:
            try:
                # Check for environment variables first
                api_key = os.environ.get('BINANCE_API_KEY')
                api_secret = os.environ.get('BINANCE_API_SECRET')
                
                # If environment variables exist, update config temporarily (without saving)
                if api_key and api_secret:
                    logger.info("Using Binance API keys from environment variables")
                    exchange_configs["binance"]["api_key"] = api_key
                    exchange_configs["binance"]["api_secret"] = api_secret
                
                self.exchanges["binance"] = BinanceExchange(self.config)
                if self.exchanges["binance"].is_ready():
                    logger.info("Binance exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Binance: {str(e)}")
                
        # Initialize Bybit if configured
        if "bybit" in exchange_configs:
            try:
                # Check for environment variables first
                api_key = os.environ.get('BYBIT_API_KEY')
                api_secret = os.environ.get('BYBIT_API_SECRET')
                
                # If environment variables exist, update config temporarily (without saving)
                if api_key and api_secret:
                    logger.info("Using Bybit API keys from environment variables")
                    exchange_configs["bybit"]["api_key"] = api_key
                    exchange_configs["bybit"]["api_secret"] = api_secret
                
                self.exchanges["bybit"] = BybitExchange(self.config)
                if self.exchanges["bybit"].is_ready():
                    logger.info("Bybit exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bybit: {str(e)}")
                
        if not self.exchanges:
            logger.warning("No exchanges were initialized. Check API keys in config.")
            
    def check_whale_activity(self, symbol):
        """Check if there's significant whale activity for a trading pair"""
        if not self.whale_detector:
            return False
            
        # Get token from symbol (e.g., 'BTC/USD' -> 'BTC')
        token = symbol.split('/')[0]
        
        # Get recent whale transactions for this token
        recent_txs = self.whale_detector.whale_transactions
        
        # Filter by token and last 30 minutes
        thirty_mins_ago = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        
        recent_whale_activity = recent_txs[
            (recent_txs['token'] == token) & 
            (recent_txs['timestamp'] > thirty_mins_ago)
        ]
        
        if not recent_whale_activity.empty:
            # Calculate total whale movement
            total_usd_value = recent_whale_activity['usd_value'].sum()
            
            # If significant movement detected
            if total_usd_value > 1000000:  # $1M threshold
                impact = recent_whale_activity['price_impact'].max()
                return {
                    'detected': True,
                    'impact': impact,
                    'total_value': total_usd_value,
                    'transactions': len(recent_whale_activity)
                }
                
        return {'detected': False}
        
    def adjust_risk_based_on_whale_activity(self, symbol):
        """Adjust trading risk parameters based on whale activity"""
        activity = self.check_whale_activity(symbol)
        
        if not activity['detected']:
            # No recent whale activity, normal trading
            self.risk_adjustment = 1.0
            self.trading_paused = False
            return self.risk_adjustment
            
        # Whale activity detected - apply risk tiers
        impact = activity.get('impact', 0)
        
        # Apply risk tier thresholds
        low_threshold = self.config.get("risk_tiers.low_impact_threshold", 10)
        high_threshold = self.config.get("risk_tiers.high_impact_threshold", 25)
        
        if impact >= high_threshold:
            # High impact - pause trading
            self.risk_adjustment = 0.0
            self.trading_paused = True
            pause_minutes = self.config.get("risk_tiers.trading_pause_minutes", 30)
            self.pause_until = datetime.utcnow() + timedelta(minutes=pause_minutes)
            logger.warning(f"Trading paused for {pause_minutes} minutes due to high whale impact ({impact}%)")
        elif impact >= low_threshold:
            # Medium impact - reduce trade size
            self.risk_adjustment = 0.5
            logger.info(f"Trade size reduced to 50% due to moderate whale impact ({impact}%)")
        else:
            # Low impact - slight reduction
            self.risk_adjustment = 0.8
            logger.info(f"Trade size reduced to 80% due to low whale impact ({impact}%)")
            
        return self.risk_adjustment
        
    def execute_trade(self, exchange_id, symbol, order_type, side, amount, price=None):
        """Execute a trade with risk adjustment and whale protection"""
        # Check if trading is paused
        if self.trading_paused:
            if datetime.utcnow() >= self.pause_until:
                # Resume trading
                self.trading_paused = False
                logger.info("Trading resumed after pause period")
            else:
                remaining = (self.pause_until - datetime.utcnow()).total_seconds() / 60
                logger.info(f"Trade skipped: Trading paused for {remaining:.1f} more minutes")
                return None
                
        # Adjust risk based on whale activity
        risk_adj = self.adjust_risk_based_on_whale_activity(symbol)
        
        if risk_adj <= 0:
            logger.info(f"Trade skipped: Risk adjustment is {risk_adj} due to whale activity")
            return None
            
        # Adjust trade amount based on risk
        adjusted_amount = amount * risk_adj
        
        # Check if the exchange is initialized
        if exchange_id not in self.exchanges:
            logger.error(f"Trade failed: Exchange {exchange_id} not initialized")
            return None
            
        exchange = self.exchanges[exchange_id]
        
        try:
            # Use the exchange implementation's execute_trade method
            order = exchange.execute_trade(symbol, order_type, side, adjusted_amount, price)
            
            if order:
                # Store order for tracking
                self.active_orders[order['id']] = {
                    'exchange': exchange_id,
                    'symbol': symbol,
                    'type': order_type,
                    'side': side,
                    'amount': adjusted_amount,
                    'price': price,
                    'status': order['status'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return order
        except Exception as e:
            logger.error(f"Trade failed: {str(e)}")
            return None 