import { createTheme } from '@mui/material/styles';
import { useSelector } from 'react-redux';

// Create theme based on dark mode and language
export const createAppTheme = (darkMode, language) => {
  const direction = language === 'ar' ? 'rtl' : 'ltr';
  const fontFamily = language === 'ar' 
    ? ['Tajawal', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'].join(',')
    : ['"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif', 'Tajawal'].join(',');

  return createTheme({
    direction,
    typography: {
      fontFamily,
      h1: {
        fontWeight: 700,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
      h4: {
        fontWeight: 500,
      },
      h5: {
        fontWeight: 500,
      },
      h6: {
        fontWeight: 500,
      },
    },
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
        light: '#42a5f5',
        dark: '#1565c0',
        contrastText: '#fff',
      },
      secondary: {
        main: '#388e3c',
        light: '#4caf50',
        dark: '#2e7d32',
        contrastText: '#fff',
      },
      error: {
        main: '#d32f2f',
        light: '#ef5350',
        dark: '#c62828',
      },
      warning: {
        main: '#ed6c02',
        light: '#ff9800',
        dark: '#e65100',
      },
      info: {
        main: '#0288d1',
        light: '#03a9f4',
        dark: '#01579b',
      },
      success: {
        main: '#2e7d32',
        light: '#4caf50',
        dark: '#1b5e20',
      },
      background: darkMode ? {
        default: '#121212',
        paper: '#1e1e1e',
      } : {
        default: '#f5f5f5',
        paper: '#ffffff',
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: 'none',
            fontWeight: 500,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: darkMode 
              ? '0 2px 8px rgba(0, 0, 0, 0.3)' 
              : '0 2px 8px rgba(0, 0, 0, 0.1)',
          },
        },
      },
      MuiCardHeader: {
        styleOverrides: {
          root: {
            paddingBottom: 0,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            textAlign: direction === 'rtl' ? 'right' : 'left',
          },
        },
      },
    },
  });
};

// Default theme for initial render
const defaultTheme = createAppTheme(false, 'ar');

export default defaultTheme;

// Custom hook to get current theme
export const useAppTheme = () => {
  const { darkMode, language } = useSelector((state) => state.ui);
  return createAppTheme(darkMode, language);
};