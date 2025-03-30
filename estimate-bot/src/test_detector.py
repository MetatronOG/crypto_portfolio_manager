#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import time

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from whale_tracker.config import Config
from whale_tracker.wallet_manager import WalletManager
from whale_tracker.whale_detector import WhaleDetector
from whale_tracker.whale_alerts import trigger_alert

def main():
    # Initialize config
    config = Config()
    
    # Initialize wallet manager
    wallet_manager = WalletManager(config)
    
    # Initialize whale detector (but don't start monitoring)
    whale_detector = WhaleDetector(config, wallet_manager)
    
    # Simulate a whale transaction
    print("Simulating a whale transaction...")
    
    # Create a test transaction
    test_tx = {
        'blockchain': 'ethereum',
        'from_address': '0xBE0eB53F46cd790Cd13851d5Eff43D12404d33E8',  # Binance 7
        'to_address': '0x40B38765696e3d5d8d9d834d8aad4bb6e418e489',  # Robinhood
        'token': 'ETH',
        'amount': 150.0,  # Above the 100 ETH threshold
        'usd_value': 150.0 * 3500,  # Using approximate ETH price of $3500
        'type': 'transfer',
        'price_impact': 0.5,
        'tx_hash': '0x' + 'test123456789' * 4,
        'timestamp': whale_detector.whale_transactions['timestamp'].iloc[0] if not whale_detector.whale_transactions.empty else None
    }
    
    # Process the whale transaction
    if test_tx['timestamp'] is None:
        import datetime
        test_tx['timestamp'] = datetime.datetime.utcnow().isoformat()
        
    whale_detector.process_whale_transaction(test_tx['blockchain'], test_tx)
    
    # Print the last transaction in the database
    if not whale_detector.whale_transactions.empty:
        print("\nStored transaction:")
        last_tx = whale_detector.whale_transactions.iloc[-1].to_dict()
        for key, value in last_tx.items():
            print(f"  {key}: {value}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main() 