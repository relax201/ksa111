import React, { useState, useEffect, useMemo } from 'react';
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
  TextField,
  Autocomplete,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Tabs,
  Tab,
  Rating,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Info as InfoIcon
} from '@mui/icons-material';

// Charts
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

// Redux actions
import { fetchFundamentalAnalysis, setSymbol, clearFundamentalAnalysis } from '../store/slices/fundamentalSlice';

// Mock stock symbols for search
const stockSymbols = [
  { symbol: '2222.SR', name: 'أرامكو السعودية' },
  { symbol: '1211.SR', name: 'معادن' },
  { symbol: '2010.SR', name: 'سابك' },
  { symbol: '1150.SR', name: 'الاتصالات السعودية' },
  { symbol: '1010.SR', name: 'الراجحي' },
  { symbol: '1050.SR', name: 'صافولا' },
  { symbol: '1120.SR', name: 'الراجحي للتأمين' },
  { symbol: '2350.SR', name: 'كيان السعودية' },
  { symbol: '2380.SR', name: 'بترو رابغ' },
  { symbol: '4261.SR', name: 'ثوب الأصيل' },
];

// Static fallbacks used when API data is not available
const FALLBACK_SECTOR_COMPARISON = [
  { metric: 'P/E', company: 15.2, sector: 18.5, market: 20.1 },
  { metric: 'P/B', company: 1.8, sector: 2.2, market: 2.5 },
  { metric: 'ROE', company: 12.5, sector: 10.2, market: 9.8 },
  { metric: 'ROA', company: 8.3, sector: 6.5, market: 5.9 },
  { metric: 'Debt/Equity', company: 0.45, sector: 0.62, market: 0.58 },
];

const FALLBACK_HEALTH_DATA = [
  { subject: 'الربحية', A: 85, fullMark: 100 },
  { subject: 'السيولة', A: 70, fullMark: 100 },
  { subject: 'الكفاءة', A: 65, fullMark: 100 },
  { subject: 'النمو', A: 90, fullMark: 100 },
  { subject: 'المديونية', A: 75, fullMark: 100 },
];

