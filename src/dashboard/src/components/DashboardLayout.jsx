import React from 'react';
import { Box, Grid, Container, Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled components
const DashboardContainer = styled(Container)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(4),
}));

const DashboardCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: '12px',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
  },
}));

const DashboardLayout = ({ children }) => {
  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <DashboardContainer maxWidth="xl">
        <Grid container spacing={3}>
          {/* Header Section */}
          <Grid item xs={12}>
            <DashboardCard>
              <Typography variant="h4" component="h1" gutterBottom>
                Trading Bot Dashboard
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Monitor and control your trading bot operations
              </Typography>
            </DashboardCard>
          </Grid>

          {/* Main Content */}
          {children}
        </Grid>
      </DashboardContainer>
    </Box>
  );
};

export default DashboardLayout; 