import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  ButtonGroup,
  IconButton,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import RefreshIcon from '@mui/icons-material/Refresh';
import SettingsIcon from '@mui/icons-material/Settings';
import HistoryIcon from '@mui/icons-material/History';
import WarningIcon from '@mui/icons-material/Warning';

const ActionPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
}));

const ActionButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(0.5),
  borderRadius: '8px',
  textTransform: 'none',
  fontWeight: 500,
}));

const QuickActions = () => {
  const handleAction = (action) => {
    // Implement action handlers here
    console.log(`Action clicked: ${action}`);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Quick Actions
      </Typography>
      <ActionPaper>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Primary Actions */}
          <ButtonGroup variant="contained" fullWidth>
            <ActionButton
              startIcon={<PlayArrowIcon />}
              onClick={() => handleAction('start')}
            >
              Start Trading
            </ActionButton>
            <ActionButton
              startIcon={<PauseIcon />}
              onClick={() => handleAction('pause')}
            >
              Pause Trading
            </ActionButton>
          </ButtonGroup>

          {/* Secondary Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1 }}>
            <Tooltip title="Refresh Data">
              <IconButton
                color="primary"
                onClick={() => handleAction('refresh')}
                sx={{ flex: 1 }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="View History">
              <IconButton
                color="primary"
                onClick={() => handleAction('history')}
                sx={{ flex: 1 }}
              >
                <HistoryIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Settings">
              <IconButton
                color="primary"
                onClick={() => handleAction('settings')}
                sx={{ flex: 1 }}
              >
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="View Alerts">
              <IconButton
                color="warning"
                onClick={() => handleAction('alerts')}
                sx={{ flex: 1 }}
              >
                <WarningIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Emergency Actions */}
          <Button
            variant="outlined"
            color="error"
            fullWidth
            onClick={() => handleAction('emergency_stop')}
          >
            Emergency Stop
          </Button>
        </Box>
      </ActionPaper>
    </Box>
  );
};

export default QuickActions; 