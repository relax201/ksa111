import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  TextField,
  Autocomplete,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  CardHeader,
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
  TrendingUp,
  TrendingDown,
  Info
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import ReactApexChart from 'react-apexcharts';
import { stockApi, fundamentalApi } from '../utils/api';
import { CHART_COLORS } from '../utils/constants';

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

const FundamentalAnalysis = () => {
  const { t } = useTranslation();
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [ratios, setRatios] = useState(null);
  const [valuation, setValuation] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [peerComparison, setPeerComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  // Fetch stocks on component mount
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await stockApi.getAll();
        setStocks(response.data.data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
        setError(t('error_fetching_stocks'));
      }
    };

    fetchStocks();
  }, [t]);

  // Fetch fundamental data when stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchFundamentalData();
    }
  }, [selectedStock]);

  const fetchFundamentalData = async () => {
    if (!selectedStock) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch company profile
      const profileResponse = await stockApi.getBySymbol(selectedStock.symbol);
      setCompanyProfile(profileResponse.data.data);

      // Fetch financial ratios
      const ratiosResponse = await fundamentalApi.getRatios(selectedStock.symbol);
      setRatios(ratiosResponse.data.data);

      // Fetch valuation metrics
      const valuationResponse = await fundamentalApi.getValuation(selectedStock.symbol);
      setValuation(valuationResponse.data.data);

      // Fetch growth metrics
      const growthResponse = await fundamentalApi.getGrowth(selectedStock.symbol);
      setGrowth(growthResponse.data.data);

      // Fetch peer comparison
      const peerResponse = await fundamentalApi.getPeerComparison(selectedStock.symbol);
      setPeerComparison(peerResponse.data.data);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching fundamental data:', error);
      setError(t('error_fetching_fundamental_data'));
      setLoading(false);
    }
  };

  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Prepare chart options and series for financial metrics
  const financialChartOptions = {
    chart: {
      type: 'bar',
      height: 350,
      toolbar: {
        show: false
      },
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
        endingShape: 'rounded'
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    xaxis: {
      categories: growth ? growth.years : [],
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    yaxis: {
      title: {
        text: t('amount_in_millions'),
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      },
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    fill: {
      opacity: 1
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return val.toFixed(2) + " " + t('million_sar');
        }
      },
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    },
    colors: [CHART_COLORS.primary, CHART_COLORS.success, CHART_COLORS.warning]
  };

  // Financial metrics chart series
  const financialChartSeries = growth ? [
    {
      name: t('revenue'),
      data: growth.revenue
    },
    {
      name: t('net_income'),
      data: growth.net_income
    },
    {
      name: t('operating_income'),
      data: growth.operating_income
    }
  ] : [];

  // Prepare chart options and series for peer comparison
  const peerChartOptions = {
    chart: {
      type: 'radar',
      height: 350,
      toolbar: {
        show: false
      },
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    xaxis: {
      categories: peerComparison ? [
        t('pe_ratio'),
        t('pb_ratio'),
        t('roe'),
        t('roa'),
        t('dividend_yield'),
        t('debt_to_equity')
      ] : [],
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
        }
      }
    },
    fill: {
      opacity: 0.5
    },
    markers: {
      size: 4
    },
    tooltip: {
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    },
    colors: [CHART_COLORS.primary, CHART_COLORS.secondary, CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.info]
  };

  // Peer comparison chart series
  const peerChartSeries = peerComparison ? peerComparison.companies.map(company => ({
    name: company.name,
    data: [
      company.pe_ratio,
      company.pb_ratio,
      company.roe,
      company.roa,
      company.dividend_yield,
      company.debt_to_equity
    ]
  })) : [];

  // Calculate valuation metrics
  const calculateValuationStatus = (metric, value, benchmark) => {
    if (!value || !benchmark) return 'neutral';
    
    // For metrics where lower is better (P/E, P/B, Debt/Equity)
    if (['pe_ratio', 'pb_ratio', 'debt_to_equity'].includes(metric)) {
      if (value < benchmark * 0.8) return 'undervalued';
      if (value > benchmark * 1.2) return 'overvalued';
      return 'fair_valued';
    }
    
    // For metrics where higher is better (ROE, ROA, Dividend Yield)
    if (['roe', 'roa', 'dividend_yield'].includes(metric)) {
      if (value > benchmark * 1.2) return 'undervalued';
      if (value < benchmark * 0.8) return 'overvalued';
      return 'fair_valued';
    }
    
    return 'neutral';
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('fundamental_analysis')}
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Autocomplete
              options={stocks}
              getOptionLabel={(option) => `${option.name} (${option.symbol})`}
              value={selectedStock}
              onChange={handleStockChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('select_stock')}
                  variant="outlined"
                  fullWidth
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              variant="contained"
              color="primary"
              onClick={fetchFundamentalData}
              disabled={!selectedStock || loading}
            >
              {loading ? <CircularProgress size={24} /> : t('analyze')}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {selectedStock && companyProfile && (
        <>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h5" gutterBottom>
                  {companyProfile.name} ({companyProfile.symbol})
                </Typography>
                <Typography variant="body1" paragraph>
                  {companyProfile.description}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('sector')}:
                    </Typography>
                    <Typography variant="body1">
                      {companyProfile.sector}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('industry')}:
                    </Typography>
                    <Typography variant="body1">
                      {companyProfile.industry}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('market_cap')}:
                    </Typography>
                    <Typography variant="body1">
                      {(companyProfile.market_cap / 1000000).toFixed(2)} {t('million_sar')}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('employees')}:
                    </Typography>
                    <Typography variant="body1">
                      {companyProfile.employees.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('founded')}:
                    </Typography>
                    <Typography variant="body1">
                      {companyProfile.founded}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('ceo')}:
                    </Typography>
                    <Typography variant="body1">
                      {companyProfile.ceo}
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title={t('key_metrics')} />
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('current_price')}:
                        </Typography>
                        <Typography variant="h6">
                          {companyProfile.price.toFixed(2)} {t('sar')}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('52_week_range')}:
                        </Typography>
                        <Typography variant="body1">
                          {companyProfile.fifty_two_week_low.toFixed(2)} - {companyProfile.fifty_two_week_high.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('pe_ratio')}:
                        </Typography>
                        <Typography variant="body1">
                          {companyProfile.pe_ratio ? companyProfile.pe_ratio.toFixed(2) : t('na')}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('eps')}:
                        </Typography>
                        <Typography variant="body1">
                          {companyProfile.eps ? companyProfile.eps.toFixed(2) : t('na')}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('dividend_yield')}:
                        </Typography>
                        <Typography variant="body1">
                          {companyProfile.dividend_yield ? (companyProfile.dividend_yield * 100).toFixed(2) + '%' : t('na')}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {t('beta')}:
                        </Typography>
                        <Typography variant="body1">
                          {companyProfile.beta ? companyProfile.beta.toFixed(2) : t('na')}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>

          <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="fundamental analysis tabs">
                <Tab label={t('financial_ratios')} id="tab-0" />
                <Tab label={t('valuation')} id="tab-1" />
                <Tab label={t('growth')} id="tab-2" />
                <Tab label={t('peer_comparison')} id="tab-3" />
              </Tabs>
            </Box>

            {/* Financial Ratios Tab */}
            <TabPanel value={tabValue} index={0}>
              {ratios ? (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>{t('ratio')}</TableCell>
                        <TableCell align="right">{t('value')}</TableCell>
                        <TableCell align="right">{t('sector_average')}</TableCell>
                        <TableCell align="right">{t('status')}</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(ratios.metrics).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell component="th" scope="row">
                            {t(key)}
                            <Tooltip title={t(`${key}_explanation`)}>
                              <Info fontSize="small" sx={{ ml: 1, verticalAlign: 'middle' }} />
                            </Tooltip>
                          </TableCell>
                          <TableCell align="right">
                            {typeof value === 'number' ? 
                              (key.includes('percent') || key.includes('yield') || key.includes('margin') || key.includes('roe') || key.includes('roa') ? 
                                (value * 100).toFixed(2) + '%' : 
                                value.toFixed(2)
                              ) : 
                              t('na')
                            }
                          </TableCell>
                          <TableCell align="right">
                            {typeof ratios.sector_average[key] === 'number' ? 
                              (key.includes('percent') || key.includes('yield') || key.includes('margin') || key.includes('roe') || key.includes('roa') ? 
                                (ratios.sector_average[key] * 100).toFixed(2) + '%' : 
                                ratios.sector_average[key].toFixed(2)
                              ) : 
                              t('na')
                            }
                          </TableCell>
                          <TableCell align="right">
                            {typeof value === 'number' && typeof ratios.sector_average[key] === 'number' ? (
                              <Typography
                                color={
                                  calculateValuationStatus(key, value, ratios.sector_average[key]) === 'undervalued' ? 
                                    'success.main' : 
                                    calculateValuationStatus(key, value, ratios.sector_average[key]) === 'overvalued' ? 
                                      'error.main' : 
                                      'text.primary'
                                }
                              >
                                {t(calculateValuationStatus(key, value, ratios.sector_average[key]))}
                              </Typography>
                            ) : (
                              t('na')
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_ratio_data')}
                </Typography>
              )}
            </TabPanel>

            {/* Valuation Tab */}
            <TabPanel value={tabValue} index={1}>
              {valuation ? (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardHeader title={t('valuation_metrics')} />
                      <CardContent>
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>{t('metric')}</TableCell>
                                <TableCell align="right">{t('value')}</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.entries(valuation.metrics).map(([key, value]) => (
                                <TableRow key={key}>
                                  <TableCell component="th" scope="row">
                                    {t(key)}
                                    <Tooltip title={t(`${key}_explanation`)}>
                                      <Info fontSize="small" sx={{ ml: 1, verticalAlign: 'middle' }} />
                                    </Tooltip>
                                  </TableCell>
                                  <TableCell align="right">
                                    {typeof value === 'number' ? 
                                      (key.includes('percent') || key.includes('yield') || key.includes('margin') ? 
                                        (value * 100).toFixed(2) + '%' : 
                                        value.toFixed(2)
                                      ) : 
                                      t('na')
                                    }
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardHeader title={t('valuation_summary')} />
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {t('fair_value_estimate')}: {valuation.fair_value.toFixed(2)} {t('sar')}
                        </Typography>
                        <Typography variant="body1" paragraph>
                          {t('current_price')}: {companyProfile.price.toFixed(2)} {t('sar')}
                        </Typography>
                        <Typography 
                          variant="body1" 
                          color={
                            companyProfile.price < valuation.fair_value * 0.9 ? 
                              'success.main' : 
                              companyProfile.price > valuation.fair_value * 1.1 ? 
                                'error.main' : 
                                'text.primary'
                          }
                          paragraph
                        >
                          {companyProfile.price < valuation.fair_value * 0.9 ? 
                            t('undervalued_by') : 
                            companyProfile.price > valuation.fair_value * 1.1 ? 
                              t('overvalued_by') : 
                              t('fairly_valued')}
                          {' '}
                          {companyProfile.price !== valuation.fair_value ? 
                            Math.abs(((companyProfile.price - valuation.fair_value) / valuation.fair_value) * 100).toFixed(2) + '%' : 
                            ''}
                        </Typography>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="body1" paragraph>
                          {valuation.analysis}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_valuation_data')}
                </Typography>
              )}
            </TabPanel>

            {/* Growth Tab */}
            <TabPanel value={tabValue} index={2}>
              {growth ? (
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Card>
                      <CardHeader title={t('financial_growth')} />
                      <CardContent>
                        <ReactApexChart
                          options={financialChartOptions}
                          series={financialChartSeries}
                          type="bar"
                          height={350}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12}>
                    <Card>
                      <CardHeader title={t('growth_rates')} />
                      <CardContent>
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>{t('metric')}</TableCell>
                                <TableCell align="right">{t('1_year')}</TableCell>
                                <TableCell align="right">{t('3_year')}</TableCell>
                                <TableCell align="right">{t('5_year')}</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.entries(growth.growth_rates).map(([key, rates]) => (
                                <TableRow key={key}>
                                  <TableCell component="th" scope="row">
                                    {t(key)}
                                  </TableCell>
                                  <TableCell align="right">
                                    <Typography
                                      color={rates.one_year > 0 ? 'success.main' : rates.one_year < 0 ? 'error.main' : 'text.primary'}
                                    >
                                      {(rates.one_year * 100).toFixed(2)}%
                                      {rates.one_year > 0 ? <TrendingUp fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : 
                                       rates.one_year < 0 ? <TrendingDown fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : null}
                                    </Typography>
                                  </TableCell>
                                  <TableCell align="right">
                                    <Typography
                                      color={rates.three_year > 0 ? 'success.main' : rates.three_year < 0 ? 'error.main' : 'text.primary'}
                                    >
                                      {(rates.three_year * 100).toFixed(2)}%
                                      {rates.three_year > 0 ? <TrendingUp fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : 
                                       rates.three_year < 0 ? <TrendingDown fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : null}
                                    </Typography>
                                  </TableCell>
                                  <TableCell align="right">
                                    <Typography
                                      color={rates.five_year > 0 ? 'success.main' : rates.five_year < 0 ? 'error.main' : 'text.primary'}
                                    >
                                      {(rates.five_year * 100).toFixed(2)}%
                                      {rates.five_year > 0 ? <TrendingUp fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : 
                                       rates.five_year < 0 ? <TrendingDown fontSize="small" sx={{ ml: 0.5, verticalAlign: 'middle' }} /> : null}
                                    </Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_growth_data')}
                </Typography>
              )}
            </TabPanel>

            {/* Peer Comparison Tab */}
            <TabPanel value={tabValue} index={3}>
              {peerComparison ? (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardHeader title={t('peer_comparison_chart')} />
                      <CardContent>
                        <ReactApexChart
                          options={peerChartOptions}
                          series={peerChartSeries}
                          type="radar"
                          height={350}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardHeader title={t('peer_comparison_table')} />
                      <CardContent>
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>{t('company')}</TableCell>
                                <TableCell align="right">{t('price')}</TableCell>
                                <TableCell align="right">{t('market_cap')}</TableCell>
                                <TableCell align="right">{t('pe_ratio')}</TableCell>
                                <TableCell align="right">{t('roe')}</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {peerComparison.companies.map((company) => (
                                <TableRow key={company.symbol}>
                                  <TableCell component="th" scope="row">
                                    {company.name}
                                  </TableCell>
                                  <TableCell align="right">
                                    {company.price.toFixed(2)}
                                  </TableCell>
                                  <TableCell align="right">
                                    {(company.market_cap / 1000000).toFixed(2)}M
                                  </TableCell>
                                  <TableCell align="right">
                                    {company.pe_ratio ? company.pe_ratio.toFixed(2) : t('na')}
                                  </TableCell>
                                  <TableCell align="right">
                                    {company.roe ? (company.roe * 100).toFixed(2) + '%' : t('na')}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body1" align="center" sx={{ py: 3 }}>
                  {t('no_peer_comparison_data')}
                </Typography>
              )}
            </TabPanel>
          </Box>
        </>
      )}
    </Box>
  );
};

export default FundamentalAnalysis;