#!/usr/bin/env python3

"""
Whale Tracker and Trading Bot - Entry Point Script
Run this script to start the bot with various options
"""

import sys
import os
from pathlib import Path
import argparse

# Add src directory to path
SRC_DIR = Path(__file__).resolve().parent / 'src'
sys.path.append(str(SRC_DIR))

def run_main():
    """Run the main bot script with the provided arguments"""
    sys.argv.pop(0)  # Remove this script's name
    from src.main import main
    main()

def run_test_import():
    """Run the wallet import test"""
    from src.test_import import main
    main()

def run_test_detector():
    """Run the whale detector test"""
    from src.test_detector import main
    main()

def run_test_trading():
    """Run the trading risk adjustment test"""
    from src.test_trading import main
    main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whale Tracker and Trading Bot")
    parser.add_argument("--mode", choices=["bot", "test-import", "test-detector", "test-trading"], 
                        default="bot", help="Operation mode")
    
    args, remaining = parser.parse_known_args()
    
    # Replace sys.argv with remaining args for the next parser
    sys.argv = [sys.argv[0]] + remaining
    
    if args.mode == "bot":
        run_main()
    elif args.mode == "test-import":
        run_test_import()
    elif args.mode == "test-detector":
        run_test_detector()
    elif args.mode == "test-trading":
        run_test_trading()
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1) 