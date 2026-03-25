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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Alert,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  FilterList,
  Close,
  ArrowUpward,
  ArrowDownward,
  Remove,
  Info
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { recommendationApi } from '../utils/api';
import { RECOMMENDATION_TYPES, RECOMMENDATION_ACTIONS } from '../utils/constants';

const Recommendations = () => {
  const { t } = useTranslation();
  const [recommendations, setRecommendations] = useState([]);
  const [portfolioRecommendations, setPortfolioRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    action: '',
    min_confidence: 50,
    sector: ''
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState({
    min_confidence: 70,
    preferred_types: ['technical', 'fundamental'],
    risk_level: 'moderate'
  });

  // Fetch recommendations on component mount
  useEffect(() => {
    fetchRecommendations();
    fetchPortfolioRecommendations();
  }, [page]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      
      const params = {
        page,
        limit: 10,
        ...filters
      };
      
      const response = await recommendationApi.getAll(params);
      setRecommendations(response.data.data);
      setTotalPages(response.data.meta.total_pages);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError(t('error_fetching_recommendations'));
      setLoading(false);
    }
  };

  const fetchPortfolioRecommendations = async () => {
    try {
      const response = await recommendationApi.getPortfolioRecommendations();
      setPortfolioRecommendations(response.data.data);
    } catch (error) {
      console.error('Error fetching portfolio recommendations:', error);
    }
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleFilterOpen = () => {
    setFilterOpen(true);
  };

  const handleFilterClose = () => {
    setFilterOpen(false);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleApplyFilters = () => {
    setPage(1);
    fetchRecommendations();
    handleFilterClose();
  };

  const handleResetFilters = () => {
    setFilters({
      type: '',
      action: '',
      min_confidence: 50,
      sector: ''
    });
  };

  const handleSettingsOpen = () => {
    setSettingsOpen(true);
  };

  const handleSettingsClose = () => {
    setSettingsOpen(false);
  };

  const handleSettingsChange = (event) => {
    const { name, value } = event.target;
    setSettings({
      ...settings,
      [name]: value
    });
  };

  const handleSaveSettings = async () => {
    try {
      await recommendationApi.updateSettings(settings);
      fetchRecommendations();
      fetchPortfolioRecommendations();
      handleSettingsClose();
    } catch (error) {
      console.error('Error updating recommendation settings:', error);
      setError(t('error_updating_settings'));
    }
  };

  // Get action color
  const getActionColor = (action) => {
    switch (action) {
      case 'buy':
        return 'success';
      case 'sell':
        return 'error';
      case 'hold':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'primary';
    if (confidence >= 40) return 'warning';
    return 'error';
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('recommendations')}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={handleFilterOpen}
            sx={{ mr: 1 }}
          >
            {t('filter')}
          </Button>
          <Button
            variant="contained"
            onClick={handleSettingsOpen}
          >
            {t('settings')}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Portfolio Recommendations */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('portfolio_recommendations')}
            </Typography>
            {portfolioRecommendations.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('stock')}</TableCell>
                      <TableCell>{t('current_price')}</TableCell>
                      <TableCell>{t('recommendation')}</TableCell>
                      <TableCell>{t('target_price')}</TableCell>
                      <TableCell>{t('potential_return')}</TableCell>
                      <TableCell>{t('confidence')}</TableCell>
                      <TableCell>{t('time_frame')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {portfolioRecommendations.map((recommendation) => (
                      <TableRow key={recommendation.id}>
                        <TableCell>
                          <Link 
                            to={`/stock/${recommendation.stock.symbol}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            <Typography variant="body1">
                              {recommendation.stock.name} ({recommendation.stock.symbol})
                            </Typography>
                          </Link>
                        </TableCell>
                        <TableCell>{recommendation.price.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip
                            label={t(recommendation.action)}
                            color={getActionColor(recommendation.action)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{recommendation.target_price.toFixed(2)}</TableCell>
                        <TableCell>
                          <Typography
                            color={
                              ((recommendation.target_price - recommendation.price) / recommendation.price) > 0
                                ? 'success.main'
                                : 'error.main'
                            }
                          >
                            {((recommendation.target_price - recommendation.price) / recommendation.price * 100).toFixed(2)}%
                            {((recommendation.target_price - recommendation.price) / recommendation.price) > 0 ? (
                              <ArrowUpward fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} />
                            ) : (
                              <ArrowDownward fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} />
                            )}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${recommendation.confidence}%`}
                            color={getConfidenceColor(recommendation.confidence)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{t(recommendation.time_frame)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body1" align="center" sx={{ py: 3 }}>
                {t('no_portfolio_recommendations')}
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* All Recommendations */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('all_recommendations')}
            </Typography>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                <CircularProgress />
              </Box>
            ) : recommendations.length > 0 ? (
              <>
                <Grid container spacing={3}>
                  {recommendations.map((recommendation) => (
                    <Grid item xs={12} md={6} lg={4} key={recommendation.id}>
                      <Card>
                        <CardHeader
                          title={
                            <Link 
                              to={`/stock/${recommendation.stock.symbol}`}
                              style={{ textDecoration: 'none', color: 'inherit' }}
                            >
                              {recommendation.stock.name} ({recommendation.stock.symbol})
                            </Link>
                          }
                          subheader={recommendation.stock.sector}
                          action={
                            <Chip
                              label={t(recommendation.action)}
                              color={getActionColor(recommendation.action)}
                            />
                          }
                        />
                        <CardContent>
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('current_price')}:
                              </Typography>
                              <Typography variant="body1">
                                {recommendation.price.toFixed(2)}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('target_price')}:
                              </Typography>
                              <Typography variant="body1">
                                {recommendation.target_price.toFixed(2)}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('potential_return')}:
                              </Typography>
                              <Typography
                                variant="body1"
                                color={
                                  ((recommendation.target_price - recommendation.price) / recommendation.price) > 0
                                    ? 'success.main'
                                    : 'error.main'
                                }
                              >
                                {((recommendation.target_price - recommendation.price) / recommendation.price * 100).toFixed(2)}%
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('confidence')}:
                              </Typography>
                              <Chip
                                label={`${recommendation.confidence}%`}
                                color={getConfidenceColor(recommendation.confidence)}
                                size="small"
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('type')}:
                              </Typography>
                              <Typography variant="body1">
                                {t(recommendation.type)}
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2" color="text.secondary">
                                {t('time_frame')}:
                              </Typography>
                              <Typography variant="body1">
                                {t(recommendation.time_frame)}
                              </Typography>
                            </Grid>
                            <Grid item xs={12}>
                              <Divider sx={{ my: 1 }} />
                              <Typography variant="body2" color="text.secondary">
                                {t('analysis_date')}:
                              </Typography>
                              <Typography variant="body1">
                                {formatDate(recommendation.analysis_date)}
                              </Typography>
                            </Grid>
                            {recommendation.notes && (
                              <Grid item xs={12}>
                                <Typography variant="body2" color="text.secondary">
                                  {t('notes')}:
                                </Typography>
                                <Typography variant="body1">
                                  {recommendation.notes}
                                </Typography>
                              </Grid>
                            )}
                          </Grid>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={handlePageChange}
                    color="primary"
                  />
                </Box>
              </>
            ) : (
              <Typography variant="body1" align="center" sx={{ py: 3 }}>
                {t('no_recommendations')}
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Filter Dialog */}
      <Dialog open={filterOpen} onClose={handleFilterClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {t('filter_recommendations')}
            <IconButton onClick={handleFilterClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="type-label">{t('recommendation_type')}</InputLabel>
                <Select
                  labelId="type-label"
                  id="type"
                  name="type"
                  value={filters.type}
                  label={t('recommendation_type')}
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">{t('all')}</MenuItem>
                  {RECOMMENDATION_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="action-label">{t('recommendation_action')}</InputLabel>
                <Select
                  labelId="action-label"
                  id="action"
                  name="action"
                  value={filters.action}
                  label={t('recommendation_action')}
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">{t('all')}</MenuItem>
                  {RECOMMENDATION_ACTIONS.map((action) => (
                    <MenuItem key={action.value} value={action.value}>
                      {action.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('min_confidence')}
                type="number"
                name="min_confidence"
                value={filters.min_confidence}
                onChange={handleFilterChange}
                InputProps={{
                  inputProps: { min: 0, max: 100 }
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('sector')}
                name="sector"
                value={filters.sector}
                onChange={handleFilterChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleResetFilters}>{t('reset_filter')}</Button>
          <Button onClick={handleApplyFilters} variant="contained">
            {t('apply_filter')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={handleSettingsClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {t('recommendation_settings')}
            <IconButton onClick={handleSettingsClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('min_confidence')}
                type="number"
                name="min_confidence"
                value={settings.min_confidence}
                onChange={handleSettingsChange}
                InputProps={{
                  inputProps: { min: 0, max: 100 }
                }}
                helperText={t('min_confidence_help')}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="preferred-types-label">{t('preferred_types')}</InputLabel>
                <Select
                  labelId="preferred-types-label"
                  id="preferred-types"
                  name="preferred_types"
                  multiple
                  value={settings.preferred_types}
                  label={t('preferred_types')}
                  onChange={handleSettingsChange}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={t(value)} />
                      ))}
                    </Box>
                  )}
                >
                  {RECOMMENDATION_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="risk-level-label">{t('risk_level')}</InputLabel>
                <Select
                  labelId="risk-level-label"
                  id="risk-level"
                  name="risk_level"
                  value={settings.risk_level}
                  label={t('risk_level')}
                  onChange={handleSettingsChange}
                >
                  <MenuItem value="conservative">{t('conservative')}</MenuItem>
                  <MenuItem value="moderate">{t('moderate')}</MenuItem>
                  <MenuItem value="aggressive">{t('aggressive')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSettingsClose}>{t('cancel')}</Button>
          <Button onClick={handleSaveSettings} variant="contained">
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Recommendations;