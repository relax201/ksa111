import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Drawer,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Avatar,
  Toolbar,
  useTheme
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Recommend as RecommendIcon,
  ShowChart as TechnicalIcon,
  Assessment as FundamentalIcon,
  Storefront as MarketIcon,
  AccountBalance as FinancialIcon,
  Psychology as SentimentIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

const Sidebar = ({ drawerWidth, open, handleDrawerToggle, isMobile }) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  // Navigation items
  const navItems = [
    { 
      text: t('nav.dashboard'), 
      icon: <DashboardIcon />, 
      path: '/' 
    },
    { 
      text: t('nav.recommendations'), 
      icon: <RecommendIcon />, 
      path: '/recommendations' 
    },
    { 
      text: t('nav.technical'), 
      icon: <TechnicalIcon />, 
      path: '/technical' 
    },
    { 
      text: t('nav.fundamental'), 
      icon: <FundamentalIcon />, 
      path: '/fundamental' 
    },
    { 
      text: t('nav.market'), 
      icon: <MarketIcon />, 
      path: '/market' 
    },
    { 
      text: t('nav.financial'), 
      icon: <FinancialIcon />, 
      path: '/financial' 
    },
    { 
      text: t('nav.sentiment'), 
      icon: <SentimentIcon />, 
      path: '/sentiment' 
    }
  ];

  // Settings item
  const settingsItem = { 
    text: t('nav.settings'), 
    icon: <SettingsIcon />, 
    path: '/settings' 
  };

  // Handle navigation
  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      handleDrawerToggle();
    }
  };

  // Drawer content
  const drawerContent = (
    <>
      <Toolbar sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        py: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar 
            src="/logo192.png" 
            alt={t('app.shortTitle')}
            sx={{ 
              width: 40, 
              height: 40,
              bgcolor: 'primary.main'
            }}
          >
            T3
          </Avatar>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 700,
              color: 'primary.main'
            }}
          >
            {t('app.shortTitle')}
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  bgcolor: 'primary.light',
                  color: 'primary.contrastText',
                  '&:hover': {
                    bgcolor: 'primary.main',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
                borderRadius: 1,
                mx: 1,
                mb: 0.5,
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton
            onClick={() => handleNavigation(settingsItem.path)}
            selected={location.pathname === settingsItem.path}
            sx={{
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.main',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
              borderRadius: 1,
              mx: 1,
              mb: 0.5,
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              {settingsItem.icon}
            </ListItemIcon>
            <ListItemText primary={settingsItem.text} />
          </ListItemButton>
        </ListItem>
      </List>
    </>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      aria-label="navigation menu"
    >
      {/* Mobile drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={open}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              bgcolor: 'background.paper',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Desktop drawer */}
      {!isMobile && (
        <Drawer
          variant="persistent"
          open={open}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              bgcolor: 'background.paper',
              borderRight: `1px solid ${theme.palette.divider}`,
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}
    </Box>
  );
};

export default Sidebar;