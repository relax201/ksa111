import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  CssBaseline, 
  Toolbar, 
  Container, 
  useMediaQuery 
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

import Sidebar from './Sidebar';
import TopBar from './TopBar';
import Footer from './Footer';
import Notifications from './Notifications';
import { toggleSidebar } from '../../store/slices/uiSlice';

const Layout = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { sidebarOpen, notifications, darkMode, language } = useSelector((state) => state.ui);
  
  // Close sidebar automatically on mobile
  const [mobileOpen, setMobileOpen] = useState(false);
  
  // Set data-theme attribute for CSS selectors
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);
  
  // Set language attribute for CSS selectors
  useEffect(() => {
    document.documentElement.setAttribute('lang', language);
  }, [language]);
  
  const handleDrawerToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen);
    } else {
      dispatch(toggleSidebar());
    }
  };

  // Calculate sidebar width
  const drawerWidth = 280;
  
  // Determine sidebar position based on language
  const isRtl = language === 'ar';
  
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* Top navigation bar */}
      <TopBar 
        drawerWidth={drawerWidth} 
        open={isMobile ? mobileOpen : sidebarOpen} 
        handleDrawerToggle={handleDrawerToggle} 
      />
      
      {/* Sidebar navigation */}
      <Sidebar 
        drawerWidth={drawerWidth} 
        open={isMobile ? mobileOpen : sidebarOpen} 
        handleDrawerToggle={handleDrawerToggle}
        isMobile={isMobile}
      />
      
      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default',
          color: 'text.primary',
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(sidebarOpen && !isMobile && {
            width: `calc(100% - ${drawerWidth}px)`,
            [isRtl ? 'marginRight' : 'marginLeft']: `${drawerWidth}px`,
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
        }}
      >
        <Toolbar />
        <Container 
          maxWidth="xl" 
          sx={{ 
            flexGrow: 1, 
            py: 2,
            px: { xs: 1, sm: 2, md: 3 } 
          }}
        >
          <Outlet />
        </Container>
        <Footer />
      </Box>
      
      {/* Notifications */}
      <Notifications notifications={notifications} />
    </Box>
  );
};

export default Layout;