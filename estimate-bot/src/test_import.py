#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from whale_tracker.config import Config
from whale_tracker.wallet_manager import WalletManager

def main():
    # Initialize config
    config = Config()
    
    # Initialize wallet manager
    wallet_manager = WalletManager(config)
    
    # Print current wallets
    print(f"Current wallets: {len(wallet_manager.wallets)}")
    for address, info in list(wallet_manager.wallets.items())[:3]:  # Print first 3 for brevity
        print(f"  {address}: {info['label']} ({info['category']})")
        
    print("\nTest complete!")

if __name__ == "__main__":
    main() 