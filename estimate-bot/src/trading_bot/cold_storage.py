import logging
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Transfer:
    asset: str
    amount: Decimal
    from_address: str
    to_address: str
    timestamp: datetime
    status: TransferStatus
    tx_hash: Optional[str] = None
    error: Optional[str] = None

class ColdStorage:
    def __init__(self, config_path: str = "config/cold_storage.json"):
        self.config_path = config_path
        self.transfers: List[Transfer] = []
        self.wallets: Dict[str, str] = {}
        self.load_config()

    def load_config(self):
        """Load cold storage wallet configurations."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.wallets = config.get("wallets", {})
            else:
                logger.warning(f"Cold storage config not found at {self.config_path}")
                self.wallets = {}
        except Exception as e:
            logger.error(f"Error loading cold storage config: {e}")
            self.wallets = {}

    def get_cold_wallet(self, asset: str) -> Optional[str]:
        """Get cold wallet address for a specific asset."""
        return self.wallets.get(asset.upper())

    def initiate_transfer(self, 
                         asset: str, 
                         amount: Decimal, 
                         from_address: str) -> Optional[Transfer]:
        """Initiate a transfer to cold storage."""
        try:
            to_address = self.get_cold_wallet(asset)
            if not to_address:
                raise ValueError(f"No cold wallet configured for {asset}")

            transfer = Transfer(
                asset=asset,
                amount=amount,
                from_address=from_address,
                to_address=to_address,
                timestamp=datetime.now(),
                status=TransferStatus.PENDING
            )
            
            # Add to pending transfers
            self.transfers.append(transfer)
            logger.info(
                f"Initiated transfer of {amount} {asset} "
                f"to cold storage: {to_address[:8]}..."
            )
            
            return transfer
            
        except Exception as e:
            logger.error(f"Error initiating cold storage transfer: {e}")
            return None

    def update_transfer_status(self, 
                             transfer: Transfer, 
                             status: TransferStatus, 
                             tx_hash: Optional[str] = None,
                             error: Optional[str] = None):
        """Update the status of a transfer."""
        transfer.status = status
        transfer.tx_hash = tx_hash
        transfer.error = error
        
        if status == TransferStatus.COMPLETED:
            logger.info(
                f"Completed transfer of {transfer.amount} {transfer.asset} "
                f"to cold storage. TX: {tx_hash[:8]}..."
            )
        elif status == TransferStatus.FAILED:
            logger.error(
                f"Failed transfer of {transfer.amount} {transfer.asset} "
                f"to cold storage: {error}"
            )

    def get_pending_transfers(self) -> List[Transfer]:
        """Get list of pending transfers."""
        return [t for t in self.transfers if t.status == TransferStatus.PENDING]

    def get_recent_transfers(self, limit: int = 10) -> List[Transfer]:
        """Get recent transfers, sorted by timestamp."""
        return sorted(
            self.transfers,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

    def get_cold_storage_balances(self) -> Dict[str, Decimal]:
        """Get balances in cold storage wallets."""
        # This is a placeholder - in production, this would query blockchain APIs
        balances = {}
        for asset, wallet in self.wallets.items():
            # Mock balance calculation based on completed transfers
            balance = sum(
                t.amount for t in self.transfers
                if t.status == TransferStatus.COMPLETED and 
                t.to_address == wallet
            )
            balances[asset] = balance
            
        return balances

    def should_transfer_to_cold_storage(self, 
                                      asset: str, 
                                      amount: Decimal, 
                                      threshold: Decimal) -> bool:
        """Determine if an amount should be transferred to cold storage."""
        if amount <= threshold:
            return False
            
        # Check if we have too many pending transfers
        pending = len(self.get_pending_transfers())
        if pending >= 5:  # Maximum pending transfers
            return False
            
        # Check if we have a cold wallet for this asset
        if not self.get_cold_wallet(asset):
            return False
            
        return True

    def calculate_transfer_amount(self, 
                                available: Decimal, 
                                threshold: Decimal) -> Decimal:
        """Calculate how much should be transferred to cold storage."""
        if available <= threshold:
            return Decimal("0")
            
        # Keep some buffer in hot wallet
        buffer = threshold * Decimal("1.5")
        transfer_amount = available - buffer
        
        if transfer_amount <= 0:
            return Decimal("0")
            
        return transfer_amount

    def export_transfer_history(self, filepath: str):
        """Export transfer history to a file."""
        try:
            history = [
                {
                    "asset": t.asset,
                    "amount": str(t.amount),
                    "from_address": t.from_address,
                    "to_address": t.to_address,
                    "timestamp": t.timestamp.isoformat(),
                    "status": t.status.value,
                    "tx_hash": t.tx_hash,
                    "error": t.error
                }
                for t in self.transfers
            ]
            
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2)
                
            logger.info(f"Exported transfer history to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting transfer history: {e}")

    def import_transfer_history(self, filepath: str):
        """Import transfer history from a file."""
        try:
            with open(filepath, 'r') as f:
                history = json.load(f)
                
            self.transfers = [
                Transfer(
                    asset=t["asset"],
                    amount=Decimal(t["amount"]),
                    from_address=t["from_address"],
                    to_address=t["to_address"],
                    timestamp=datetime.fromisoformat(t["timestamp"]),
                    status=TransferStatus(t["status"]),
                    tx_hash=t.get("tx_hash"),
                    error=t.get("error")
                )
                for t in history
            ]
            
            logger.info(f"Imported transfer history from {filepath}")
            
        except Exception as e:
            logger.error(f"Error importing transfer history: {e}")

    def should_transfer_to_cold_storage(
        self,
        symbol: str,
        amount: Decimal,
        threshold: Decimal
    ) -> bool:
        """Determine if funds should be moved to cold storage."""
        # Don't transfer if we have too many pending transfers
        if len(self.get_pending_transfers()) >= 3:
            return False
            
        # Check if amount exceeds threshold
        return amount > threshold
        
    def calculate_transfer_amount(
        self,
        total_amount: Decimal,
        threshold: Decimal
    ) -> Decimal:
        """Calculate how much should be transferred to cold storage."""
        # Keep threshold amount in hot wallet
        excess = total_amount - threshold
        
        if excess <= 0:
            return Decimal("0")
            
        # Transfer 80% of excess to cold storage
        return (excess * Decimal("0.8")).quantize(Decimal("0.00000001"))
        
    def initiate_transfer(
        self,
        symbol: str,
        amount: Decimal,
        from_address: str,
        to_address: Optional[str] = None
    ) -> Dict:
        """Initiate a transfer to cold storage."""
        transfer = {
            "id": len(self.get_pending_transfers()) + len(self.transfers),
            "symbol": symbol,
            "amount": amount,
            "from_address": from_address,
            "to_address": to_address,
            "status": TransferStatus.PENDING,
            "timestamp": datetime.now().isoformat(),
            "retry_count": 0,
            "tx_hash": None,
            "error": None
        }
        
        self.transfers.append(Transfer(
            asset=symbol,
            amount=amount,
            from_address=from_address,
            to_address=to_address,
            timestamp=datetime.now(),
            status=TransferStatus.PENDING
        ))
        logger.info(
            f"Initiated cold storage transfer: {amount} {symbol} "
            f"from {from_address[:8]}..."
        )
        
        return transfer
        
    def update_transfer_status(
        self,
        transfer: Dict,
        new_status: TransferStatus,
        tx_hash: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update the status of a transfer."""
        transfer["status"] = new_status
        transfer["tx_hash"] = tx_hash
        transfer["error"] = error
        
        if new_status == TransferStatus.COMPLETED:
            self.transfers = [t for t in self.transfers if t.asset != transfer["symbol"]]
            logger.info(
                f"Transfer completed: {transfer['amount']} {transfer['symbol']} "
                f"(TX: {tx_hash[:8]}...)"
            )
        elif new_status == TransferStatus.FAILED:
            if transfer["retry_count"] < 3:
                transfer["retry_count"] += 1
                transfer["status"] = TransferStatus.PENDING
                logger.warning(
                    f"Transfer failed, retrying ({transfer['retry_count']}/3): "
                    f"{error}"
                )
            else:
                self.transfers = [t for t in self.transfers if t.asset != transfer["symbol"]]
                logger.error(
                    f"Transfer failed permanently: {transfer['amount']} "
                    f"{transfer['symbol']} - {error}"
                )
                
    def get_pending_transfers(self) -> List[Dict]:
        """Get list of pending transfers."""
        return [t.__dict__ for t in self.get_pending_transfers()]
        
    def get_transfer_history(self) -> List[Dict]:
        """Get complete transfer history."""
        return [t.__dict__ for t in self.transfers] 