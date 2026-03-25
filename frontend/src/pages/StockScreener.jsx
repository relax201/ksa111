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
  Button,
  IconButton,
  TextField,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Close,
  FilterList,
  Save,
  ExpandMore,
  TrendingUp,
  TrendingDown,
  Search
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { screenerApi } from '../utils/api';
import { SECTORS } from '../utils/constants';
import { Link } from 'react-router-dom';

const StockScreener = () => {
  const { t } = useTranslation();
  const [screenResults, setScreenResults] = useState([]);
  const [savedScreens, setSavedScreens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveScreenDialogOpen, setSaveScreenDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [currentScreen, setCurrentScreen] = useState(null);
  const [orderBy, setOrderBy] = useState('market_cap');
  const [order, setOrder] = useState('desc');
  
  const [filters, setFilters] = useState({
    sector: '',
    min_price: 0,
    max_price: 1000,
    min_market_cap: 0,
    max_market_cap: 1000000,
    min_pe_ratio: 0,
    max_pe_ratio: 100,
    min_pb_ratio: 0,
    max_pb_ratio: 20,
    min_dividend_yield: 0,
    max_dividend_yield: 15,
    min_roe: -50,
    max_roe: 50,
    min_roa: -30,
    max_roa: 30,
    min_debt_to_equity: 0,
    max_debt_to_equity: 5,
    min_current_ratio: 0,
    max_current_ratio: 10,
    min_revenue_growth: -50,
    max_revenue_growth: 100,
    min_earnings_growth: -50,
    max_earnings_growth: 100
  });
  
  const [screenName, setScreenName] = useState('');

  // Fetch saved screens on component mount
  useEffect(() => {
    fetchSavedScreens();
  }, []);

  const fetchSavedScreens = async () => {
    try {
      const response = await screenerApi.getSavedScreens();
      setSavedScreens(response.data.data);
    } catch (error) {
      console.error('Error fetching saved screens:', error);
      setError(t('error_fetching_saved_screens'));
    }
  };

  const handleScreen = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await screenerApi.screen(filters);
      setScreenResults(response.data.data);
      
      setLoading(false);
    } catch (error) {
      console.error('Error running screen:', error);
      setError(t('error_running_screen'));
      setLoading(false);
    }
  };

  const handleSaveScreenDialogOpen = () => {
    setSaveScreenDialogOpen(true);
  };

  const handleSaveScreenDialogClose = () => {
    setSaveScreenDialogOpen(false);
    setScreenName('');
  };

  const handleDeleteDialogOpen = (screen) => {
    setCurrentScreen(screen);
    setDeleteDialogOpen(true);
  };

  const handleDeleteDialogClose = () => {
    setDeleteDialogOpen(false);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleRangeChange = (name, newValue) => {
    setFilters({
      ...filters,
      [`min_${name}`]: newValue[0],
      [`max_${name}`]: newValue[1]
    });
  };

  const handleScreenNameChange = (event) => {
    setScreenName(event.target.value);
  };

  const handleSaveScreen = async () => {
    try {
      await screenerApi.saveScreen({
        name: screenName,
        filters
      });
      
      fetchSavedScreens();
      handleSaveScreenDialogClose();
    } catch (error) {
      console.error('Error saving screen:', error);
      setError(t('error_saving_screen'));
    }
  };

  const handleDeleteScreen = async () => {
    try {
      await screenerApi.deleteScreen(currentScreen.id);
      fetchSavedScreens();
      handleDeleteDialogClose();
    } catch (error) {
      console.error('Error deleting screen:', error);
      setError(t('error_deleting_screen'));
    }
  };

  const handleLoadScreen = (screen) => {
    setFilters(screen.filters);
  };

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleResetFilters = () => {
    setFilters({
      sector: '',
      min_price: 0,
      max_price: 1000,
      min_market_cap: 0,
      max_market_cap: 1000000,
      min_pe_ratio: 0,
      max_pe_ratio: 100,
      min_pb_ratio: 0,
      max_pb_ratio: 20,
      min_dividend_yield: 0,
      max_dividend_yield: 15,
      min_roe: -50,
      max_roe: 50,
      min_roa: -30,
      max_roa: 30,
      min_debt_to_equity: 0,
      max_debt_to_equity: 5,
      min_current_ratio: 0,
      max_current_ratio: 10,
      min_revenue_growth: -50,
      max_revenue_growth: 100,
      min_earnings_growth: -50,
      max_earnings_growth: 100
    });
  };

  // Sort function for table
  const sortedResults = React.useMemo(() => {
    if (!screenResults || screenResults.length === 0) return [];
    
    return [...screenResults].sort((a, b) => {
      const valueA = a[orderBy] !== null ? a[orderBy] : (orderBy.includes('growth') || orderBy.includes('yield') ? 0 : Number.MIN_SAFE_INTEGER);
      const valueB = b[orderBy] !== null ? b[orderBy] : (orderBy.includes('growth') || orderBy.includes('yield') ? 0 : Number.MIN_SAFE_INTEGER);
      
      if (valueA < valueB) {
        return order === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        return order === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [screenResults, order, orderBy]);

  // Format value based on type
  const formatValue = (value, type) => {
    if (value === null || value === undefined) return t('na');
    
    switch (type) {
      case 'price':
      case 'ratio':
        return value.toFixed(2);
      case 'percent':
        return value.toFixed(2) + '%';
      case 'market_cap':
        return value >= 1000 ? (value / 1000).toFixed(2) + 'B' : value.toFixed(2) + 'M';
      default:
        return value.toString();
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('stock_screener')}
        </Typography>
        <Box>
          {screenResults.length > 0 && (
            <Button
              variant="outlined"
              startIcon={<Save />}
              onClick={handleSaveScreenDialogOpen}
              sx={{ mr: 1 }}
            >
              {t('save_screen')}
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Filters */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: { xs: 3, md: 0 } }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {t('filters')}
              </Typography>
              <Button
                variant="text"
                onClick={handleResetFilters}
              >
                {t('reset')}
              </Button>
            </Box>
            
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>{t('basic_filters')}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel id="sector-label">{t('sector')}</InputLabel>
                      <Select
                        labelId="sector-label"
                        id="sector"
                        name="sector"
                        value={filters.sector}
                        label={t('sector')}
                        onChange={handleFilterChange}
                      >
                        <MenuItem value="">{t('all_sectors')}</MenuItem>
                        {SECTORS.map((sector) => (
                          <MenuItem key={sector.value} value={sector.value}>
                            {sector.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('price_range')} ({filters.min_price} - {filters.max_price})
                    </Typography>
                    <Slider
                      value={[filters.min_price, filters.max_price]}
                      onChange={(e, newValue) => handleRangeChange('price', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={1000}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('market_cap')} ({formatValue(filters.min_market_cap, 'market_cap')} - {formatValue(filters.max_market_cap, 'market_cap')})
                    </Typography>
                    <Slider
                      value={[filters.min_market_cap, filters.max_market_cap]}
                      onChange={(e, newValue) => handleRangeChange('market_cap', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={1000000}
                      scale={(x) => x}
                      valueLabelFormat={(x) => formatValue(x, 'market_cap')}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>{t('valuation_filters')}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('pe_ratio')} ({filters.min_pe_ratio} - {filters.max_pe_ratio})
                    </Typography>
                    <Slider
                      value={[filters.min_pe_ratio, filters.max_pe_ratio]}
                      onChange={(e, newValue) => handleRangeChange('pe_ratio', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('pb_ratio')} ({filters.min_pb_ratio} - {filters.max_pb_ratio})
                    </Typography>
                    <Slider
                      value={[filters.min_pb_ratio, filters.max_pb_ratio]}
                      onChange={(e, newValue) => handleRangeChange('pb_ratio', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={20}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('dividend_yield')} ({filters.min_dividend_yield}% - {filters.max_dividend_yield}%)
                    </Typography>
                    <Slider
                      value={[filters.min_dividend_yield, filters.max_dividend_yield]}
                      onChange={(e, newValue) => handleRangeChange('dividend_yield', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={15}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>{t('financial_filters')}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('roe')} ({filters.min_roe}% - {filters.max_roe}%)
                    </Typography>
                    <Slider
                      value={[filters.min_roe, filters.max_roe]}
                      onChange={(e, newValue) => handleRangeChange('roe', newValue)}
                      valueLabelDisplay="auto"
                      min={-50}
                      max={50}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('roa')} ({filters.min_roa}% - {filters.max_roa}%)
                    </Typography>
                    <Slider
                      value={[filters.min_roa, filters.max_roa]}
                      onChange={(e, newValue) => handleRangeChange('roa', newValue)}
                      valueLabelDisplay="auto"
                      min={-30}
                      max={30}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('debt_to_equity')} ({filters.min_debt_to_equity} - {filters.max_debt_to_equity})
                    </Typography>
                    <Slider
                      value={[filters.min_debt_to_equity, filters.max_debt_to_equity]}
                      onChange={(e, newValue) => handleRangeChange('debt_to_equity', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={5}
                      step={0.1}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('current_ratio')} ({filters.min_current_ratio} - {filters.max_current_ratio})
                    </Typography>
                    <Slider
                      value={[filters.min_current_ratio, filters.max_current_ratio]}
                      onChange={(e, newValue) => handleRangeChange('current_ratio', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.1}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>{t('growth_filters')}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('revenue_growth')} ({filters.min_revenue_growth}% - {filters.max_revenue_growth}%)
                    </Typography>
                    <Slider
                      value={[filters.min_revenue_growth, filters.max_revenue_growth]}
                      onChange={(e, newValue) => handleRangeChange('revenue_growth', newValue)}
                      valueLabelDisplay="auto"
                      min={-50}
                      max={100}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      {t('earnings_growth')} ({filters.min_earnings_growth}% - {filters.max_earnings_growth}%)
                    </Typography>
                    <Slider
                      value={[filters.min_earnings_growth, filters.max_earnings_growth]}
                      onChange={(e, newValue) => handleRangeChange('earnings_growth', newValue)}
                      valueLabelDisplay="auto"
                      min={-50}
                      max={100}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
            
            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                fullWidth
                startIcon={<Search />}
                onClick={handleScreen}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : t('run_screen')}
              </Button>
            </Box>
            
            {savedScreens.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {t('saved_screens')}
                </Typography>
                <List>
                  {savedScreens.map((screen) => (
                    <ListItem
                      key={screen.id}
                      secondaryAction={
                        <IconButton
                          edge="end"
                          aria-label="delete"
                          onClick={() => handleDeleteDialogOpen(screen)}
                        >
                          <Delete />
                        </IconButton>
                      }
                    >
                      <ListItemButton onClick={() => handleLoadScreen(screen)}>
                        <ListItemText primary={screen.name} />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('screen_results')} {screenResults.length > 0 && `(${screenResults.length})`}
            </Typography>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                <CircularProgress />
              </Box>
            ) : screenResults.length > 0 ? (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('stock')}</TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'price'}
                          direction={orderBy === 'price' ? order : 'asc'}
                          onClick={() => handleRequestSort('price')}
                        >
                          {t('price')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'market_cap'}
                          direction={orderBy === 'market_cap' ? order : 'asc'}
                          onClick={() => handleRequestSort('market_cap')}
                        >
                          {t('market_cap')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'pe_ratio'}
                          direction={orderBy === 'pe_ratio' ? order : 'asc'}
                          onClick={() => handleRequestSort('pe_ratio')}
                        >
                          {t('pe_ratio')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'pb_ratio'}
                          direction={orderBy === 'pb_ratio' ? order : 'asc'}
                          onClick={() => handleRequestSort('pb_ratio')}
                        >
                          {t('pb_ratio')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'dividend_yield'}
                          direction={orderBy === 'dividend_yield' ? order : 'asc'}
                          onClick={() => handleRequestSort('dividend_yield')}
                        >
                          {t('dividend_yield')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'roe'}
                          direction={orderBy === 'roe' ? order : 'asc'}
                          onClick={() => handleRequestSort('roe')}
                        >
                          {t('roe')}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={orderBy === 'revenue_growth'}
                          direction={orderBy === 'revenue_growth' ? order : 'asc'}
                          onClick={() => handleRequestSort('revenue_growth')}
                        >
                          {t('revenue_growth')}
                        </TableSortLabel>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sortedResults.map((stock) => (
                      <TableRow key={stock.symbol}>
                        <TableCell component="th" scope="row">
                          <Link 
                            to={`/stock/${stock.symbol}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            <Typography variant="body2" fontWeight="bold">
                              {stock.symbol}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {stock.name}
                            </Typography>
                          </Link>
                        </TableCell>
                        <TableCell>{formatValue(stock.price, 'price')}</TableCell>
                        <TableCell>{formatValue(stock.market_cap, 'market_cap')}</TableCell>
                        <TableCell>{formatValue(stock.pe_ratio, 'ratio')}</TableCell>
                        <TableCell>{formatValue(stock.pb_ratio, 'ratio')}</TableCell>
                        <TableCell>{formatValue(stock.dividend_yield, 'percent')}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {stock.roe !== null && (
                              <>
                                {formatValue(stock.roe, 'percent')}
                                {stock.roe > 0 ? (
                                  <TrendingUp color="success" fontSize="small" sx={{ ml: 0.5 }} />
                                ) : stock.roe < 0 ? (
                                  <TrendingDown color="error" fontSize="small" sx={{ ml: 0.5 }} />
                                ) : null}
                              </>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {stock.revenue_growth !== null && (
                              <>
                                {formatValue(stock.revenue_growth, 'percent')}
                                {stock.revenue_growth > 0 ? (
                                  <TrendingUp color="success" fontSize="small" sx={{ ml: 0.5 }} />
                                ) : stock.revenue_growth < 0 ? (
                                  <TrendingDown color="error" fontSize="small" sx={{ ml: 0.5 }} />
                                ) : null}
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body1" align="center" sx={{ py: 3 }}>
                {t('no_screen_results')}
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Save Screen Dialog */}
      <Dialog open={saveScreenDialogOpen} onClose={handleSaveScreenDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {t('save_screen')}
            <IconButton onClick={handleSaveScreenDialogClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label={t('screen_name')}
            value={screenName}
            onChange={handleScreenNameChange}
            sx={{ mt: 1 }}
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSaveScreenDialogClose}>{t('cancel')}</Button>
          <Button 
            onClick={handleSaveScreen} 
            variant="contained"
            disabled={!screenName.trim()}
          >
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteDialogClose}>
        <DialogTitle>{t('confirm_delete')}</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            {t('confirm_delete_screen')}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleDeleteScreen} color="error">
            {t('delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StockScreener;