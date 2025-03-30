import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    def __init__(self, config_path=None):
        """Initialize configuration with optional custom path"""
        if config_path is None:
            # Default to config.json in the project root
            self.config_path = Path(__file__).parent.parent.parent / "config.json"
        else:
            self.config_path = Path(config_path)
            
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
            
        self.load_config()
        
        # API Keys
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.xrpscan_api_key = os.getenv('XRPSCAN_API_KEY', '')
        
        # Whale Detection Settings
        self.min_eth_value = 1000  # Minimum ETH value to consider as whale movement
        self.min_xrp_value = 1000000  # Minimum XRP value
        self.min_xlm_value = 1000000  # Minimum XLM value
        self.alert_timeframe = 3600  # Alert timeframe in seconds (1 hour)
        
        # API Endpoints
        self.etherscan_endpoint = "https://api.etherscan.io/api"
        self.xrpscan_endpoint = "https://api.xrpscan.com/api/v1"
        
        # Rate Limiting
        self.max_requests_per_second = 5
        self.request_cooldown = 0.2  # seconds between requests
        
        # Cache Settings
        self.cache_duration = 300  # 5 minutes
        self.max_cached_transactions = 1000
        
        # Logging
        self.log_file = "logs/whale_alerts.log"
        self.log_level = "INFO"
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}, creating default config.")
            self.config = self._create_default_config()
            self.save_config()
            
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def _create_default_config(self):
        """Create default configuration settings"""
        return {
            "app_name": "Whale Tracker & Trading Bot",
            "version": "1.0.0",
            "log_level": "INFO",
            "log_file": "whale_tracker.log",
            
            "blockchain": {
                "ethereum": {
                    "enabled": True,
                    "api_key": "",
                    "node_url": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"
                },
                "solana": {
                    "enabled": True,
                    "api_key": "",
                    "node_url": "https://api.mainnet-beta.solana.com"
                },
                "bitcoin": {
                    "enabled": False,
                    "api_key": "",
                    "node_url": "https://btc.getblock.io/mainnet/"
                }
            },
            
            "whale_detection": {
                "whale_threshold_eth": 100,
                "whale_threshold_btc": 10,
                "whale_threshold_sol": 10000,
                "scan_interval_seconds": 60,
                "wallet_database": "data/wallets.csv",
                "transaction_log": "data/whale_transactions.csv"
            },
            
            "exchanges": {
                "binance": {
                    "api_key": "",
                    "api_secret": "",
                    "test_mode": True,
                    "options": {
                        "defaultType": "spot"
                    }
                },
                "bybit": {
                    "api_key": "",
                    "api_secret": "",
                    "test_mode": True,
                    "options": {
                        "defaultType": "spot"
                    }
                }
            },
            
            "risk_tiers": {
                "low_impact_threshold": 10,
                "high_impact_threshold": 25,
                "trading_pause_minutes": 30,
                "small_adjustment": 0.8,
                "medium_adjustment": 0.5,
                "large_adjustment": 0.0
            },
            
            "trading": {
                "default_market": "ETH/USDT",
                "default_size": 0.1,
                "max_position_usd": 1000,
                "risk_per_trade": 0.02,
                "enable_trading": False
            },
            
            "alerts": {
                "telegram": {
                    "enabled": True,
                    "bot_token": "",
                    "chat_id": ""
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_email": ""
                }
            }
        }

    def get(self, key, default=None):
        """Get configuration value with dot notation support"""
        if "." in key:
            sections = key.split(".")
            value = self.config
            for section in sections:
                if section in value:
                    value = value[section]
                else:
                    return default
            return value
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value with dot notation support"""
        if "." in key:
            sections = key.split(".")
            config_section = self.config
            for section in sections[:-1]:
                if section not in config_section:
                    config_section[section] = {}
                config_section = config_section[section]
            config_section[sections[-1]] = value
        else:
            self.config[key] = value
        self.save_config() 