#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import time
from datetime import datetime, timedelta

# Add src directory to path for imports
src_path = str(Path(__file__).parent)
sys.path.append(src_path)

# Fix for ccxt module not found
import site
site_packages = site.getsitepackages()
for site_package in site_packages:
    sys.path.append(site_package)

# Now import directly from local paths
from whale_tracker.config import Config
from whale_tracker.wallet_manager import WalletManager
from whale_tracker.whale_detector import WhaleDetector
# Import directly from local file
from trading_bot.trade_executor import TradeExecutor

def simulate_whale_transaction(whale_detector, impact_level="medium"):
    """Simulate a whale transaction with different impact levels"""
    
    # Define impact levels and corresponding values
    impact_values = {
        "low": {"amount": 105.0, "impact": 5.0},       # Just above threshold, low impact
        "medium": {"amount": 250.0, "impact": 15.0},   # Medium sized transaction, medium impact
        "high": {"amount": 500.0, "impact": 30.0}      # Large transaction, high impact
    }
    
    impact = impact_values.get(impact_level, impact_values["medium"])
    
    # Create a test transaction
    test_tx = {
        'blockchain': 'ethereum',
        'from_address': '0xBE0eB53F46cd790Cd13851d5Eff43D12404d33E8',  # Binance 7
        'to_address': '0x40B38765696e3d5d8d9d834d8aad4bb6e418e489',  # Robinhood
        'token': 'ETH',
        'amount': impact["amount"],
        'usd_value': impact["amount"] * 3500,  # Using approximate ETH price of $3500
        'type': 'transfer',
        'price_impact': impact["impact"],
        'tx_hash': '0x' + 'test' + impact_level + str(int(time.time())),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Process the whale transaction
    whale_detector.process_whale_transaction(test_tx['blockchain'], test_tx)
    print(f"Simulated {impact_level} impact whale transaction: {test_tx['amount']} ETH with {test_tx['price_impact']}% price impact")
    return test_tx

def main():
    # Initialize config
    config = Config()
    
    # Initialize wallet manager
    wallet_manager = WalletManager(config)
    
    # Initialize whale detector
    whale_detector = WhaleDetector(config, wallet_manager)
    
    # Initialize trade executor
    trade_executor = TradeExecutor(config, whale_detector)
    
    print("Testing trading risk adjustment based on whale activity...\n")
    
    # Test case 1: No whale activity (normal trading)
    print("Test Case 1: No whale activity")
    risk_adj = trade_executor.adjust_risk_based_on_whale_activity("ETH/USD")
    print(f"Risk adjustment: {risk_adj:.2f} (Expected: 1.00 - normal trading)\n")
    
    # Test case 2: Low impact whale activity
    print("Test Case 2: Low impact whale activity")
    simulate_whale_transaction(whale_detector, "low")
    risk_adj = trade_executor.adjust_risk_based_on_whale_activity("ETH/USD")
    print(f"Risk adjustment: {risk_adj:.2f} (Expected: 0.80 - slightly reduced position size)\n")
    
    # Test case 3: Medium impact whale activity
    print("Test Case 3: Medium impact whale activity")
    simulate_whale_transaction(whale_detector, "medium")
    risk_adj = trade_executor.adjust_risk_based_on_whale_activity("ETH/USD")
    print(f"Risk adjustment: {risk_adj:.2f} (Expected: 0.50 - halved position size)\n")
    
    # Test case 4: High impact whale activity
    print("Test Case 4: High impact whale activity")
    simulate_whale_transaction(whale_detector, "high")
    risk_adj = trade_executor.adjust_risk_based_on_whale_activity("ETH/USD")
    print(f"Risk adjustment: {risk_adj:.2f} (Expected: 0.00 - trading paused)\n")
    
    # Test case 5: Attempt to execute trade during high-impact pause
    print("Test Case 5: Attempting to execute trade during high-impact pause")
    trade_result = trade_executor.execute_trade("binance", "ETH/USD", "market", "buy", 1.0)
    print(f"Trade execution result: {trade_result} (Expected: None - trade should be skipped)\n")
    
    print("Test complete!")

if __name__ == "__main__":
    main() 