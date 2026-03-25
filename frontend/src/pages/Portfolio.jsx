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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Tooltip
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Close,
  TrendingUp,
  TrendingDown,
  Info,
  ArrowUpward,
  ArrowDownward,
  Remove
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import ReactApexChart from 'react-apexcharts';
import { portfolioApi, stockApi } from '../utils/api';
import { CHART_COLORS } from '../utils/constants';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// TabPanel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Portfolio = () => {
  const { t } = useTranslation();
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [portfolioDialogOpen, setPortfolioDialogOpen] = useState(false);
  const [stockDialogOpen, setStockDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [stocks, setStocks] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  
  const [portfolioForm, setPortfolioForm] = useState({
    name: '',
    description: ''
  });
  
  const [stockForm, setStockForm] = useState({
    stock_id: '',
    quantity: 0,
    purchase_price: 0,
    purchase_date: new Date()
  });

  // Fetch portfolios on component mount
  useEffect(() => {
    fetchPortfolios();
    fetchStocks();
  }, []);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const response = await portfolioApi.getAll();
      setPortfolios(response.data.data);
      
      if (response.data.data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(response.data.data[0]);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching portfolios:', error);
      setError(t('error_fetching_portfolios'));
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

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handlePortfolioSelect = (portfolio) => {
    setSelectedPortfolio(portfolio);
  };

  const handlePortfolioDialogOpen = (portfolio = null) => {
    if (portfolio) {
      setPortfolioForm({
        name: portfolio.name,
        description: portfolio.description
      });
      setEditMode(true);
      setCurrentItem(portfolio);
    } else {
      setPortfolioForm({
        name: '',
        description: ''
      });
      setEditMode(false);
      setCurrentItem(null);
    }
    setPortfolioDialogOpen(true);
  };

  const handlePortfolioDialogClose = () => {
    setPortfolioDialogOpen(false);
  };

  const handleStockDialogOpen = (stock = null) => {
    if (stock) {
      setStockForm({
        stock_id: stock.stock.id,
        quantity: stock.quantity,
        purchase_price: stock.purchase_price,
        purchase_date: new Date(stock.purchase_date)
      });
      setEditMode(true);
      setCurrentItem(stock);
    } else {
      setStockForm({
        stock_id: '',
        quantity: 0,
        purchase_price: 0,
        purchase_date: new Date()
      });
      setEditMode(false);
      setCurrentItem(null);
    }
    setStockDialogOpen(true);
  };

  const handleStockDialogClose = () => {
    setStockDialogOpen(false);
  };

  const handleDeleteDialogOpen = (item, type) => {
    setCurrentItem({ ...item, type });
    setDeleteDialogOpen(true);
  };

  const handleDeleteDialogClose = () => {
    setDeleteDialogOpen(false);
  };

  const handlePortfolioFormChange = (event) => {
    const { name, value } = event.target;
    setPortfolioForm({
      ...portfolioForm,
      [name]: value
    });
  };

  const handleStockFormChange = (event) => {
    const { name, value } = event.target;
    setStockForm({
      ...stockForm,
      [name]: value
    });
  };

  const handleStockSelect = (event, newValue) => {
    setStockForm({
      ...stockForm,
      stock_id: newValue ? newValue.id : ''
    });
  };

  const handleDateChange = (date) => {
    setStockForm({
      ...stockForm,
      purchase_date: date
    });
  };

  const handleSavePortfolio = async () => {
    try {
      if (editMode) {
        await portfolioApi.update(currentItem.id, portfolioForm);
      } else {
        await portfolioApi.create(portfolioForm);
      }
      
      fetchPortfolios();
      handlePortfolioDialogClose();
    } catch (error) {
      console.error('Error saving portfolio:', error);
      setError(t('error_saving_portfolio'));
    }
  };

  const handleSaveStock = async () => {
    try {
      if (!selectedPortfolio) return;
      
      if (editMode) {
        await portfolioApi.updateStock(selectedPortfolio.id, currentItem.id, stockForm);
      } else {
        await portfolioApi.addStock(selectedPortfolio.id, stockForm);
      }
      
      // Refresh the selected portfolio
      const response = await portfolioApi.getById(selectedPortfolio.id);
      setSelectedPortfolio(response.data.data);
      
      handleStockDialogClose();
    } catch (error) {
      console.error('Error saving stock:', error);
      setError(t('error_saving_stock'));
    }
  };

  const handleDelete = async () => {
    try {
      if (currentItem.type === 'portfolio') {
        await portfolioApi.delete(currentItem.id);
        fetchPortfolios();
        if (selectedPortfolio && selectedPortfolio.id === currentItem.id) {
          setSelectedPortfolio(null);
        }
      } else if (currentItem.type === 'stock') {
        await portfolioApi.removeStock(selectedPortfolio.id, currentItem.id);
        // Refresh the selected portfolio
        const response = await portfolioApi.getById(selectedPortfolio.id);
        setSelectedPortfolio(response.data.data);
      }
      
      handleDeleteDialogClose();
    } catch (error) {
      console.error('Error deleting item:', error);
      setError(t('error_deleting_item'));
    }
  };

  // Calculate portfolio performance
  const calculatePerformance = () => {
    if (!selectedPortfolio || !selectedPortfolio.stocks || selectedPortfolio.stocks.length === 0) {
      return {
        totalInvestment: 0,
        currentValue: 0,
        profitLoss: 0,
        profitLossPercent: 0
      };
    }
    
    const totalInvestment = selectedPortfolio.stocks.reduce(
      (sum, stock) => sum + (stock.purchase_price * stock.quantity),
      0
    );
    
    const currentValue = selectedPortfolio.stocks.reduce(
      (sum, stock) => sum + (stock.current_price * stock.quantity),
      0
    );
    
    const profitLoss = currentValue - totalInvestment;
    const profitLossPercent = (profitLoss / totalInvestment) * 100;
    
    return {
      totalInvestment,
      currentValue,
      profitLoss,
      profitLossPercent
    };
  };

  const performance = calculatePerformance();

  // Prepare chart options and series for portfolio composition
  const compositionChartOptions = {
    chart: {
      type: 'pie',
      height: 350,
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    labels: selectedPortfolio?.stocks?.map(stock => stock.stock.name) || [],
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 200
        },
        legend: {
          position: 'bottom'
        }
      }
    }],
    legend: {
      position: 'bottom',
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    tooltip: {
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    },
    colors: [
      CHART_COLORS.primary,
      CHART_COLORS.secondary,
      CHART_COLORS.success,
      CHART_COLORS.warning,
      CHART_COLORS.info,
      CHART_COLORS.error,
      '#795548',
      '#607d8b',
      '#9c27b0',
      '#673ab7'
    ]
  };

  const compositionChartSeries = selectedPortfolio?.stocks?.map(stock => stock.current_price * stock.quantity) || [];

  // Prepare chart options and series for portfolio performance
  const performanceChartOptions = {
    chart: {
      type: 'area',
      height: 350,
      toolbar: {
        show: false
      },
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 2
    },
    xaxis: {
      type: 'datetime',
      categories: selectedPortfolio?.performance?.dates || [],
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    yaxis: {
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        },
        formatter: function (value) {
          return value.toFixed(2) + ' ' + t('sar');
        }
      }
    },
    tooltip: {
      x: {
        format: 'dd MMM yyyy'
      },
      y: {
        formatter: function (value) {
          return value.toFixed(2) + ' ' + t('sar');
        }
      },
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.7,
        opacityTo: 0.3,
        stops: [0, 90, 100]
      }
    },
    colors: [performance.profitLoss >= 0 ? CHART_COLORS.success : CHART_COLORS.error]
  };

  const performanceChartSeries = [{
    name: t('portfolio_value'),
    data: selectedPortfolio?.performance?.values || []
  }];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('portfolio')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handlePortfolioDialogOpen()}
        >
          {t('create_portfolio')}
        </Button>
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
          {/* Portfolio List */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                {t('my_portfolios')}
              </Typography>
              {portfolios.length > 0 ? (
                <List>
                  {portfolios.map((portfolio) => (
                    <ListItem
                      key={portfolio.id}
                      button
                      selected={selectedPortfolio && selectedPortfolio.id === portfolio.id}
                      onClick={() => handlePortfolioSelect(portfolio)}
                      secondaryAction={
                        <Box>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={(e) => {
                              e.stopPropagation();
                              handlePortfolioDialogOpen(portfolio);
                            }}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDialogOpen(portfolio, 'portfolio');
                            }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={portfolio.name}
                        secondary={
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {portfolio.description}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_portfolios')}
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Portfolio Details */}
          <Grid item xs={12} md={9}>
            {selectedPortfolio ? (
              <Box>
                <Paper sx={{ p: 2, mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h5">
                      {selectedPortfolio.name}
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Add />}
                      onClick={() => handleStockDialogOpen()}
                    >
                      {t('add_stock')}
                    </Button>
                  </Box>
                  <Typography variant="body1" paragraph>
                    {selectedPortfolio.description}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            {t('total_investment')}
                          </Typography>
                          <Typography variant="h6">
                            {performance.totalInvestment.toFixed(2)} {t('sar')}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            {t('current_value')}
                          </Typography>
                          <Typography variant="h6">
                            {performance.currentValue.toFixed(2)} {t('sar')}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            {t('profit_loss')}
                          </Typography>
                          <Typography
                            variant="h6"
                            color={performance.profitLoss >= 0 ? 'success.main' : 'error.main'}
                          >
                            {performance.profitLoss >= 0 ? '+' : ''}
                            {performance.profitLoss.toFixed(2)} {t('sar')}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">
                            {t('profit_loss_percent')}
                          </Typography>
                          <Typography
                            variant="h6"
                            color={performance.profitLossPercent >= 0 ? 'success.main' : 'error.main'}
                          >
                            {performance.profitLossPercent >= 0 ? '+' : ''}
                            {performance.profitLossPercent.toFixed(2)}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Paper>

                <Box sx={{ width: '100%' }}>
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="portfolio tabs">
                      <Tab label={t('stocks')} id="tab-0" />
                      <Tab label={t('performance')} id="tab-1" />
                      <Tab label={t('composition')} id="tab-2" />
                    </Tabs>
                  </Box>

                  {/* Stocks Tab */}
                  <TabPanel value={tabValue} index={0}>
                    {selectedPortfolio.stocks && selectedPortfolio.stocks.length > 0 ? (
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>{t('stock')}</TableCell>
                              <TableCell align="right">{t('quantity')}</TableCell>
                              <TableCell align="right">{t('purchase_price')}</TableCell>
                              <TableCell align="right">{t('purchase_date')}</TableCell>
                              <TableCell align="right">{t('current_price')}</TableCell>
                              <TableCell align="right">{t('current_value')}</TableCell>
                              <TableCell align="right">{t('profit_loss')}</TableCell>
                              <TableCell align="right">{t('actions')}</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {selectedPortfolio.stocks.map((stock) => {
                              const purchaseValue = stock.purchase_price * stock.quantity;
                              const currentValue = stock.current_price * stock.quantity;
                              const profitLoss = currentValue - purchaseValue;
                              const profitLossPercent = (profitLoss / purchaseValue) * 100;
                              
                              return (
                                <TableRow key={stock.id}>
                                  <TableCell component="th" scope="row">
                                    {stock.stock.name} ({stock.stock.symbol})
                                  </TableCell>
                                  <TableCell align="right">{stock.quantity}</TableCell>
                                  <TableCell align="right">{stock.purchase_price.toFixed(2)}</TableCell>
                                  <TableCell align="right">
                                    {new Date(stock.purchase_date).toLocaleDateString()}
                                  </TableCell>
                                  <TableCell align="right">{stock.current_price.toFixed(2)}</TableCell>
                                  <TableCell align="right">{currentValue.toFixed(2)}</TableCell>
                                  <TableCell align="right">
                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                                      <Typography
                                        color={profitLoss >= 0 ? 'success.main' : 'error.main'}
                                      >
                                        {profitLoss >= 0 ? '+' : ''}
                                        {profitLoss.toFixed(2)} ({profitLossPercent.toFixed(2)}%)
                                      </Typography>
                                      {profitLoss > 0 ? (
                                        <ArrowUpward color="success" fontSize="small" sx={{ ml: 0.5 }} />
                                      ) : profitLoss < 0 ? (
                                        <ArrowDownward color="error" fontSize="small" sx={{ ml: 0.5 }} />
                                      ) : (
                                        <Remove fontSize="small" sx={{ ml: 0.5 }} />
                                      )}
                                    </Box>
                                  </TableCell>
                                  <TableCell align="right">
                                    <IconButton
                                      size="small"
                                      onClick={() => handleStockDialogOpen(stock)}
                                    >
                                      <Edit fontSize="small" />
                                    </IconButton>
                                    <IconButton
                                      size="small"
                                      onClick={() => handleDeleteDialogOpen(stock, 'stock')}
                                    >
                                      <Delete fontSize="small" />
                                    </IconButton>
                                  </TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Typography variant="body1" align="center" sx={{ py: 3 }}>
                        {t('no_stocks_in_portfolio')}
                      </Typography>
                    )}
                  </TabPanel>

                  {/* Performance Tab */}
                  <TabPanel value={tabValue} index={1}>
                    <Card>
                      <CardHeader title={t('portfolio_performance')} />
                      <CardContent>
                        {selectedPortfolio.performance && selectedPortfolio.performance.dates.length > 0 ? (
                          <ReactApexChart
                            options={performanceChartOptions}
                            series={performanceChartSeries}
                            type="area"
                            height={350}
                          />
                        ) : (
                          <Typography variant="body1" align="center" sx={{ py: 3 }}>
                            {t('no_performance_data')}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </TabPanel>

                  {/* Composition Tab */}
                  <TabPanel value={tabValue} index={2}>
                    <Card>
                      <CardHeader title={t('portfolio_composition')} />
                      <CardContent>
                        {selectedPortfolio.stocks && selectedPortfolio.stocks.length > 0 ? (
                          <ReactApexChart
                            options={compositionChartOptions}
                            series={compositionChartSeries}
                            type="pie"
                            height={350}
                          />
                        ) : (
                          <Typography variant="body1" align="center" sx={{ py: 3 }}>
                            {t('no_stocks_in_portfolio')}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </TabPanel>
                </Box>
              </Box>
            ) : (
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  {t('no_portfolio_selected')}
                </Typography>
                <Typography variant="body1" paragraph>
                  {t('select_or_create_portfolio')}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => handlePortfolioDialogOpen()}
                >
                  {t('create_portfolio')}
                </Button>
              </Paper>
            )}
          </Grid>
        </Grid>
      )}

      {/* Portfolio Dialog */}
      <Dialog open={portfolioDialogOpen} onClose={handlePortfolioDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {editMode ? t('edit_portfolio') : t('create_portfolio')}
            <IconButton onClick={handlePortfolioDialogClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('portfolio_name')}
                name="name"
                value={portfolioForm.name}
                onChange={handlePortfolioFormChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('portfolio_description')}
                name="description"
                value={portfolioForm.description}
                onChange={handlePortfolioFormChange}
                multiline
                rows={4}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handlePortfolioDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleSavePortfolio} variant="contained">
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Stock Dialog */}
      <Dialog open={stockDialogOpen} onClose={handleStockDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {editMode ? t('edit_stock') : t('add_stock')}
            <IconButton onClick={handleStockDialogClose}>
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
                value={stocks.find(stock => stock.id === stockForm.stock_id) || null}
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
              <TextField
                fullWidth
                label={t('quantity')}
                name="quantity"
                type="number"
                value={stockForm.quantity}
                onChange={handleStockFormChange}
                InputProps={{
                  inputProps: { min: 1 }
                }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('purchase_price')}
                name="purchase_price"
                type="number"
                value={stockForm.purchase_price}
                onChange={handleStockFormChange}
                InputProps={{
                  inputProps: { min: 0, step: 0.01 }
                }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label={t('purchase_date')}
                  value={stockForm.purchase_date}
                  onChange={handleDateChange}
                  renderInput={(params) => <TextField {...params} fullWidth required />}
                />
              </LocalizationProvider>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleStockDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleSaveStock} variant="contained">
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteDialogClose}>
        <DialogTitle>{t('confirm_delete')}</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            {currentItem?.type === 'portfolio'
              ? t('confirm_delete_portfolio')
              : t('confirm_delete_stock')}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteDialogClose}>{t('cancel')}</Button>
          <Button onClick={handleDelete} color="error">
            {t('delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Portfolio;