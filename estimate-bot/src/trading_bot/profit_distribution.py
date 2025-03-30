from enum import Enum
import logging
from typing import Dict, List, Optional
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinCategory(Enum):
    ISO20022 = "iso20022"
    MEME = "meme"
    STABLECOIN = "stablecoin"

class ISO20022Coins:
    SYMBOLS = {
        "XRP", "XLM", "HBAR", "ALGO", "QNT", 
        "IOTA", "XDC", "XRPL", "QUANT"
    }

class ProfitDistributor:
    def __init__(self):
        self.iso20022_coins = {
            "XRP", "XLM", "HBAR", "ALGO", "QNT", "IOTA", "XDC"
        }
        self.meme_coins = {
            "DOGE", "SHIB", "PEPE", "FLOKI"
        }
        self.stablecoins = {
            "USDT", "USDC", "BUSD", "DAI"
        }
        
        # Profit taking thresholds for meme coins
        self.profit_thresholds = {
            "2x": Decimal("2.0"),
            "3x": Decimal("3.0"),
            "5x": Decimal("5.0")
        }
        
        # DCA settings for ISO20022 coins
        self.dca_settings = {
            "min_dip_percentage": Decimal("5.0"),
            "allocation_percentage": Decimal("20.0"),
            "max_single_buy": Decimal("1000.0")
        }

    def categorize_coin(self, symbol: str) -> CoinCategory:
        """Categorize a coin based on its symbol."""
        base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        
        if base_symbol in self.iso20022_coins:
            return CoinCategory.ISO20022
        elif base_symbol in self.meme_coins:
            return CoinCategory.MEME
        elif base_symbol in self.stablecoins:
            return CoinCategory.STABLECOIN
        else:
            # Default to treating unknown coins as meme coins
            return CoinCategory.MEME

    def should_take_profit_meme(self, symbol: str, current_price: Decimal, 
                              entry_price: Decimal) -> Optional[Decimal]:
        """Determine if profit should be taken on a meme coin position."""
        if self.categorize_coin(symbol) != CoinCategory.MEME:
            return None

        profit_multiple = current_price / entry_price
        
        # Check profit thresholds in descending order
        for threshold, multiple in sorted(self.profit_thresholds.items(), 
                                       key=lambda x: x[1], reverse=True):
            if profit_multiple >= multiple:
                logger.info(f"Taking profit on {symbol} at {threshold} ({profit_multiple}x)")
                return Decimal("0.5")  # Sell 50% of position
                
        return None

    def should_dca_iso20022(
        self,
        symbol: str,
        current_price: Decimal,
        peak_price: Decimal
    ) -> Optional[Decimal]:
        """Determine if and how much to DCA into an ISO20022 coin."""
        if self.categorize_coin(symbol) != CoinCategory.ISO20022:
            return None
            
        # Calculate price drop percentage
        price_drop = ((peak_price - current_price) / peak_price) * 100
        
        # DCA strategy based on price drop
        if price_drop >= 20:
            return Decimal("100")  # Large dip - buy more
        elif price_drop >= 10:
            return Decimal("50")   # Medium dip
        elif price_drop >= 5:
            return Decimal("25")   # Small dip
            
        return None  # No DCA needed

    def distribute_profits(
        self,
        profit_amount: Decimal,
        distribution_config: Dict[str, str]
    ) -> Dict[CoinCategory, Decimal]:
        """Distribute profits according to configuration."""
        distribution = {}
        
        for category in CoinCategory:
            percentage = Decimal(distribution_config.get(category.value, "0"))
            amount = (profit_amount * percentage) / Decimal("100")
            distribution[category] = amount
            
        return distribution

    def should_take_meme_profits(
        self,
        symbol: str,
        entry_price: Decimal,
        current_price: Decimal
    ) -> bool:
        """Determine if profits should be taken on a meme coin position."""
        if self.categorize_coin(symbol) != CoinCategory.MEME:
            return False
            
        profit_percentage = ((current_price - entry_price) / entry_price) * 100
        
        # Take profits at different multiples
        if profit_percentage >= 400:  # 5x
            return True
        elif profit_percentage >= 200:  # 3x
            return True
        elif profit_percentage >= 100:  # 2x
            return True
            
        return False

    def update_holdings(self, symbol: str, amount: Decimal):
        """Update holdings for a given coin."""
        category = self.categorize_coin(symbol)
        
        if category == CoinCategory.ISO20022:
            self.iso20022_coins.add(symbol)
        elif category == CoinCategory.MEME:
            self.meme_coins.add(symbol)
        elif category == CoinCategory.STABLECOIN:
            self.stablecoins.add(symbol)

    def get_total_value(self, prices: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Calculate total value of holdings by category."""
        totals = {
            "iso20022": Decimal("0"),
            "meme": Decimal("0"),
            "stablecoin": Decimal("0")
        }
        
        for symbol in self.iso20022_coins:
            if symbol in prices:
                totals["iso20022"] += prices[symbol]
                
        for symbol in self.meme_coins:
            if symbol in prices:
                totals["meme"] += prices[symbol]
                
        for symbol in self.stablecoins:
            totals["stablecoin"] += prices[symbol]
            
        return totals 