import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  Chip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import SettingsIcon from '@mui/icons-material/Settings';
import SpeedIcon from '@mui/icons-material/Speed';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import WarningIcon from '@mui/icons-material/Warning';

const StatusPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
}));

const StatusChip = styled(Chip)(({ theme, status }) => ({
  backgroundColor: status === 'active' 
    ? theme.palette.success.light 
    : status === 'paused'
    ? theme.palette.warning.light
    : theme.palette.error.light,
  color: status === 'active'
    ? theme.palette.success.dark
    : status === 'paused'
    ? theme.palette.warning.dark
    : theme.palette.error.dark,
}));

const BotStatus = () => {
  // Example data - replace with real data from your bot
  const botStatus = {
    isRunning: true,
    status: 'active',
    lastUpdate: '2024-03-21 14:35:00',
    tradingMode: 'auto',
    riskLevel: 'medium',
    balance: '25.5 SOL',
    warnings: ['Low liquidity detected', 'High volatility alert'],
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Bot Status
      </Typography>
      <StatusPaper>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PowerSettingsNewIcon 
            color={botStatus.isRunning ? 'success' : 'error'} 
            sx={{ mr: 1 }}
          />
          <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
            Trading Bot
          </Typography>
          <StatusChip 
            label={botStatus.status} 
            status={botStatus.status}
            size="small"
          />
        </Box>

        <List>
          <ListItem>
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Trading Mode"
              secondary={botStatus.tradingMode.charAt(0).toUpperCase() + botStatus.tradingMode.slice(1)}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <SpeedIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Risk Level"
              secondary={botStatus.riskLevel.charAt(0).toUpperCase() + botStatus.riskLevel.slice(1)}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <AccountBalanceWalletIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Available Balance"
              secondary={botStatus.balance}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <WarningIcon color="warning" />
            </ListItemIcon>
            <ListItemText 
              primary="Last Update"
              secondary={botStatus.lastUpdate}
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Active Warnings
          </Typography>
          {botStatus.warnings.map((warning, index) => (
            <Chip
              key={index}
              label={warning}
              color="warning"
              size="small"
              sx={{ mr: 1, mb: 1 }}
            />
          ))}
        </Box>

        <FormControlLabel
          control={
            <Switch
              checked={botStatus.isRunning}
              color="primary"
              onChange={() => {}}
            />
          }
          label="Enable Trading"
        />
      </StatusPaper>
    </Box>
  );
};

export default BotStatus; 