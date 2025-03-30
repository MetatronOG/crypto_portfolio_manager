# 🐋 Whale Tracker & Trading Bot

An autonomous, profit-maximizing AI system that executes smart trades, accumulates ISO 20022 coins, and takes profits on meme coins while protecting against crashes.

## 🌟 Features

### 1️⃣ Smart Trading System (Whale + Momentum AI)
- **ISO 20022 Coins (Long-Term Hold)**
  - Never sell rule for XRP, XLM, HBAR, ALGO, QNT, IOTA, XDC
  - Automatic DCA (dollar-cost averaging) on major dips
  - No liquidation even during market crashes

- **Meme Coins (High-Risk Trading)**
  - Automated profit-taking at 2x, 3x, 5x
  - Dynamic volatility management
  - Profit recycling into ISO 20022 coins or stablecoins

### 2️⃣ Market Crash Protection
| Market Event | Bot Action |
|--------------|------------|
| BTC -5-10% | Reduce trade sizes, secure meme coin profits |
| BTC -10-20% | Stop meme trading, convert profits to stablecoins/ISO 20022 |
| BTC -20%+ | Move all meme assets to stablecoins, ISO 20022 untouched |

### 3️⃣ Cold Storage Integration
- Automatic transfers of profits to cold storage
- Secure storage of ISO 20022 holdings
- Configurable thresholds for each asset type

### 4️⃣ Real-Time Dashboard
- Live ISO 20022 holdings tracker
- Meme coin trading performance
- Market crash alerts
- Cold storage transfer status

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/whale-tracker-bot.git
cd whale-tracker-bot
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the project root:
```env
# Exchange API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_api_secret

# Blockchain API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key
XRPSCAN_API_KEY=your_xrpscan_api_key

# Notification Settings
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email Settings (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
```

4. **Configure trading settings**
Edit `config/trading_bot.json` to set:
- Risk levels and position sizes
- Cold storage thresholds
- DCA parameters
- Trading pairs

5. **Configure cold storage**
Edit `config/cold_storage.json` to set:
- Wallet addresses for each asset
- Transfer settings
- Security parameters

## 🎮 Usage

### Start the Trading Bot
```bash
# Full bot with trading enabled
python src/main.py

# Track whales only (no trading)
python src/main.py --track-only

# Test mode with mock trading
python src/main.py --test
```

### Start the Web Dashboard
```bash
# Start the Flask server
python web_ui/app.py
```
Access the dashboard at `http://localhost:5001`

## 🛠 Configuration

### Risk Levels
```json
{
    "low": {
        "max_position_size": "1000",
        "stop_loss_percentage": "5"
    },
    "medium": {
        "max_position_size": "2000",
        "stop_loss_percentage": "10"
    },
    "high": {
        "max_position_size": "5000",
        "stop_loss_percentage": "15"
    }
}
```

### Cold Storage Thresholds
```json
{
    "iso20022": "10000",
    "meme": "1000",
    "stablecoin": "50000"
}
```

### Trading Pairs
```json
{
    "iso20022": [
        "XRP/USDT",
        "XLM/USDT",
        "HBAR/USDT",
        "ALGO/USDT",
        "QNT/USDT",
        "IOTA/USDT",
        "XDC/USDT"
    ],
    "meme": [
        "DOGE/USDT",
        "SHIB/USDT",
        "PEPE/USDT",
        "FLOKI/USDT"
    ]
}
```

## 📊 Monitoring

### Logging
- Trading logs: `logs/trading_bot.log`
- Whale alerts: `logs/whale_alerts.log`
- Transfer logs: `logs/transfers.log`

### Notifications
- Telegram alerts for:
  - Large whale movements
  - Market crash warnings
  - Successful trades
  - Cold storage transfers

- Email notifications for:
  - Daily performance reports
  - Critical system alerts
  - Large transfers

## 🔒 Security

### API Key Storage
- All API keys stored in `.env` file
- Never commit `.env` to repository
- Use environment variables in production

### Cold Storage
- Whitelist-only withdrawals
- 2FA required for transfers
- Multiple confirmation thresholds
- Automatic backup of transfer history

## 📈 Performance Tracking

### Trading Performance
- Win/loss ratio
- Profit/loss by category
- Risk-adjusted returns
- Maximum drawdown

### Portfolio Analytics
- Asset allocation
- ISO 20022 accumulation rate
- Meme coin profit recycling
- Cold storage growth

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is for educational purposes only. Cryptocurrency trading carries significant risks. Always do your own research and never trade with money you can't afford to lose. 