"""
Base exchange class that defines common methods and interfaces.
"""
import ccxt
import logging
from abc import ABC, abstractmethod

class BaseExchange(ABC):
    """Base exchange class for implementing exchange-specific functionality."""
    
    def __init__(self, config, exchange_id):
        """
        Initialize the exchange interface.
        
        Args:
            config: Configuration object
            exchange_id: The exchange identifier (e.g., 'binance', 'bybit')
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.exchange_id = exchange_id
        self.exchange = None
        self.is_initialized = False
        
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize the exchange connection using API keys from config."""
        try:
            # Get exchange config from main config
            exchange_configs = self.config.get('exchanges', {})
            if self.exchange_id not in exchange_configs:
                self.logger.error(f"Exchange {self.exchange_id} not found in config")
                return
            
            exchange_config = exchange_configs[self.exchange_id]
            
            # Check if API keys are provided
            if 'api_key' not in exchange_config or 'api_secret' not in exchange_config:
                self.logger.error(f"API keys for {self.exchange_id} not found in config")
                return
            
            # Initialize the CCXT exchange instance
            exchange_class = getattr(ccxt, self.exchange_id)
            self.exchange = exchange_class({
                'apiKey': exchange_config['api_key'],
                'secret': exchange_config['api_secret'],
                'enableRateLimit': True,
                'options': exchange_config.get('options', {})
            })
            
            self.is_initialized = True
            self.logger.info(f"{self.exchange_id.capitalize()} exchange initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.exchange_id} exchange: {str(e)}")
    
    def is_ready(self):
        """Check if exchange is initialized and ready for trading."""
        return self.is_initialized and self.exchange is not None
    
    def get_balance(self, currency=None):
        """
        Get account balance for a specific currency or all currencies.
        
        Args:
            currency: Currency symbol (e.g., 'BTC'). If None, returns all balances.
            
        Returns:
            Balance dict or specific currency balance
        """
        if not self.is_ready():
            self.logger.error(f"{self.exchange_id} exchange not initialized")
            return None
        
        try:
            balance = self.exchange.fetch_balance()
            if currency:
                return balance.get(currency, {'free': 0, 'used': 0, 'total': 0})
            return balance
        except Exception as e:
            self.logger.error(f"Failed to fetch balance from {self.exchange_id}: {str(e)}")
            return None
    
    def get_ticker(self, symbol):
        """
        Get current ticker price for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Ticker information dict
        """
        if not self.is_ready():
            self.logger.error(f"{self.exchange_id} exchange not initialized")
            return None
        
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            self.logger.error(f"Failed to fetch ticker for {symbol} from {self.exchange_id}: {str(e)}")
            return None
    
    @abstractmethod
    def execute_trade(self, symbol, order_type, side, amount, price=None):
        """
        Execute a trade on the exchange.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            order_type: Order type ('market', 'limit', etc.)
            side: Order side ('buy' or 'sell')
            amount: Order amount
            price: Order price (required for limit orders)
            
        Returns:
            Order result dict or None if failed
        """
        pass 