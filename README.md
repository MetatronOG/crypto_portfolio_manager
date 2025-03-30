# Crypto Portfolio Manager

A comprehensive cryptocurrency portfolio management system that combines trading automation, whale tracking, and portfolio analytics in a modern web interface.

## Features

- **Portfolio Management**
  - Real-time portfolio tracking
  - Multi-exchange support (Binance, Bybit)
  - Performance analytics and metrics
  - Transaction history and logging

- **Trading Automation**
  - Configurable trading strategies
  - Risk management tools
  - Automated trade execution
  - Performance monitoring

- **Whale Tracking**
  - Large transaction monitoring
  - Whale wallet analysis
  - Market impact assessment
  - Alert system for significant movements

- **Dashboard Interface**
  - Real-time portfolio overview
  - Performance metrics visualization
  - Trading activity monitoring
  - Quick action controls
  - Responsive design

## Project Structure

```
crypto-portfolio-manager/
├── src/
│   ├── dashboard/           # React-based web dashboard
│   │   ├── public/         # Static assets
│   │   └── src/           # Dashboard source code
│   │       ├── components/ # React components
│   │       └── App.jsx    # Main dashboard application
│   └── trading_bot/       # Trading bot core
│       ├── exchanges/     # Exchange integrations
│       └── strategies/    # Trading strategies
├── telegram_alerts.py     # Telegram notification system
├── transaction_logger.py  # Transaction logging system
├── wallet_tracker.py      # Wallet monitoring system
└── whale_tracker_integration.txt  # Whale tracking configuration
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/MetatronOG/crypto-portfolio-manager.git
   cd crypto-portfolio-manager
   ```

2. Install dependencies:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Install Node.js dependencies for the dashboard
   cd src/dashboard
   npm install
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret
   BYBIT_API_KEY=your_bybit_api_key
   BYBIT_API_SECRET=your_bybit_api_secret
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

4. Start the services:
   ```bash
   # Start the trading bot
   python src/trading_bot/main.py

   # Start the dashboard (in a separate terminal)
   cd src/dashboard
   npm start
   ```

## Configuration

### Trading Bot Settings
- Configure trading pairs in `src/trading_bot/config.py`
- Adjust risk management parameters
- Set up trading strategies

### Whale Tracking
- Configure whale thresholds in `whale_tracker_integration.txt`
- Set up alert conditions
- Customize tracking parameters

### Dashboard
- Customize the dashboard layout
- Configure display preferences
- Set up additional metrics

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 