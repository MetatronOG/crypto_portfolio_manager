"""
Binance exchange implementation.
"""
import logging
from .base_exchange import BaseExchange

class BinanceExchange(BaseExchange):
    """Binance exchange implementation."""
    
    def __init__(self, config):
        """
        Initialize the Binance exchange interface.
        
        Args:
            config: Configuration object
        """
        super().__init__(config, 'binance')
        self.logger = logging.getLogger(__name__)
    
    def execute_trade(self, symbol, order_type, side, amount, price=None):
        """
        Execute a trade on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            order_type: Order type ('market', 'limit', etc.)
            side: Order side ('buy' or 'sell')
            amount: Order amount
            price: Order price (required for limit orders)
            
        Returns:
            Order result dict or None if failed
        """
        if not self.is_ready():
            self.logger.error("Binance exchange not initialized")
            return None
            
        # Validate inputs
        if order_type not in ['market', 'limit']:
            self.logger.error(f"Unsupported order type: {order_type}")
            return None
            
        if side not in ['buy', 'sell']:
            self.logger.error(f"Invalid order side: {side}")
            return None
            
        if order_type == 'limit' and price is None:
            self.logger.error("Price is required for limit orders")
            return None
            
        try:
            # Create order parameters
            params = {}
            
            if order_type == 'market':
                # Execute market order
                result = self.exchange.create_order(
                    symbol=symbol,
                    type=order_type,
                    side=side,
                    amount=amount,
                    params=params
                )
            else:
                # Execute limit order
                result = self.exchange.create_order(
                    symbol=symbol,
                    type=order_type,
                    side=side,
                    amount=amount,
                    price=price,
                    params=params
                )
                
            self.logger.info(f"Order executed on Binance: {order_type} {side} {amount} {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute {side} order on Binance: {str(e)}")
            return None
            
    def get_order_status(self, order_id, symbol):
        """
        Get the status of an order on Binance.
        
        Args:
            order_id: Order ID
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Order status dict or None if failed
        """
        if not self.is_ready():
            self.logger.error("Binance exchange not initialized")
            return None
            
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            self.logger.error(f"Failed to fetch order status from Binance: {str(e)}")
            return None
            
    def cancel_order(self, order_id, symbol):
        """
        Cancel an order on Binance.
        
        Args:
            order_id: Order ID
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Cancellation result dict or None if failed
        """
        if not self.is_ready():
            self.logger.error("Binance exchange not initialized")
            return None
            
        try:
            return self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            self.logger.error(f"Failed to cancel order on Binance: {str(e)}")
            return None 