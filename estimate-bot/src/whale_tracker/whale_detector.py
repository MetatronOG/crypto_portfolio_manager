import time
import requests
import threading
import pandas as pd
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from decimal import Decimal
import json
import asyncio
import websockets

# Set up logging
def setup_logging(config):
    log_level = config.get("log_level", "INFO")
    log_file = config.get("log_file", "logs/whale_tracker.log")
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    return logging.getLogger(__name__)

class WhaleDetector:
    def __init__(self, config, wallet_manager):
        """Initialize the whale detector with config and wallet manager"""
        self.config = config
        self.wallet_manager = wallet_manager
        self.logger = setup_logging(config)
        self.logger.info("Initializing WhaleDetector")
        
        self.running = False
        self.detectors = {}
        self.threads = []
        self.recent_alerts = []
        self.last_request_time = 0
        self.xrp_websocket = None
        self.xrp_last_ledger = None
        self.event_loop = None
        
        # Initialize blockchain-specific detectors
        try:
            if getattr(self.config.blockchain.ethereum, 'enabled', False):
                self.logger.info("Ethereum detector initialized")
            else:
                self.logger.warning("Ethereum detector not enabled")
                
            # Storage for detected transactions
            self.whale_transactions = self.load_historical_data()
            self.logger.info(f"Loaded {len(self.whale_transactions)} historical whale transactions")
        except Exception as e:
            self.logger.error(f"Error loading historical data: {str(e)}")
            # Create an empty DataFrame as fallback
            self.whale_transactions = pd.DataFrame(columns=[
                'timestamp', 'blockchain', 'from_address', 'to_address', 
                'token', 'amount', 'usd_value', 'type', 'price_impact', 'tx_hash'
            ])
        
        # Initialize XRP tracking if enabled
        try:
            if getattr(self.config.blockchain.xrp, 'enabled', False):
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                self.event_loop.create_task(self._init_xrp_tracking())
                # Run the event loop in a separate thread
                self.xrp_thread = threading.Thread(target=self._run_event_loop, daemon=True)
                self.xrp_thread.start()
                self.logger.info("XRP detector initialized")
            else:
                self.logger.warning("XRP detector not enabled")
        except Exception as e:
            self.logger.error(f"Failed to initialize XRP tracking: {e}")
        
    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()
        
    def cleanup(self):
        """Clean up resources before shutdown."""
        if self.event_loop:
            self.event_loop.stop()
            self.event_loop.close()
        
    def load_historical_data(self):
        """Load historical whale transactions from storage"""
        tx_path = Path(self.config.get("whale_detection.transaction_log", "data/whale_transactions.csv"))
        
        # Ensure parent directory exists
        tx_path.parent.mkdir(exist_ok=True)
        
        try:
            if tx_path.exists():
                df = pd.read_csv(tx_path)
                self.logger.debug(f"Successfully loaded transaction data from {tx_path}")
                return df
            else:
                self.logger.warning(f"Transaction log file not found at {tx_path}, creating new one")
                # Create empty DataFrame with correct columns
                df = pd.DataFrame(columns=[
                    'timestamp', 'blockchain', 'from_address', 'to_address', 
                    'token', 'amount', 'usd_value', 'type', 'price_impact', 'tx_hash'
                ])
                df.to_csv(tx_path, index=False)
                return df
        except (FileNotFoundError, pd.errors.EmptyDataError) as e:
            self.logger.error(f"Error reading transaction data: {str(e)}")
            # Create empty DataFrame with correct columns
            df = pd.DataFrame(columns=[
                'timestamp', 'blockchain', 'from_address', 'to_address', 
                'token', 'amount', 'usd_value', 'type', 'price_impact', 'tx_hash'
            ])
            df.to_csv(tx_path, index=False)
            return df
        except Exception as e:
            self.logger.error(f"Unexpected error loading transaction data: {str(e)}", exc_info=True)
            raise
    
    def init_detectors(self):
        """Initialize chain-specific detectors"""
        # Ethereum detector
        eth_config = self.config.get("blockchain.ethereum", {})
        if eth_config.get("enabled", False) and eth_config.get("api_key"):
            self.detectors["ethereum"] = EthereumDetector(
                eth_config.get("api_key"),
                self.config.get("whale_detection.whale_threshold_eth", 100)
            )
            self.logger.info("Ethereum detector initialized")
            
        # Solana detector
        sol_config = self.config.get("blockchain.solana", {})
        if sol_config.get("enabled", False) and sol_config.get("api_key"):
            # TODO: Implement SolanaDetector class
            self.logger.info("Solana detector would be initialized here")
            
        # Bitcoin detector
        btc_config = self.config.get("blockchain.bitcoin", {})
        if btc_config.get("enabled", False) and btc_config.get("api_key"):
            # TODO: Implement BitcoinDetector class
            self.logger.info("Bitcoin detector would be initialized here")
            
        if not self.detectors:
            self.logger.warning("No detectors were initialized. Check API keys in config.")
    
    def start_monitoring(self):
        """Start the monitoring threads"""
        if not self.detectors:
            self.logger.error("Cannot start monitoring: No detectors initialized")
            return False
            
        self.running = True
        
        # Start a thread for each blockchain
        self.threads = []
        for blockchain, detector in self.detectors.items():
            thread = threading.Thread(
                target=self.monitor_blockchain,
                args=(blockchain, detector),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            
        self.logger.info(f"Monitoring started for: {', '.join(self.detectors.keys())}")
        return True
    
    def stop_monitoring(self):
        """Stop the monitoring threads"""
        if not self.running:
            return
            
        self.running = False
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        self.logger.info("Monitoring stopped")
    
    def monitor_blockchain(self, blockchain, detector):
        """Monitor a specific blockchain for whale transactions"""
        polling_interval = self.config.get("whale_detection.scan_interval_seconds", 60)
        
        while self.running:
            try:
                # Get latest transactions
                transactions = detector.get_latest_transactions()
                
                # Filter for whale transactions
                whale_txs = detector.filter_whale_transactions(transactions)
                
                if whale_txs:
                    self.logger.info(f"Found {len(whale_txs)} whale transactions on {blockchain}")
                    
                    # Process and store whale transactions
                    for tx in whale_txs:
                        self.process_whale_transaction(blockchain, tx)
                    
                # Wait for next polling interval
                time.sleep(polling_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring {blockchain}: {str(e)}", exc_info=True)
                time.sleep(polling_interval * 2)  # Longer interval on error
    
    def process_whale_transaction(self, blockchain, tx_data):
        """Process, store, and trigger alerts for whale transactions"""
        # Add blockchain info
        tx_data['blockchain'] = blockchain
        tx_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Calculate price impact if possible
        if 'price_impact' not in tx_data:
            tx_data['price_impact'] = self.estimate_price_impact(blockchain, tx_data)
        
        # Get wallet information
        from_info = self.wallet_manager.get_wallet_info(tx_data['from_address'])
        to_info = self.wallet_manager.get_wallet_info(tx_data['to_address'])
        
        # Determine transaction type if not provided
        if 'type' not in tx_data:
            tx_data['type'] = self.determine_transaction_type(tx_data, from_info, to_info)
        
        # Update wallet activity
        self.wallet_manager.update_wallet_activity(tx_data['from_address'], tx_data)
        self.wallet_manager.update_wallet_activity(tx_data['to_address'], tx_data)
        
        # Store transaction
        self.store_transaction(tx_data)
        
        # Trigger alerts - this will be implemented in the next step
        self.logger.info(f"Whale transaction detected: {tx_data['amount']} {tx_data['token']} " + 
                   f"({tx_data['type']}) worth ${tx_data['usd_value']:,.2f}")
        
        # TODO: Uncomment when alert_manager is implemented
        # from whale_tracker.alert_manager import trigger_alert
        # trigger_alert(tx_data, self.config)
    
    def estimate_price_impact(self, blockchain, tx_data):
        """Estimate the price impact of a transaction"""
        # This would integrate with price APIs to determine impact
        # For now, return a placeholder estimate based on transaction size
        token = tx_data['token']
        amount = tx_data['amount']
        
        # Placeholder logic - in reality, this would use liquidity data
        if blockchain == "ethereum":
            if amount > 1000:  # Large ETH transaction
                return 5.0  # Estimated 5% impact
            elif amount > 500:
                return 2.0
            elif amount > 100:
                return 0.5
        
        # Default minimal impact
        return 0.1
    
    def determine_transaction_type(self, tx_data, from_info, to_info):
        """Determine transaction type based on wallet categories"""
        if from_info.get('category') == 'exchange' and to_info.get('category') != 'exchange':
            return 'withdrawal'
        elif from_info.get('category') != 'exchange' and to_info.get('category') == 'exchange':
            return 'deposit'
        else:
            return 'transfer'
    
    def store_transaction(self, tx_data):
        """Store whale transaction in the database"""
        try:
            # Convert transaction to DataFrame row and append
            tx_df = pd.DataFrame([tx_data])
            self.whale_transactions = pd.concat([self.whale_transactions, tx_df], ignore_index=True)
            
            # Save to CSV
            tx_path = Path(self.config.get("whale_detection.transaction_log", "data/whale_transactions.csv"))
            self.whale_transactions.to_csv(tx_path, index=False)
            self.logger.debug(f"Stored transaction {tx_data['tx_hash']} to {tx_path}")
        except Exception as e:
            self.logger.error(f"Failed to store transaction: {str(e)}")
            # Try to save the transaction separately to avoid losing data
            try:
                backup_path = Path(self.config.get("whale_detection.transaction_log", "data/whale_transactions.csv")).with_suffix('.backup.csv')
                pd.DataFrame([tx_data]).to_csv(backup_path, mode='a', header=not backup_path.exists(), index=False)
                self.logger.warning(f"Transaction stored in backup file: {backup_path}")
            except Exception as backup_error:
                self.logger.critical(f"Could not save transaction even to backup: {str(backup_error)}")
    
    def get_recent_transactions(self, limit=10):
        """Get recent whale transactions for API/UI"""
        return self.whale_transactions.tail(limit).to_dict('records')
        
    def get_transactions_by_address(self, address, limit=50):
        """Get transactions involving a specific address"""
        address_txs = self.whale_transactions[
            (self.whale_transactions['from_address'] == address) | 
            (self.whale_transactions['to_address'] == address)
        ]
        return address_txs.tail(limit).to_dict('records')

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get whale alerts from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.recent_alerts if alert["timestamp"] > cutoff]
        
    def check_rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.request_cooldown:
            time.sleep(self.config.request_cooldown - time_since_last)
            
        self.last_request_time = time.time()
        
    def fetch_eth_transactions(self) -> List[Dict]:
        """Fetch large ETH transactions from Etherscan."""
        try:
            self.check_rate_limit()
            
            params = {
                "module": "account",
                "action": "txlist",
                "startblock": "0",
                "endblock": "99999999",
                "sort": "desc",
                "apikey": self.config.etherscan_api_key
            }
            
            response = requests.get(
                self.config.etherscan_endpoint,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "1":
                    return data["result"]
                else:
                    self.logger.error(f"Etherscan API error: {data.get('message')}")
            else:
                self.logger.error(f"HTTP error {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error fetching ETH transactions: {e}")
            
        return []
        
    def analyze_transaction(self, tx: Dict, blockchain: str = "ETH") -> Optional[Dict]:
        """Analyze a transaction for whale activity."""
        try:
            if blockchain == "ETH":
                value = Decimal(tx.get("value", "0")) / Decimal("1000000000000000000")  # Convert Wei to ETH
                min_value = self.config.whale_detection["whale_threshold_eth"]
            elif blockchain == "XRP":
                value = Decimal(tx.get("Amount", "0")) / Decimal("1000000")  # Convert drops to XRP
                min_value = self.config.whale_detection["whale_threshold_xrp"]
            else:
                self.logger.warning(f"Unsupported blockchain: {blockchain}")
                return None
                
            if value >= min_value:
                from_whale = self.wallet_manager.is_known_whale(tx["from"])
                to_whale = self.wallet_manager.is_known_whale(tx["to"])
                
                alert = {
                    "timestamp": datetime.now(),
                    "blockchain": blockchain,
                    "from_address": tx["from"],
                    "to_address": tx["to"],
                    "value": float(value),
                    "hash": tx["hash"],
                    "from_whale": from_whale,
                    "to_whale": to_whale
                }
                
                # Update wallet information
                if from_whale:
                    self.wallet_manager.update_wallet_activity(tx["from"], float(value))
                if to_whale:
                    self.wallet_manager.update_wallet_activity(tx["to"], float(value))
                    
                return alert
                
        except Exception as e:
            self.logger.error(f"Error analyzing transaction: {e}")
            
        return None
        
    def process_new_transactions(self):
        """Process new transactions and generate alerts."""
        # Process ETH transactions
        eth_transactions = self.fetch_eth_transactions()
        for tx in eth_transactions:
            alert = self.analyze_transaction(tx, "ETH")
            if alert:
                self.recent_alerts.append(alert)
                self.logger.info(
                    f"ETH Whale Alert: {alert['value']:.2f} ETH moved from "
                    f"{alert['from_address'][:8]}... to {alert['to_address'][:8]}..."
                )
                
        # Clean up old alerts
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_alerts = [
            alert for alert in self.recent_alerts 
            if alert["timestamp"] > cutoff
        ]
        
    def get_whale_influence(self, symbol: str) -> float:
        """Calculate whale influence on a specific token."""
        recent_alerts = self.get_recent_alerts(hours=1)
        total_volume = sum(
            alert["value"] for alert in recent_alerts
            if alert.get("symbol") == symbol
        )
        
        # Return a score between 0 and 1
        if symbol == "ETH":
            return min(1.0, total_volume / self.config.whale_detection["whale_threshold_eth"])
        elif symbol == "XRP":
            return min(1.0, total_volume / self.config.whale_detection["whale_threshold_xrp"])
        else:
            return 0.0
        
    def should_adjust_trading(self, symbol: str) -> bool:
        """Determine if trading should be adjusted based on whale activity."""
        influence = self.get_whale_influence(symbol)
        return influence >= 0.7  # High whale activity threshold

    async def _init_xrp_tracking(self):
        """Initialize XRP websocket connection."""
        try:
            self.xrp_websocket = await websockets.connect(
                self.config.blockchain["xrp"]["websocket_url"]
            )
            
            # Subscribe to transactions
            await self.xrp_websocket.send(json.dumps({
                "command": "subscribe",
                "streams": ["transactions"]
            }))
            
            # Start processing messages
            await self._process_xrp_messages()
            
        except Exception as e:
            self.logger.error(f"Error connecting to XRP websocket: {e}")
            
    async def _process_xrp_messages(self):
        """Process incoming XRP websocket messages."""
        while True:
            try:
                message = await self.xrp_websocket.recv()
                data = json.loads(message)
                
                if "transaction" in data:
                    tx = data["transaction"]
                    amount = Decimal(tx.get("Amount", "0")) / Decimal("1000000")  # Convert drops to XRP
                    
                    if amount >= self.config.whale_detection["whale_threshold_xrp"]:
                        alert = {
                            "timestamp": datetime.now(),
                            "blockchain": "XRP",
                            "from_address": tx.get("Account"),
                            "to_address": tx.get("Destination"),
                            "value": float(amount),
                            "hash": tx.get("hash"),
                            "from_whale": self.wallet_manager.is_known_whale(tx.get("Account")),
                            "to_whale": self.wallet_manager.is_known_whale(tx.get("Destination"))
                        }
                        
                        self.recent_alerts.append(alert)
                        self.logger.info(
                            f"XRP Whale Alert: {amount:,.2f} XRP moved from "
                            f"{alert['from_address'][:8]}... to {alert['to_address'][:8]}..."
                        )
                        
            except Exception as e:
                self.logger.error(f"Error processing XRP message: {e}")
                await asyncio.sleep(5)  # Wait before reconnecting
                await self._init_xrp_tracking()

class EthereumDetector:
    def __init__(self, api_key, threshold):
        """Initialize Ethereum detector with API key and threshold"""
        self.api_key = api_key
        self.threshold = threshold
        self.api_url = "https://api.etherscan.io/api"
        
        # Keep track of processed transactions to avoid duplicates
        self.processed_txs = set()
        
        # Get current ETH price
        self.eth_price = self.get_eth_price()
        self.price_last_updated = datetime.utcnow()
        
    def get_latest_transactions(self):
        """Get latest large transactions from Ethereum"""
        try:
            # Update ETH price every hour
            if (datetime.utcnow() - self.price_last_updated).total_seconds() > 3600:
                self.eth_price = self.get_eth_price()
                self.price_last_updated = datetime.utcnow()
            
            # Example implementation using Etherscan API
            # In a real implementation, you'd monitor multiple addresses or use a token transfer API
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance hot wallet as example
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 100,  # Last 100 transactions
                'sort': 'desc',
                'apikey': self.api_key
            }
            
            response = requests.get(self.api_url, params=params)
            data = response.json()
            
            if data['status'] == '1':
                return data['result']
            else:
                self.logger.error(f"Error fetching Ethereum transactions: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Exception in get_latest_transactions: {str(e)}", exc_info=True)
            return []
    
    def filter_whale_transactions(self, transactions):
        """Filter transactions that exceed the whale threshold"""
        whale_txs = []
        
        for tx in transactions:
            # Skip already processed transactions
            if tx['hash'] in self.processed_txs:
                continue
                
            # Add to processed set
            self.processed_txs.add(tx['hash'])
            
            # Skip failed transactions
            if tx['isError'] == '1':
                continue
                
            # Convert value from wei to ETH
            value_eth = int(tx['value']) / 10**18
            
            # Check if it meets the whale threshold
            if value_eth >= self.threshold:
                usd_value = value_eth * self.eth_price
                
                whale_txs.append({
                    'from_address': tx['from'],
                    'to_address': tx['to'],
                    'token': 'ETH',
                    'amount': value_eth,
                    'usd_value': usd_value,
                    'tx_hash': tx['hash'],
                    'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])).isoformat(),
                    'type': 'transfer'  # Default type, refined later
                })
                
        return whale_txs
    
    def get_eth_price(self):
        """Get current ETH price in USD"""
        try:
            # Use a price API like CoinGecko
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
            data = response.json()
            return data['ethereum']['usd']
        except Exception as e:
            self.logger.error(f"Error fetching ETH price: {str(e)}")
            return 3500  # Default fallback price 