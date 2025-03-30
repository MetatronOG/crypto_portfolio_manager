#!/usr/bin/env python3
"""
Setup script for Whale Tracker and Trading Bot

This script helps with:
1. Installing required dependencies
2. Creating necessary directories
3. Setting up initial configuration
4. Testing connections to APIs and exchanges
"""
import os
import sys
import json
import argparse
import subprocess
import site
from pathlib import Path

# Fix for ccxt import issue
sys.path.extend(site.getsitepackages())

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print_header("Installing Dependencies")
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies:")
        print(e.stderr)
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")
    
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Created logs directory: {logs_dir}")
    
    return True

def setup_config():
    """Setup the initial configuration"""
    print_header("Setting Up Configuration")
    config_path = Path(__file__).parent / "config.json"
    
    if config_path.exists():
        print(f"📄 Config file already exists at {config_path}")
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        print(f"📄 Creating new config file at {config_path}")
        # Import Config class to create default config
        sys.path.append(str(Path(__file__).parent))
        from src.whale_tracker.config import Config
        config_obj = Config(config_path)
        config = config_obj.config
    
    # Now we can optionally collect user input for API keys, etc.
    # For this example, we'll just save the config as is
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✅ Configuration file setup complete!")
    return True

def setup_sample_data():
    """Create sample data files if they don't exist"""
    print_header("Setting Up Sample Data")
    wallets_path = Path(__file__).parent / "data" / "wallets.csv"
    
    if not wallets_path.exists():
        # Create sample wallets.csv
        with open(wallets_path, 'w') as f:
            f.write("address,name,category,blockchain\n")
            f.write("0xBE0eB53F46cd790Cd13851d5Eff43D12404d33E8,Binance 7,exchange,ethereum\n")
            f.write("0x28C6c06298d514Db089934071355E5743bf21d60,Binance 8,exchange,ethereum\n")
            f.write("0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549,Binance Cold Wallet,exchange,ethereum\n")
            f.write("0xdAC17F958D2ee523a2206206994597C13D831ec7,USDT Treasury,token,ethereum\n")
            f.write("0x5754284f345afc66a98fbB0a0Afe71e0F007B949,Kraken,exchange,ethereum\n")
            f.write("0x2FAF487A4414Fe77e2327F0bf4AE2a264a776AD2,FTX,exchange,ethereum\n")
            f.write("0x40B38765696e3d5d8d9d834d8aad4bb6e418e489,Robinhood,exchange,ethereum\n")
        print(f"✅ Created sample wallets data: {wallets_path}")
    else:
        print(f"📄 Wallets data already exists: {wallets_path}")
    
    # Create empty whale_transactions.csv if it doesn't exist
    tx_path = Path(__file__).parent / "data" / "whale_transactions.csv"
    if not tx_path.exists():
        with open(tx_path, 'w') as f:
            f.write("timestamp,blockchain,from_address,to_address,token,amount,usd_value,type,price_impact,tx_hash\n")
        print(f"✅ Created empty transactions log: {tx_path}")
    else:
        print(f"📄 Transactions log already exists: {tx_path}")
    
    return True

def test_connections():
    """Test connections to APIs and exchanges"""
    print_header("Testing Connections")
    
    # We'll import modules here to test their functionality
    try:
        try:
            import ccxt
        except ImportError:
            print("CCXT module not found. Installing it now...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "ccxt"],
                check=True,
                capture_output=True,
                text=True
            )
            import ccxt
            
        print("✅ CCXT module loaded successfully")
        
        # Test connection to a public API (no API key needed)
        binance = ccxt.binance()
        ticker = binance.fetch_ticker('BTC/USDT')
        print(f"✅ Connected to Binance: BTC/USDT price = ${ticker['last']:.2f}")
    except ImportError as e:
        print(f"❌ Failed to import CCXT module: {str(e)}")
        print(f"Module search paths: {sys.path}")
    except Exception as e:
        print(f"❌ Error connecting to exchange: {str(e)}")
    
    # You could add more tests here for other APIs
    
    return True

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup Whale Tracker and Trading Bot")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-config", action="store_true", help="Skip configuration setup")
    parser.add_argument("--skip-data", action="store_true", help="Skip sample data creation")
    parser.add_argument("--skip-tests", action="store_true", help="Skip connection tests")
    args = parser.parse_args()
    
    print_header("Whale Tracker and Trading Bot Setup")
    
    # Create directories first
    create_directories()
    
    # Install dependencies if not skipped
    if not args.skip_deps:
        install_dependencies()
    else:
        print("Skipping dependency installation...")
    
    # Setup configuration if not skipped
    if not args.skip_config:
        setup_config()
    else:
        print("Skipping configuration setup...")
    
    # Setup sample data if not skipped
    if not args.skip_data:
        setup_sample_data()
    else:
        print("Skipping sample data creation...")
    
    # Test connections if not skipped
    if not args.skip_tests:
        test_connections()
    else:
        print("Skipping connection tests...")
    
    print_header("Setup Complete!")
    print("You can now run the bot with:")
    print("  python monitor.py             # For whale monitoring only")
    print("  python run_bot.py --mode bot  # For full bot functionality")
    
if __name__ == "__main__":
    main() 