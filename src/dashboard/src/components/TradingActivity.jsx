import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  Box,
} from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
}));

const StatusChip = styled(Chip)(({ theme, status }) => ({
  backgroundColor: status === 'completed' 
    ? theme.palette.success.light 
    : status === 'pending'
    ? theme.palette.warning.light
    : theme.palette.error.light,
  color: status === 'completed'
    ? theme.palette.success.dark
    : status === 'pending'
    ? theme.palette.warning.dark
    : theme.palette.error.dark,
}));

const TradingActivity = () => {
  // Example data - replace with real data from your bot
  const trades = [
    {
      id: 1,
      timestamp: '2024-03-21 14:30:00',
      pair: 'SOL/USDT',
      type: 'Buy',
      amount: '2.5 SOL',
      price: '$98.45',
      status: 'completed',
      profit: '+$12.50',
    },
    {
      id: 2,
      timestamp: '2024-03-21 14:25:00',
      pair: 'SOL/USDT',
      type: 'Sell',
      amount: '1.8 SOL',
      price: '$97.80',
      status: 'completed',
      profit: '-$5.20',
    },
    {
      id: 3,
      timestamp: '2024-03-21 14:20:00',
      pair: 'SOL/USDT',
      type: 'Buy',
      amount: '3.2 SOL',
      price: '$97.50',
      status: 'pending',
      profit: 'Pending',
    },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Recent Trading Activity
      </Typography>
      <StyledTableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Pair</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Profit/Loss</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={trade.id}>
                <TableCell>{trade.timestamp}</TableCell>
                <TableCell>{trade.pair}</TableCell>
                <TableCell>
                  <Chip
                    label={trade.type}
                    color={trade.type === 'Buy' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{trade.amount}</TableCell>
                <TableCell>{trade.price}</TableCell>
                <TableCell>
                  <StatusChip
                    label={trade.status}
                    status={trade.status}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right" sx={{
                  color: trade.profit.startsWith('+') ? 'success.main' : 
                         trade.profit.startsWith('-') ? 'error.main' : 
                         'text.secondary'
                }}>
                  {trade.profit}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </StyledTableContainer>
    </Box>
  );
};

export default TradingActivity; 