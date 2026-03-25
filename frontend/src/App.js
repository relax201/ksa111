import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { useThemeContext } from './context/ThemeContext';
import { useAuth } from './context/AuthContext';
import rtlPlugin from 'stylis-plugin-rtl';
import { prefixer } from 'stylis';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';

// Layouts
import MainLayout from './components/layouts/MainLayout';
import AuthLayout from './components/layouts/AuthLayout';

// Pages
import Dashboard from './pages/Dashboard';
import MarketOverview from './pages/MarketOverview';
import StockDetails from './pages/StockDetails';
import StockScreener from './pages/StockScreener';
import TechnicalAnalysis from './pages/TechnicalAnalysis';
import FundamentalAnalysis from './pages/FundamentalAnalysis';
import Recommendations from './pages/Recommendations';
import Portfolio from './pages/Portfolio';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import NotFound from './pages/NotFound';

// RTL setup for Material UI
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>جاري التحميل...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  const { theme } = useThemeContext();
  const { checkAuth } = useAuth();
  
  // Create MUI theme
  const muiTheme = createTheme({
    direction: 'rtl',
    palette: {
      mode: theme,
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
    },
    typography: {
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
  });
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  return (
    <CacheProvider value={cacheRtl}>
      <ThemeProvider theme={muiTheme}>
        <CssBaseline />
        <Routes>
          {/* Auth routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
          </Route>
          
          {/* Main app routes */}
          <Route element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }>
            <Route path="/" element={<Dashboard />} />
            <Route path="/market" element={<MarketOverview />} />
            <Route path="/stock/:symbol" element={<StockDetails />} />
            <Route path="/screener" element={<StockScreener />} />
            <Route path="/technical" element={<TechnicalAnalysis />} />
            <Route path="/fundamental" element={<FundamentalAnalysis />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
          
          {/* 404 route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </ThemeProvider>
    </CacheProvider>
  );
}

export default App;