#!/usr/bin/env python3

"""
Whale Monitoring Entry Point
"""

import sys
import os
from pathlib import Path

# Add src directory to path
SRC_DIR = Path(__file__).resolve().parent / 'src'
sys.path.append(str(SRC_DIR))

if __name__ == "__main__":
    from src.monitor_whales import main
    main() 