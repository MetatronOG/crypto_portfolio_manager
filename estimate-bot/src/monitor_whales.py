#!/usr/bin/env python3

"""
Simple Whale Monitoring Script - No Trading Functionality
This script just monitors whale transactions without the trading functionality that depends on ccxt.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("whale_monitoring.log")
    ]
)
logger = logging.getLogger("whale_monitor")

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from whale_tracker.config import Config
from whale_tracker.wallet_manager import WalletManager
from whale_tracker.whale_detector import WhaleDetector

def main():
    """Run the whale monitoring functionality"""
    logger.info("Starting Whale Monitor")
    
    # Initialize config
    config = Config()
    
    # Initialize wallet manager
    wallet_manager = WalletManager(config)
    logger.info(f"Loaded {len(wallet_manager.wallets)} wallet addresses")
    
    # Initialize whale detector
    whale_detector = WhaleDetector(config, wallet_manager)
    
    # Start monitoring in a separate thread
    if whale_detector.start_monitoring():
        logger.info("Whale monitoring started successfully")
        
        try:
            # Keep the main thread running
            logger.info("Press Ctrl+C to stop monitoring")
            while True:
                # Wait for 10 seconds, then check for any recent transactions
                time.sleep(10)
                
                # Display recent transactions (if any)
                if not whale_detector.whale_transactions.empty:
                    recent = whale_detector.whale_transactions.tail(1)
                    if not recent.empty:
                        latest = recent.iloc[0]
                        age = time.time() - time.mktime(time.strptime(latest['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                        # Only show if detected in the last minute
                        if age < 60:
                            logger.info(f"Recent whale: {latest['amount']} {latest['token']} {latest['type']} worth ${latest['usd_value']:,.2f}")
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected, shutting down...")
        finally:
            # Stop monitoring
            whale_detector.stop_monitoring()
            logger.info("Whale monitoring stopped")
    else:
        logger.error("Failed to start whale monitoring")

if __name__ == "__main__":
    main() 