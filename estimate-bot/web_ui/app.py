from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, timedelta
import random
import os
import requests
import time
from functools import lru_cache
import logging
from dotenv import load_dotenv
import hmac
import hashlib
from decimal import Decimal
from urllib.parse import urlencode
from typing import Dict, List

# Import our custom modules
from trading_bot.profit_distribution import ProfitDistributor, CoinCategory
from trading_bot.crash_protection import CrashProtection, MarketState

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize our trading components
profit_distributor = ProfitDistributor()
crash_protection = CrashProtection()

# Configuration from environment variables
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
CACHE_DURATION = int(os.getenv('CACHE_DURATION', 5))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 2))

class PriceCache:
    def __init__(self):
        self.cache = {}
        self.last_update = 0
        self.update_interval = 5  # seconds
        self.error_count = 0
        self.max_errors = 3
        self.error_reset_time = 60  # seconds

    def get_price_data(self):
        current_time = time.time()
        
        # If we've had too many errors, wait before trying again
        if self.error_count >= self.max_errors:
            if current_time - self.last_update < self.error_reset_time:
                logger.warning("Too many API errors, using cached data")
                return self.cache
            else:
                self.error_count = 0  # Reset error count after waiting
        
        # If cache is empty or too old, update it
        if not self.cache or (current_time - self.last_update) >= self.update_interval:
            try:
                # Get ISO20022 coins and BTC prices
                coins = list(profit_distributor.ISO20022Coins.SYMBOLS) + ["bitcoin"]
                coins_str = ",".join(coins).lower()
                
                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {
                    "ids": coins_str,
                    "vs_currencies": "usd",
                    "include_24hr_vol": True,
                    "include_24hr_change": True
                }
                response = requests.get(url, params=params, timeout=5)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning("Rate limit hit, using cached data")
                    self.error_count += 1
                    return self.cache
                    
                response.raise_for_status()
                new_data = response.json()
                
                # Update cache if we got valid data
                if new_data:
                    self.cache = new_data
                    self.last_update = current_time
                    self.error_count = 0  # Reset error count on success
                    logger.info("Price cache updated successfully")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error updating price cache: {e}")
                self.error_count += 1
                # If cache is empty, set default values
                if not self.cache:
                    self.cache = {coin: {"usd": 0, "usd_24h_change": 0, "usd_24h_vol": 0} 
                                for coin in coins}
        
        return self.cache

price_cache = PriceCache()

# Simulated data store
class BotState:
    def __init__(self):
        self.start_time = datetime.now()
        self.last_trade_time = datetime.now()
        self.whale_alerts_1h = []
        self.whale_alerts_24h = []
        self.trades = []
        self.errors = []
        
    def get_uptime(self):
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours} hours {minutes} minutes"

    def add_whale_alert(self, wallet, amount):
        alert = {
            "wallet": wallet,
            "amount": amount,
            "timestamp": datetime.now()
        }
        self.whale_alerts_24h.append(alert)
        # Clean up old alerts
        now = datetime.now()
        self.whale_alerts_1h = [a for a in self.whale_alerts_24h 
                               if now - a["timestamp"] < timedelta(hours=1)]
        self.whale_alerts_24h = [a for a in self.whale_alerts_24h 
                                if now - a["timestamp"] < timedelta(hours=24)]

bot_state = BotState()

def get_mock_portfolio():
    return {
        "BTC": round(random.uniform(0.1, 2.0), 6),
        "ETH": round(random.uniform(1.0, 10.0), 6),
        "USDT": round(random.uniform(10000, 50000), 2)
    }

def get_market_data():
    data = price_cache.get_price_data()
    
    if not data or "bitcoin" not in data or "ethereum" not in data:
        logger.warning("Using fallback market data")
        return None
    
    return {
        "BTC/USDT": {
            "price": data["bitcoin"]["usd"],
            "24h_change": data["bitcoin"].get("usd_24h_change", 0),
            "volume": data["bitcoin"].get("usd_24h_vol", 0)
        },
        "ETH/USDT": {
            "price": data["ethereum"]["usd"],
            "24h_change": data["ethereum"].get("usd_24h_change", 0),
            "volume": data["ethereum"].get("usd_24h_vol", 0)
        }
    }

