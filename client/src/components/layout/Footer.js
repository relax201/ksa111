import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Typography, Link, Divider } from '@mui/material';

const Footer = () => {
  const { t } = useTranslation();
  
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
      }}
    >
      <Divider sx={{ mb: 2 }} />
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          {t('app.footer')}
        </Typography>
        
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            mt: { xs: 1, sm: 0 },
          }}
        >
          <Link href="#" color="inherit" underline="hover">
            <Typography variant="body2" color="text.secondary">
              سياسة الخصوصية
            </Typography>
          </Link>
          <Link href="#" color="inherit" underline="hover">
            <Typography variant="body2" color="text.secondary">
              شروط الاستخدام
            </Typography>
          </Link>
          <Link href="#" color="inherit" underline="hover">
            <Typography variant="body2" color="text.secondary">
              اتصل بنا
            </Typography>
          </Link>
        </Box>
      </Box>
    </Box>
  );
};

export default Footer;