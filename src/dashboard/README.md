# Trading Bot Dashboard

A modern, responsive dashboard for monitoring and controlling your Solana trading bot.

## Features

- Real-time performance metrics
- Trading activity monitoring
- Bot status and configuration
- Quick actions for common operations
- Modern Material-UI design
- Responsive layout for all devices

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Installation

1. Navigate to the dashboard directory:
   ```bash
   cd src/dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Development

To start the development server:

```bash
npm start
```

This will start the development server at `http://localhost:3000`.

## Building for Production

To create a production build:

```bash
npm run build
```

The build output will be in the `build` directory.

## Project Structure

```
src/dashboard/
├── components/
│   ├── DashboardLayout.jsx    # Main layout component
│   ├── PerformanceMetrics.jsx # Trading performance metrics
│   ├── TradingActivity.jsx    # Recent trading activity
│   ├── BotStatus.jsx         # Bot status and configuration
│   └── QuickActions.jsx      # Common bot operations
├── styles/                   # Custom styles
├── App.jsx                   # Main application component
└── package.json             # Project dependencies
```

## Customization

The dashboard uses Material-UI's theming system for customization. You can modify the theme in `App.jsx` to change colors, typography, and component styles.

## Integration with Trading Bot

To integrate this dashboard with your trading bot:

1. Update the data fetching logic in each component to connect to your bot's API
2. Implement the action handlers in the QuickActions component
3. Configure the WebSocket connection for real-time updates

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 