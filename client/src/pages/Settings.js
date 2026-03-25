import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Switch,
  FormControlLabel,
  FormGroup,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  useTheme
} from '@mui/material';
import {
  DarkMode as DarkModeIcon,
  Language as LanguageIcon,
  Notifications as NotificationsIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Security as SecurityIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';

// Redux actions
import { 
  toggleDarkMode, 
  setLanguage, 
  addNotification, 
  clearNotifications 
} from '../store/slices/uiSlice';

const Settings = () => {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const { darkMode, language } = useSelector((state) => state.ui);
  
  // Local state
  const [showPassword, setShowPassword] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState('success');
  
  // User profile state
  const [userProfile, setUserProfile] = useState({
    name: 'محمد أحمد',
    email: 'mohammed@example.com',
    phone: '+966 50 123 4567',
    password: '********',
    language: language
  });
  
  // Handle form changes
  const handleProfileChange = (event) => {
    const { name, value } = event.target;
    setUserProfile({
      ...userProfile,
      [name]: value
    });
  };
  
  // Handle language change
  const handleLanguageChange = (event) => {
    const newLanguage = event.target.value;
    dispatch(setLanguage(newLanguage));
    setUserProfile({
      ...userProfile,
      language: newLanguage
    });
    localStorage.setItem('language', newLanguage);
  };
  
  // Handle dark mode toggle
  const handleDarkModeToggle = () => {
    dispatch(toggleDarkMode());
  };
  
  // Handle notifications toggle
  const handleNotificationsToggle = () => {
    setNotificationsEnabled(!notificationsEnabled);
  };
  
  // Handle email notifications toggle
  const handleEmailNotificationsToggle = () => {
    setEmailNotifications(!emailNotifications);
  };
  
  // Handle push notifications toggle
  const handlePushNotificationsToggle = () => {
    setPushNotifications(!pushNotifications);
  };
  
  // Handle password visibility toggle
  const handlePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  // Handle save settings
  const handleSaveSettings = () => {
    // Show success message
    setAlertMessage('تم حفظ الإعدادات بنجاح');
    setAlertSeverity('success');
    setAlertOpen(true);
    
    // Add notification
    dispatch(addNotification({
      message: 'تم تحديث إعدادات الحساب',
      type: 'success',
      duration: 5000
    }));
  };
  
  // Handle alert close
  const handleAlertClose = () => {
    setAlertOpen(false);
  };
  
  // Handle test notification
  const handleTestNotification = () => {
    dispatch(addNotification({
      message: 'هذا إشعار تجريبي',
      type: 'info',
      duration: 5000
    }));
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('settings.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* User Profile */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="الملف الشخصي" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="الاسم"
                    name="name"
                    value={userProfile.name}
                    onChange={handleProfileChange}
                    variant="outlined"
                    margin="normal"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="البريد الإلكتروني"
                    name="email"
                    type="email"
                    value={userProfile.email}
                    onChange={handleProfileChange}
                    variant="outlined"
                    margin="normal"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="رقم الهاتف"
                    name="phone"
                    value={userProfile.phone}
                    onChange={handleProfileChange}
                    variant="outlined"
                    margin="normal"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="كلمة المرور"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={userProfile.password}
                    onChange={handleProfileChange}
                    variant="outlined"
                    margin="normal"
                    InputProps={{
                      endAdornment: (
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handlePasswordVisibility}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveSettings}
                    >
                      حفظ التغييرات
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* App Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="إعدادات التطبيق" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <List>
                {/* Dark Mode */}
                <ListItem>
                  <ListItemIcon>
                    <DarkModeIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="الوضع الليلي" 
                    secondary="تفعيل الوضع الليلي للتطبيق"
                  />
                  <Switch
                    edge="end"
                    checked={darkMode}
                    onChange={handleDarkModeToggle}
                    inputProps={{
                      'aria-labelledby': 'dark-mode-switch',
                    }}
                  />
                </ListItem>
                
                <Divider variant="inset" component="li" />
                
                {/* Language */}
                <ListItem>
                  <ListItemIcon>
                    <LanguageIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="اللغة" 
                    secondary="اختر لغة التطبيق"
                  />
                  <FormControl sx={{ minWidth: 120 }}>
                    <Select
                      value={language}
                      onChange={handleLanguageChange}
                      displayEmpty
                      inputProps={{ 'aria-label': 'language' }}
                      size="small"
                    >
                      <MenuItem value="ar">العربية</MenuItem>
                      <MenuItem value="en">English</MenuItem>
                    </Select>
                  </FormControl>
                </ListItem>
                
                <Divider variant="inset" component="li" />
                
                {/* Notifications */}
                <ListItem>
                  <ListItemIcon>
                    <NotificationsIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="الإشعارات" 
                    secondary="تفعيل أو تعطيل الإشعارات"
                  />
                  <Switch
                    edge="end"
                    checked={notificationsEnabled}
                    onChange={handleNotificationsToggle}
                    inputProps={{
                      'aria-labelledby': 'notifications-switch',
                    }}
                  />
                </ListItem>
                
                {notificationsEnabled && (
                  <>
                    <ListItem sx={{ pl: 4 }}>
                      <ListItemText 
                        primary="إشعارات البريد الإلكتروني" 
                        secondary="استلام الإشعارات عبر البريد الإلكتروني"
                      />
                      <Switch
                        edge="end"
                        checked={emailNotifications}
                        onChange={handleEmailNotificationsToggle}
                        inputProps={{
                          'aria-labelledby': 'email-notifications-switch',
                        }}
                      />
                    </ListItem>
                    
                    <ListItem sx={{ pl: 4 }}>
                      <ListItemText 
                        primary="إشعارات الدفع" 
                        secondary="استلام الإشعارات على الجهاز"
                      />
                      <Switch
                        edge="end"
                        checked={pushNotifications}
                        onChange={handlePushNotificationsToggle}
                        inputProps={{
                          'aria-labelledby': 'push-notifications-switch',
                        }}
                      />
                    </ListItem>
                    
                    <ListItem sx={{ pl: 4 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={handleTestNotification}
                      >
                        اختبار الإشعارات
                      </Button>
                    </ListItem>
                  </>
                )}
                
                <Divider variant="inset" component="li" />
                
                {/* Security */}
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="الأمان" 
                    secondary="إعدادات الأمان والخصوصية"
                  />
                  <Button
                    variant="outlined"
                    size="small"
                    color="primary"
                  >
                    تعديل
                  </Button>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Data Management */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="إدارة البيانات" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        حذف البيانات المؤقتة
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        حذف البيانات المؤقتة والملفات المخزنة مؤقتاً
                      </Typography>
                      <Button
                        variant="outlined"
                        color="primary"
                        startIcon={<DeleteIcon />}
                      >
                        حذف البيانات المؤقتة
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        تصدير البيانات
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        تصدير بياناتك الشخصية وإعداداتك
                      </Typography>
                      <Button
                        variant="outlined"
                        color="primary"
                      >
                        تصدير البيانات
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        حذف الحساب
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        حذف حسابك وجميع بياناتك نهائياً
                      </Typography>
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                      >
                        حذف الحساب
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Success/Error Alert */}
      <Snackbar
        open={alertOpen}
        autoHideDuration={6000}
        onClose={handleAlertClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleAlertClose} severity={alertSeverity} sx={{ width: '100%' }}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