// Map metric key → score 0-100 using a simple clamped linear scale
function metricScore(value, lowBad = false) {
  if (value == null || isNaN(value)) return 50;
  const v = parseFloat(value);
  // For ratios like current_ratio: higher is better; for debt: lower is better
  const clamped = Math.max(0, Math.min(100, lowBad ? Math.max(0, 100 - v * 10) : Math.min(100, v * 5)));
  return Math.round(clamped);
}

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`fundamental-tabpanel-${index}`}
      aria-labelledby={`fundamental-tab-${index}`}
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
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const {
    symbol,
    name,
    metrics,
    analysisDate,
    valuation,
    sectorComparison,
    status,
    error
  } = useSelector((state) => state.fundamental);
  
  // Local state
  const [selectedStock, setSelectedStock] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  // Derive sector comparison data from Redux sectorComparison if available
  const sectorComparisonData = useMemo(() => {
    const entries = Object.entries(sectorComparison ?? {});
    if (entries.length === 0) return FALLBACK_SECTOR_COMPARISON;
    return entries.map(([metric, vals]) => ({
      metric,
      company: parseFloat(vals.company ?? 0),
      sector: parseFloat(vals.sector ?? 0),
      market: parseFloat(vals.market ?? 0),
    }));
  }, [sectorComparison]);

  // Derive financial health radar data from metrics if available
  const financialHealthData = useMemo(() => {
    if (!metrics || Object.keys(metrics).length === 0) return FALLBACK_HEALTH_DATA;
    const m = metrics;
    return [
      { subject: 'الربحية',  A: metricScore(m.ROE?.value ?? m.roe?.value),           fullMark: 100 },
      { subject: 'السيولة',  A: metricScore(m.current_ratio?.value ?? m.CR?.value),  fullMark: 100 },
      { subject: 'الكفاءة',  A: metricScore(m.ROA?.value ?? m.roa?.value),           fullMark: 100 },
      { subject: 'النمو',    A: metricScore(m.EPS?.value ?? m.eps?.value),           fullMark: 100 },
      { subject: 'المديونية', A: metricScore(m.debt_to_equity?.value ?? m.DE?.value, true), fullMark: 100 },
    ];
  }, [metrics]);
  
  // Handle stock selection
  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
    if (newValue) {
      dispatch(setSymbol(newValue.symbol));
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Analyze stock
  const analyzeStock = () => {
    if (selectedStock) {
      dispatch(fetchFundamentalAnalysis({
        symbol: selectedStock.symbol,
        metrics: ['PE', 'PB', 'ROE', 'ROA', 'EPS', 'DPS', 'BVPS', 'DebtToEquity']
      }));
    }
  };
  
  // Get valuation color
  const getValuationColor = (val) => {
    switch (val) {
      case 'مقيم بأقل من قيمته':
        return theme.palette.success.main;
      case 'مقيم بأعلى من قيمته':
        return theme.palette.error.main;
      default:
        return theme.palette.warning.main;
    }
  };
  
  // Get valuation icon
  const getValuationIcon = (val) => {
    switch (val) {
      case 'مقيم بأقل من قيمته':
        return <TrendingUpIcon />;
      case 'مقيم بأعلى من قيمته':
        return <TrendingDownIcon />;
      default:
        return <TrendingFlatIcon />;
    }
  };
  
  // Set initial stock
  useEffect(() => {
    if (!selectedStock && stockSymbols.length > 0) {
      const initialStock = stockSymbols.find(s => s.symbol === '2222.SR') || stockSymbols[0];
      setSelectedStock(initialStock);
      dispatch(setSymbol(initialStock.symbol));
    }
  }, [selectedStock, dispatch]);
  
  // Fetch analysis when symbol changes
  useEffect(() => {
    if (symbol && status === 'idle') {
      dispatch(fetchFundamentalAnalysis({
        symbol,
        metrics: ['PE', 'PB', 'ROE', 'ROA', 'EPS', 'DPS', 'BVPS', 'DebtToEquity']
      }));
    }
  }, [symbol, status, dispatch]);
  
  // Clear analysis on unmount
  useEffect(() => {
    return () => {
      dispatch(clearFundamentalAnalysis());
    };
  }, [dispatch]);
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('fundamental.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stock Selection */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="اختيار السهم" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={8}>
                  <Autocomplete
                    id="stock-select"
                    options={stockSymbols}
                    getOptionLabel={(option) => `${option.name} (${option.symbol})`}
                    value={selectedStock}
                    onChange={handleStockChange}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="اختر السهم"
                        variant="outlined"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={analyzeStock}
                    startIcon={<SearchIcon />}
                    sx={{ height: '56px' }}
                  >
                    تحليل
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Loading State */}
        {status === 'loading' && (
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
              <CircularProgress />
            </Box>
          </Grid>
        )}
        
        {/* Error State */}
        {status === 'failed' && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error || 'حدث خطأ أثناء جلب بيانات التحليل الأساسي'}
            </Alert>
          </Grid>
        )}
        
        {/* Analysis Results */}
        {status === 'succeeded' && (
          <>
            {/* Stock Overview */}
            <Grid item xs={12}>
              <Card>
                <CardHeader 
                  title={`${name} (${symbol})`}
                  titleTypographyProps={{ variant: 'h6' }}
                  subheader={analysisDate ? `تاريخ التحليل: ${analysisDate}` : ''}
                  action={
                    <Chip
                      icon={getValuationIcon(valuation)}
                      label={valuation}
                      sx={{
                        bgcolor: getValuationColor(valuation),
                        color: 'white',
                      }}
                    />
                  }
                />
                <Divider />
                <CardContent>
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="fundamental analysis tabs">
                      <Tab label="المؤشرات الأساسية" />
                      <Tab label="مقارنة القطاع" />
                      <Tab label="الصحة المالية" />
                    </Tabs>
                  </Box>
                  
                  {/* Key Metrics Tab */}
                  <TabPanel value={tabValue} index={0}>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <TableContainer component={Paper}>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>المؤشر</TableCell>
                                <TableCell>القيمة</TableCell>
                                <TableCell>التقييم</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {metrics && Object.entries(metrics).map(([key, metric]) => (
                                <TableRow key={key}>
                                  <TableCell>
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                      {key}
                                      <Tooltip title={metric.description || ''}>
                                        <InfoIcon fontSize="small" sx={{ ml: 1, color: 'text.secondary' }} />
                                      </Tooltip>
                                    </Box>
                                  </TableCell>
                                  <TableCell>{metric.value}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={metric.evaluation}
                                      size="small"
                                      sx={{
                                        bgcolor: 
                                          metric.evaluation === 'جيد' ? theme.palette.success.light :
                                          metric.evaluation === 'ضعيف' ? theme.palette.error.light :
                                          theme.palette.warning.light,
                                        color: 
                                          metric.evaluation === 'جيد' ? theme.palette.success.dark :
                                          metric.evaluation === 'ضعيف' ? theme.palette.error.dark :
                                          theme.palette.warning.dark,
                                      }}
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader 
                            title="تقييم المؤشرات الأساسية"
                            titleTypographyProps={{ variant: 'h6' }}
                          />
                          <Divider />
                          <CardContent>
                            <Box sx={{ height: 300 }}>
                              <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                  data={Object.entries(metrics || {}).map(([key, metric]) => ({
                                    name: key,
                                    value: parseFloat(metric.value),
                                    benchmark: parseFloat(metric.benchmark || 0),
                                  }))}
                                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                                >
                                  <CartesianGrid strokeDasharray="3 3" />
                                  <XAxis dataKey="name" />
                                  <YAxis />
                                  <RechartsTooltip />
                                  <Legend />
                                  <Bar dataKey="value" name="القيمة الحالية" fill={theme.palette.primary.main} />
                                  <Bar dataKey="benchmark" name="المعيار" fill={theme.palette.secondary.main} />
                                </BarChart>
                              </ResponsiveContainer>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </TabPanel>
                  
                  {/* Sector Comparison Tab */}
                  <TabPanel value={tabValue} index={1}>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <TableContainer component={Paper}>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>المؤشر</TableCell>
                                <TableCell>الشركة</TableCell>
                                <TableCell>القطاع</TableCell>
                                <TableCell>السوق</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {sectorComparisonData.map((row) => (
                                <TableRow key={row.metric}>
                                  <TableCell>{row.metric}</TableCell>
                                  <TableCell>{row.company}</TableCell>
                                  <TableCell>{row.sector}</TableCell>
                                  <TableCell>{row.market}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader 
                            title="مقارنة مع القطاع"
                            titleTypographyProps={{ variant: 'h6' }}
                          />
                          <Divider />
                          <CardContent>
                            <Box sx={{ height: 300 }}>
                              <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                  data={sectorComparisonData}
                                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                                >
                                  <CartesianGrid strokeDasharray="3 3" />
                                  <XAxis dataKey="metric" />
                                  <YAxis />
                                  <RechartsTooltip />
                                  <Legend />
                                  <Bar dataKey="company" name="الشركة" fill={theme.palette.primary.main} />
                                  <Bar dataKey="sector" name="القطاع" fill={theme.palette.secondary.main} />
                                  <Bar dataKey="market" name="السوق" fill={theme.palette.info.main} />
                                </BarChart>
                              </ResponsiveContainer>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </TabPanel>
                  
                  {/* Financial Health Tab */}
                  <TabPanel value={tabValue} index={2}>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader 
                            title="الصحة المالية"
                            titleTypographyProps={{ variant: 'h6' }}
                          />
                          <Divider />
                          <CardContent>
                            <Box sx={{ height: 300 }}>
                              <ResponsiveContainer width="100%" height="100%">
                                <RadarChart outerRadius={90} data={financialHealthData}>
                                  <PolarGrid />
                                  <PolarAngleAxis dataKey="subject" />
                                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                                  <Radar name="الشركة" dataKey="A" stroke={theme.palette.primary.main} fill={theme.palette.primary.main} fillOpacity={0.6} />
                                  <Legend />
                                </RadarChart>
                              </ResponsiveContainer>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader 
                            title="تقييم الصحة المالية"
                            titleTypographyProps={{ variant: 'h6' }}
                          />
                          <Divider />
                          <CardContent>
                            <Box>
                              {financialHealthData.map((item) => {
                                const score = item.A;
                                const color = score >= 80 ? 'success.main' : score >= 60 ? 'primary.main' : 'warning.main';
                                return (
                                  <Box key={item.subject} sx={{ width: '100%', mb: 2 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                      <Typography variant="body1">{item.subject}</Typography>
                                      <Typography variant="body2" color="text.secondary">{score}/100</Typography>
                                    </Box>
                                    <Box sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
                                      <Box sx={{ width: `${score}%`, height: 10, bgcolor: color, borderRadius: 1 }} />
                                    </Box>
                                  </Box>
                                );
                              })}
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </TabPanel>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

export default FundamentalAnalysis;
