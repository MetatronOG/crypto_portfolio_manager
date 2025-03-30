import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self, wallet_file: str = "data/wallets.json"):
        self.wallet_file = wallet_file
        self.wallets: Dict[str, Dict] = {}
        self.load_wallets()
        
    def load_wallets(self):
        """Load known whale wallets from file."""
        try:
            with open(self.wallet_file, 'r') as f:
                self.wallets = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Wallet file not found: {self.wallet_file}")
            self.wallets = {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in wallet file: {self.wallet_file}")
            self.wallets = {}
            
    def save_wallets(self):
        """Save whale wallets to file."""
        try:
            with open(self.wallet_file, 'w') as f:
                json.dump(self.wallets, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving wallets: {e}")
            
    def add_wallet(self, address: str, chain: str, label: Optional[str] = None):
        """Add a new whale wallet to track."""
        if address not in self.wallets:
            self.wallets[address] = {
                "chain": chain,
                "label": label or "Unknown Whale",
                "first_seen": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "total_transactions": 0,
                "total_volume": 0
            }
            self.save_wallets()
            
    def update_wallet_activity(self, address: str, transaction_value: float):
        """Update wallet activity with new transaction."""
        if address in self.wallets:
            self.wallets[address]["last_active"] = datetime.now().isoformat()
            self.wallets[address]["total_transactions"] += 1
            self.wallets[address]["total_volume"] += transaction_value
            self.save_wallets()
            
    def get_active_whales(self, hours: int = 24) -> List[str]:
        """Get list of whale wallets active in the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        active_whales = []
        
        for address, data in self.wallets.items():
            last_active = datetime.fromisoformat(data["last_active"])
            if last_active > cutoff:
                active_whales.append(address)
                
        return active_whales
        
    def get_wallet_info(self, address: str) -> Optional[Dict]:
        """Get information about a specific wallet."""
        return self.wallets.get(address)
        
    def is_known_whale(self, address: str) -> bool:
        """Check if an address belongs to a known whale."""
        return address in self.wallets 