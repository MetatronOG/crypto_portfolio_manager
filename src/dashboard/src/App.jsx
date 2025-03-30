import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, Grid } from '@mui/material';
import DashboardLayout from './components/DashboardLayout';
import PerformanceMetrics from './components/PerformanceMetrics';
import TradingActivity from './components/TradingActivity';
import BotStatus from './components/BotStatus';
import QuickActions from './components/QuickActions';

// Create a custom theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DashboardLayout>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <PerformanceMetrics />
            </Grid>
            <Grid item xs={12}>
              <TradingActivity />
            </Grid>
          </Grid>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <BotStatus />
            </Grid>
            <Grid item xs={12}>
              <QuickActions />
            </Grid>
          </Grid>
        </Grid>
      </DashboardLayout>
    </ThemeProvider>
  );
};

export default App; 