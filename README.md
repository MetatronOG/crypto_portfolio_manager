# Solana Trading Bot

A sophisticated trading bot for the Solana blockchain that includes features for tracking whales, monitoring transactions, and executing trades based on custom strategies.

## Features

- Whale tracking and monitoring
- Transaction logging
- Telegram alerts
- Dashboard interface
- Multiple exchange support (Binance, Bybit)
- Custom trading strategies

## Project Structure

```
.
├── src/
│   ├── dashboard/          # React dashboard frontend
│   └── trading_bot/        # Python trading bot backend
│       └── exchanges/      # Exchange integrations
├── telegram_alerts.py      # Telegram notification system
├── transaction_logger.py   # Transaction logging system
└── wallet_tracker.py       # Wallet monitoring system
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solana-trading-bot.git
cd solana-trading-bot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies for the dashboard:
```bash
cd src/dashboard
npm install
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in your API keys and configuration

5. Start the services:
```bash
# Start the trading bot
python src/trading_bot/main.py

# Start the dashboard (in a separate terminal)
cd src/dashboard
npm start
```

## Configuration

The bot can be configured through the following files:
- `.env` - Environment variables and API keys
- `src/trading_bot/config.py` - Trading bot configuration
- `src/dashboard/src/config.js` - Dashboard configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details. 