# Mock data for testing
class MockData:
    @staticmethod
    def get_mock_iso20022_holdings():
        return [
            {
                "symbol": "XRP",
                "amount": round(random.uniform(1000, 5000), 2),
                "value": round(random.uniform(500, 2500), 2),
                "dca_active": random.choice([True, False])
            },
            {
                "symbol": "XLM",
                "amount": round(random.uniform(5000, 20000), 2),
                "value": round(random.uniform(1000, 5000), 2),
                "dca_active": random.choice([True, False])
            }
        ]

    @staticmethod
    def get_mock_meme_holdings():
        return [
            {
                "symbol": "DOGE",
                "amount": round(random.uniform(10000, 50000), 2),
                "entry_price": round(random.uniform(0.05, 0.15), 4),
                "current_price": round(random.uniform(0.05, 0.15), 4),
                "pl_percentage": round(random.uniform(-20, 50), 2),
                "action": random.choice([None, "Take Profit", "Stop Loss"])
            },
            {
                "symbol": "SHIB",
                "amount": round(random.uniform(1000000, 5000000), 2),
                "entry_price": round(random.uniform(0.00001, 0.0001), 8),
                "current_price": round(random.uniform(0.00001, 0.0001), 8),
                "pl_percentage": round(random.uniform(-20, 50), 2),
                "action": random.choice([None, "Take Profit", "Stop Loss"])
            }
        ]

    @staticmethod
    def get_mock_protection_rules():
        btc_drop = random.uniform(-25, 5)
        return [
            {
                "description": "Reduce Position Sizes (5-10% Drop)",
                "active": -10 <= btc_drop <= -5
            },
            {
                "description": "Stop Meme Trading (10-20% Drop)",
                "active": -20 <= btc_drop <= -10
            },
            {
                "description": "Convert to Stablecoins (>20% Drop)",
                "active": btc_drop <= -20
            }
        ]

    @staticmethod
    def get_mock_transfers():
        return [
            {
                "time": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                "asset": random.choice(["XRP", "XLM", "USDT"]),
                "amount": round(random.uniform(100, 1000), 2),
                "status": random.choice(["Completed", "Pending"])
            } for _ in range(5)
        ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    try:
        # Get market data
        price_data = price_cache.get_price_data()
        
        # Update market state based on BTC price
        btc_price = Decimal(str(price_data.get("bitcoin", {}).get("usd", 0)))
        market_state = crash_protection.update_market_state(btc_price)
        
        # Calculate BTC drop percentage
        btc_reference = crash_protection.btc_reference_price
        btc_drop_percentage = 0
        if btc_reference > 0:
            btc_drop_percentage = ((btc_price - btc_reference) / btc_reference) * 100

        # Get mock data (replace with real data in production)
        iso20022_holdings = MockData.get_mock_iso20022_holdings()
        meme_holdings = MockData.get_mock_meme_holdings()
        protection_rules = MockData.get_mock_protection_rules()
        recent_transfers = MockData.get_mock_transfers()

        # Calculate totals
        totals = {
            "iso20022": sum(holding["value"] for holding in iso20022_holdings),
            "meme": sum(
                holding["amount"] * holding["current_price"] 
                for holding in meme_holdings
            ),
            "stablecoin": round(random.uniform(5000, 20000), 2)  # Mock data
        }

        # Cold storage data
        cold_storage = {
            "iso20022": round(random.uniform(10000, 50000), 2),  # Mock data
            "stablecoin": round(random.uniform(5000, 20000), 2),  # Mock data
            "pending_transfers": random.randint(0, 3)  # Mock data
        }

        return jsonify({
            "market_state": market_state.value,
            "btc_price": float(btc_price),
            "btc_reference_price": float(btc_reference),
            "btc_drop_percentage": float(btc_drop_percentage),
            "iso20022_holdings": iso20022_holdings,
            "meme_holdings": meme_holdings,
            "protection_rules": protection_rules,
            "totals": totals,
            "cold_storage": cold_storage,
            "recent_transfers": recent_transfers,
            "system": {
                "uptime": "2 hours 30 minutes",  # Mock data
                "api_status": "Operational",
                "errors": []
            }
        })
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({
            "error": "Failed to fetch market data",
            "message": str(e)
        }), 500

@app.route('/api/toggle-meme-trading', methods=['POST'])
def toggle_meme_trading():
    try:
        # Mock implementation - replace with real logic
        enabled = random.choice([True, False])
        return jsonify({"enabled": enabled})
    except Exception as e:
        logger.error(f"Error toggling meme trading: {e}")
        return jsonify({
            "error": "Failed to toggle meme trading",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 