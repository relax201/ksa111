import React, { useEffect, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { Box, ThemeProvider, CssBaseline } from '@mui/material';
import rtlPlugin from 'stylis-plugin-rtl';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';

// Layout components
import Layout from './components/layout/Layout';

// Page components
import Dashboard from './pages/Dashboard';
import Recommendations from './pages/Recommendations';
import TechnicalAnalysis from './pages/TechnicalAnalysis';
import FundamentalAnalysis from './pages/FundamentalAnalysis';
import MarketData from './pages/MarketData';
import FinancialData from './pages/FinancialData';
import SentimentAnalysis from './pages/SentimentAnalysis';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

// Redux actions
import { setLanguage } from './store/slices/uiSlice';

// Theme
import { createAppTheme } from './theme';

function App() {
  const { i18n } = useTranslation();
  const dispatch = useDispatch();
  const { language, darkMode } = useSelector((state) => state.ui);

  // Create RTL cache for Material UI
  const cacheRtl = createCache({
    key: 'muirtl',
    stylisPlugins: [prefixer, rtlPlugin],
  });

  // Create LTR cache for Material UI
  const cacheLtr = createCache({
    key: 'muiltr',
    stylisPlugins: [prefixer],
  });

  // Create theme based on current settings
  const theme = useMemo(() => createAppTheme(darkMode, language), [darkMode, language]);

  // Set language based on Redux state
  useEffect(() => {
    i18n.changeLanguage(language);
    document.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language, i18n]);

  // Initialize language from browser or localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && savedLanguage !== language) {
      dispatch(setLanguage(savedLanguage));
    }
  }, [dispatch, language]);

  return (
    <CacheProvider value={language === 'ar' ? cacheRtl : cacheLtr}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', height: '100vh' }}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="recommendations" element={<Recommendations />} />
              <Route path="technical" element={<TechnicalAnalysis />} />
              <Route path="fundamental" element={<FundamentalAnalysis />} />
              <Route path="market" element={<MarketData />} />
              <Route path="financial" element={<FinancialData />} />
              <Route path="sentiment" element={<SentimentAnalysis />} />
              <Route path="settings" element={<Settings />} />
              <Route path="404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Route>
          </Routes>
        </Box>
      </ThemeProvider>
    </CacheProvider>
  );
}

export default App;