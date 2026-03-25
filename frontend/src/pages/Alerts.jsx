import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  IconButton,
  TextField,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Close,
  Notifications,
  NotificationsActive,
  NotificationsOff,
  Check,
  Info
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { alertsApi, stockApi } from '../utils/api';
import { Link } from 'react-router-dom';

const Alerts = () => {
  const { t } = useTranslation();
  const [alerts, setAlerts] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentAlert, setCurrentAlert] = useState(null);
  
  const [alertForm, setAlertForm] = useState({
    stock_id: '',
    type: 'price',
    condition: 'above',
    value: 0,
    active: true,
    notes: ''
  });

  // Fetch alerts and stocks on component mount
  useEffect(() => {
    fetchAlerts();
    fetchStocks();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertsApi.getAll();
      setAlerts(response.data.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setError(t('error_fetching_alerts'));
      setLoading(false);
    }
  };

  const fetchStocks = async () => {
    try {
      const response = await stockApi.getAll();
      setStocks(response.data.data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
    }
  };

  const handleAlertDialogOpen = (alert = null) => {
    if (alert) {
      setAlertForm({
        stock_id: alert.stock.id,
        type: alert.type,
        condition: alert.condition,
        value: alert.value,
        active: alert.active,
        notes: alert.notes || ''
      });
      setEditMode(true);
      setCurrentAlert(alert);
    } else {
      setAlertForm({
        stock_id: '',
        type: 'price',
        condition: 'above',
        value: 0,
        active: true,
        notes: ''
      });
      setEditMode(false);
      setCurrentAlert(null);
    }
    setAlertDialogOpen(true);
  };

  const handleAlertDialogClose = () => {
    setAlertDialogOpen(false);
  };

  const handleDeleteDialogOpen = (alert) => {
    setCurrentAlert(alert);
    setDeleteDialogOpen(true);
  };

  const handleDeleteDialogClose = () => {
    setDeleteDialogOpen(false);
  };

  const handleAlertFormChange = (event) => {
    const { name, value, checked } = event.target;
    setAlertForm({
      ...alertForm,
      [name]: name === 'active' ? checked : value
    });
  };

  const handleStockSelect = (event, newValue) => {
    setAlertForm({
      ...alertForm,
      stock_id: newValue ? newValue.id : ''
    });
  };

  const handleSaveAlert = async () => {
    try {
      if (editMode) {
        await alertsApi.update(currentAlert.id, alertForm);
      } else {
        await alertsApi.create(alertForm);
      }
      
      fetchAlerts();
      handleAlertDialogClose();
    } catch (error) {
      console.error('Error saving alert:', error);
      setError(t('error_saving_alert'));
    }
  };

  const handleDeleteAlert = async () => {
    try {
      await alertsApi.delete(currentAlert.id);
      fetchAlerts();
      handleDeleteDialogClose();
    } catch (error) {
      console.error('Error deleting alert:', error);
      setError(t('error_deleting_alert'));
    }
  };

  const handleMarkAsRead = async (alertId) => {
    try {
      await alertsApi.markAsRead(alertId);
      fetchAlerts();
    } catch (error) {
      console.error('Error marking alert as read:', error);
      setError(t('error_marking_alert_read'));
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const promises = alerts
        .filter(alert => alert.triggered && !alert.read)
        .map(alert => alertsApi.markAsRead(alert.id));
      
      await Promise.all(promises);
      fetchAlerts();
    } catch (error) {
      console.error('Error marking all alerts as read:', error);
      setError(t('error_marking_alerts_read'));
    }
  };

  // Get alert type label
  const getAlertTypeLabel = (type) => {
    switch (type) {
      case 'price':
        return t('price_alert');
      case 'volume':
        return t('volume_alert');
      case 'percent_change':
        return t('percent_change_alert');
      case 'moving_average':
        return t('moving_average_alert');
      default:
        return t('unknown_alert');
    }
  };

  // Get condition label
  const getConditionLabel = (condition) => {
    switch (condition) {
      case 'above':
        return t('above');
      case 'below':
        return t('below');
      case 'equal':
        return t('equal_to');
      case 'crosses_above':
        return t('crosses_above');
      case 'crosses_below':
        return t('crosses_below');
      default:
        return t('unknown_condition');
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Count unread triggered alerts
  const unreadAlertsCount = alerts.filter(alert => alert.triggered && !alert.read).length;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('alerts')}
          {unreadAlertsCount > 0 && (
            <Badge
              badgeContent={unreadAlertsCount}
              color="error"
              sx={{ ml: 2 }}
            >
              <NotificationsActive />
            </Badge>
          )}
        </Typography>
        <Box>
          {unreadAlertsCount > 0 && (
            <Button
              variant="outlined"
              startIcon={<Check />}
              onClick={handleMarkAllAsRead}
              sx={{ mr: 1 }}
            >
              {t('mark_all_as_read')}
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleAlertDialogOpen()}
          >
            {t('create_alert')}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Triggered Alerts */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {t('triggered_alerts')}
              </Typography>
              {alerts.filter(alert => alert.triggered).length > 0 ? (
                <Grid container spacing={2}>
                  {alerts
                    .filter(alert => alert.triggered)
                    .sort((a, b) => new Date(b.triggered_at) - new Date(a.triggered_at))
                    .map((alert) => (
                      <Grid item xs={12} md={6} lg={4} key={alert.id}>
                        <Card 
                          sx={{ 
                            position: 'relative',
                            bgcolor: alert.read ? 'background.paper' : 'action.hover'
                          }}
                        >
                          {!alert.read && (
                            <Box
                              sx={{
                                position: 'absolute',
                                top: 8,
                                right: 8,
                                zIndex: 1
                              }}
                            >
                              <Chip
                                label={t('new')}
                                color="error"
                                size="small"
                              />
                            </Box>
                          )}
                          <CardHeader
                            title={
                              <Link 
                                to={`/stock/${alert.stock.symbol}`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                              >
                                {alert.stock.name} ({alert.stock.symbol})
                              </Link>
                            }
                            subheader={getAlertTypeLabel(alert.type)}
                            action={
                              <IconButton
                                onClick={() => handleMarkAsRead(alert.id)}
                                disabled={alert.read}
                                title={t('mark_as_read')}
                              >
                                <Check />
                              </IconButton>
                            }
                          />
                          <CardContent>
                            <Typography variant="body1" gutterBottom>
                              {getConditionLabel(alert.condition)} {alert.value}
                              {alert.type === 'percent_change' && '%'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {t('triggered_at')}: {formatDate(alert.triggered_at)}
                            </Typography>
                            {alert.notes && (
                              <Typography variant="body2" sx={{ mt: 1 }}>
                                {alert.notes}
                              </Typography>
                            )}
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleAlertDialogOpen(alert)}
                              >
                                <Edit fontSize="small" />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteDialogOpen(alert)}
                              >
                                <Delete fontSize="small" />
                              </IconButton>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                </Grid>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_triggered_alerts')}
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Active Alerts */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {t('active_alerts')}
              </Typography>
              {alerts.filter(alert => alert.active && !alert.triggered).length > 0 ? (
                <Grid container spacing={2}>
                  {alerts
                    .filter(alert => alert.active && !alert.triggered)
                    .map((alert) => (
                      <Grid item xs={12} md={6} lg={4} key={alert.id}>
                        <Card>
                          <CardHeader
                            title={
                              <Link 
                                to={`/stock/${alert.stock.symbol}`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                              >
                                {alert.stock.name} ({alert.stock.symbol})
                              </Link>
                            }
                            subheader={getAlertTypeLabel(alert.type)}
                            action={
                              <Tooltip title={t('alert_active')}>
                                <NotificationsActive color="primary" />
                              </Tooltip>
                            }
                          />
                          <CardContent>
                            <Typography variant="body1" gutterBottom>
                              {getConditionLabel(alert.condition)} {alert.value}
                              {alert.type === 'percent_change' && '%'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {t('created_at')}: {formatDate(alert.created_at)}
                            </Typography>
                            {alert.notes && (
                              <Typography variant="body2" sx={{ mt: 1 }}>
                                {alert.notes}
                              </Typography>
                            )}
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleAlertDialogOpen(alert)}
                              >
                                <Edit fontSize="small" />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteDialogOpen(alert)}
                              >
                                <Delete fontSize="small" />
                              </IconButton>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                </Grid>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_active_alerts')}
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Inactive Alerts */}
          {alerts.filter(alert => !alert.active && !alert.triggered).length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t('inactive_alerts')}
                </Typography>
                <Grid container spacing={2}>
                  {alerts
                    .filter(alert => !alert.active && !alert.triggered)
                    .map((alert) => (
                      <Grid item xs={12} md={6} lg={4} key={alert.id}>
                        <Card sx={{ opacity: 0.7 }}>
                          <CardHeader
                            title={
                              <Link 
                                to={`/stock/${alert.stock.symbol}`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                              >
                                {alert.stock.name} ({alert.stock.symbol})
                              </Link>
                            }
                            subheader={getAlertTypeLabel(alert.type)}
                            action={
                              <Tooltip title={t('alert_inactive')}>
                                <NotificationsOff color="action" />
                              </Tooltip>
                            }
                          />
                          <CardContent>
                            <Typography variant="body1" gutterBottom>
                              {getConditionLabel(alert.condition)} {alert.value}
                              {alert.type === 'percent_change' && '%'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {t('created_at')}: {formatDate(alert.created_at)}
                            </Typography>
                            {alert.notes && (
                              <Typography variant="body2" sx={{ mt: 1 }}>
                                {alert.notes}
                              </Typography>
                            )}
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleAlertDialogOpen(alert)}
                              >
                                <Edit fontSize="small" />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteDialogOpen(alert)}
                              >
                                <Delete fontSize="small" />
                              </IconButton>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                </Grid>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* Alert Dialog */}
      <Dialog open={alertDialogOpen} onClose={handleAlertDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {editMode ? t('edit_alert') : t('create_alert')}
            <IconButton onClick={handleAlertDialogClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Autocomplete
                options={stocks}
                getOptionLabel={(option) => `${option.name} (${option.symbol})`}
                value={stocks.find(stock => stock.id === alertForm.stock_id) || null}
                onChange={handleStockSelect}
                disabled={editMode}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label={t('select_stock')}
                    variant="outlined"
                    fullWidth
                    required
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="alert-type-label">{t('alert_type')}</InputLabel>
                <Select
                  labelId="alert-type-label"
                  id="type"
                  name="type"
                  value={alertForm.type}
                  label={t('alert_type')}
                  onChange={handleAlertFormChange}
                >
                  <MenuItem value="price">{t('price_alert')}</MenuItem>
                  <MenuItem value="volume">{t('volume_alert')}</MenuItem>
                  <MenuItem value="percent_change">{t('percent_change_alert')}</MenuItem>
                  <MenuItem value="moving_average">{t('moving_average_alert')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="alert-condition-label">{t('condition')}</InputLabel>
                <Select
                  labelId="alert-condition-label"
                  id="condition"
                  name="condition"
                  value={alertForm.condition}
                  label={t('condition')}
                  onChange={handleAlertFormChange}
                >
                  <MenuItem value="above">{t('above')}</MenuItem>
                  <MenuItem value="below">{t('below')}</MenuItem>
                  <MenuItem value="equal">{t('equal_to')}</MenuItem>
                  {alertForm.type === 'moving_average' && (
                    <>
                      <MenuItem value="crosses_above">{t('crosses_above')}</MenuItem>
                      <MenuItem value="crosses_below">{t('crosses_below')}</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('value')}
                name="value"
                type="number"
                value={alertForm.value}
                onChange={handleAlertFormChange}
                InputProps={{
                  inputProps: { 
                    min: 0,
                    step: alertForm.type === 'percent_change' ? 0.01 : 0.001
                  },
                  endAdornment: alertForm.type === 'percent_change' ? '%' : null
                }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={alertForm.active}
                    onChange={handleAlertFormChange}
                    name="active"
                  />
                }
                label={t('alert_active')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('notes')}
                name="notes"
                value={alertForm.notes}
                onChange={handleAlertFormChange}
                multiline
                rows={3}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleAlertDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleSaveAlert} variant="contained">
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteDialogClose}>
        <DialogTitle>{t('confirm_delete')}</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            {t('confirm_delete_alert')}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleDeleteAlert} color="error">
            {t('delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Alerts;