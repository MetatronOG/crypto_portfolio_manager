import logging
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketState(Enum):
    NORMAL = "normal"
    CAUTION = "caution"  # 5-10% drop
    WARNING = "warning"  # 10-20% drop
    DANGER = "danger"    # 20%+ drop

class CrashProtection:
    def __init__(self):
        self.market_state = MarketState.NORMAL
        self.last_state_change = datetime.now()
        self.btc_price_history = []
        self.max_history_size = 1000
        
    def update_market_state(self, btc_price: Decimal) -> MarketState:
        """Update market state based on BTC price movement."""
        # Add price to history
        self.btc_price_history.append({
            "price": btc_price,
            "timestamp": datetime.now()
        })
        
        # Keep history size manageable
        if len(self.btc_price_history) > self.max_history_size:
            self.btc_price_history.pop(0)
            
        # Calculate price change
        if len(self.btc_price_history) < 2:
            return self.market_state
            
        price_24h_ago = self._get_price_n_hours_ago(24)
        if not price_24h_ago:
            return self.market_state
            
        price_change_pct = ((btc_price - price_24h_ago) / price_24h_ago) * 100
        
        # Determine new state
        new_state = self._determine_state(price_change_pct)
        
        # Log state change
        if new_state != self.market_state:
            logger.warning(
                f"Market state changed from {self.market_state.value} to {new_state.value} "
                f"(BTC 24h change: {price_change_pct:.2f}%)"
            )
            self.market_state = new_state
            self.last_state_change = datetime.now()
            
        return self.market_state
        
    def _get_price_n_hours_ago(self, hours: int) -> Decimal:
        """Get the price from n hours ago."""
        target_time = datetime.now() - timedelta(hours=hours)
        
        # Find the closest price point
        closest_price = None
        min_time_diff = timedelta(hours=24)  # Initialize with max difference
        
        for price_point in self.btc_price_history:
            time_diff = abs(price_point["timestamp"] - target_time)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_price = price_point["price"]
                
        return closest_price
        
    def _determine_state(self, price_change_pct: Decimal) -> MarketState:
        """Determine market state based on price change percentage."""
        if price_change_pct <= -20:
            return MarketState.DANGER
        elif price_change_pct <= -10:
            return MarketState.WARNING
        elif price_change_pct <= -5:
            return MarketState.CAUTION
        else:
            return MarketState.NORMAL
            
    def should_reduce_exposure(self) -> bool:
        """Determine if trading exposure should be reduced."""
        return self.market_state in [MarketState.WARNING, MarketState.DANGER]
        
    def should_stop_trading(self) -> bool:
        """Determine if trading should be stopped."""
        return self.market_state == MarketState.DANGER
        
    def get_risk_adjustment(self) -> Decimal:
        """Get risk adjustment factor based on market state."""
        if self.market_state == MarketState.DANGER:
            return Decimal("0.0")  # No new trades
        elif self.market_state == MarketState.WARNING:
            return Decimal("0.5")  # 50% size
        elif self.market_state == MarketState.CAUTION:
            return Decimal("0.8")  # 80% size
        else:
            return Decimal("1.0")  # Normal size

    def get_trading_rules(self) -> Dict:
        """Get current trading rules based on market state."""
        return self.trading_rules[self.market_state]

    def should_convert_to_stablecoin(self, 
                                   symbol: str, 
                                   category: str, 
                                   unrealized_profit: Decimal) -> bool:
        """Determine if a position should be converted to stablecoin."""
        if category == "iso20022":
            return False  # Never convert ISO20022 coins
            
        if category == "meme":
            # Convert meme coins based on market state and profit
            if self.market_state == MarketState.DANGER:
                return True  # Convert all meme coins in danger state
            elif self.market_state == MarketState.WARNING:
                return unrealized_profit > 0  # Convert if in profit
            elif self.market_state == MarketState.CAUTION:
                return unrealized_profit >= Decimal("10.0")  # Convert if 10%+ profit
                
        return False

    def get_stop_loss_price(self, 
                           entry_price: Decimal, 
                           category: str) -> Optional[Decimal]:
        """Calculate stop loss price based on market conditions."""
        if category == "iso20022":
            return None  # No stop loss for ISO20022 coins
            
        multiplier = self.trading_rules[self.market_state]["stop_loss_multiplier"]
        return entry_price * multiplier

    def can_open_position(self, 
                         symbol: str, 
                         category: str, 
                         position_size: Decimal) -> bool:
        """Check if a new position can be opened."""
        rules = self.trading_rules[self.market_state]
        
        if category == "meme" and not rules["meme_trading"]:
            return False
            
        max_position = position_size * rules["position_size"]
        return max_position > 0

    def reset_reference_price(self, price: Decimal):
        """Reset the BTC reference price."""
        self.btc_reference_price = price
        self.market_state = MarketState.NORMAL
        self.last_state_change = datetime.now()
        logger.info(f"Reset BTC reference price to {price}") 