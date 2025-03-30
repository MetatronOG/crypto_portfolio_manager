import React from 'react';
import { Grid, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SpeedIcon from '@mui/icons-material/Speed';

const MetricCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: '8px',
  backgroundColor: theme.palette.background.paper,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
}));

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '1.5rem',
  fontWeight: 'bold',
  color: theme.palette.primary.main,
}));

const MetricLabel = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: '0.875rem',
}));

const PerformanceMetrics = () => {
  // Example data - replace with real data from your bot
  const metrics = {
    totalProfit: 1250.50,
    profitChange: 12.5,
    activeTrades: 3,
    winRate: 68.5,
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <MetricCard>
          <AccountBalanceWalletIcon color="primary" />
          <Box>
            <MetricValue>${metrics.totalProfit.toFixed(2)}</MetricValue>
            <MetricLabel>Total Profit</MetricLabel>
          </Box>
        </MetricCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard>
          {metrics.profitChange >= 0 ? (
            <TrendingUpIcon color="success" />
          ) : (
            <TrendingDownIcon color="error" />
          )}
          <Box>
            <MetricValue>{metrics.profitChange}%</MetricValue>
            <MetricLabel>24h Change</MetricLabel>
          </Box>
        </MetricCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard>
          <SpeedIcon color="primary" />
          <Box>
            <MetricValue>{metrics.activeTrades}</MetricValue>
            <MetricLabel>Active Trades</MetricLabel>
          </Box>
        </MetricCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <MetricCard>
          <TrendingUpIcon color="success" />
          <Box>
            <MetricValue>{metrics.winRate}%</MetricValue>
            <MetricLabel>Win Rate</MetricLabel>
          </Box>
        </MetricCard>
      </Grid>
    </Grid>
  );
};

export default PerformanceMetrics; 