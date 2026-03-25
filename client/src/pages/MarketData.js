import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

// Charts
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Redux actions
import { fetchMarketData, setSymbols, clearMarketData } from '../store/slices/marketSlice';

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

// Mock data for market index
const marketIndexData = [
  { date: '2025-01-01', value: 10500 },
  { date: '2025-01-02', value: 10550 },
  { date: '2025-01-03', value: 10600 },
  { date: '2025-01-04', value: 10580 },
  { date: '2025-01-05', value: 10620 },
  { date: '2025-01-06', value: 10700 },
  { date: '2025-01-07', value: 10750 },
  { date: '2025-01-08', value: 10800 },
  { date: '2025-01-09', value: 10780 },
  { date: '2025-01-10', value: 10850 },
  { date: '2025-01-11', value: 10900 },
  { date: '2025-01-12', value: 10950 },
  { date: '2025-01-13', value: 11000 },
  { date: '2025-01-14', value: 11050 },
];

// Static fallback for sector distribution (overridden by API when loaded)
const DEFAULT_SECTOR_DATA = [
  { name: 'البنوك', value: 35 },
  { name: 'الطاقة', value: 25 },
  { name: 'الاتصالات', value: 15 },
  { name: 'العقارات', value: 10 },
  { name: 'التأمين', value: 8 },
  { name: 'أخرى', value: 7 },
];

// Mock data for market volume
const marketVolumeData = [
  { date: '2025-01-01', value: 150000000 },
  { date: '2025-01-02', value: 160000000 },
  { date: '2025-01-03', value: 155000000 },
  { date: '2025-01-04', value: 165000000 },
  { date: '2025-01-05', value: 170000000 },
  { date: '2025-01-06', value: 180000000 },
  { date: '2025-01-07', value: 175000000 },
  { date: '2025-01-08', value: 185000000 },
  { date: '2025-01-09', value: 190000000 },
  { date: '2025-01-10', value: 195000000 },
  { date: '2025-01-11', value: 200000000 },
  { date: '2025-01-12', value: 205000000 },
  { date: '2025-01-13', value: 210000000 },
  { date: '2025-01-14', value: 215000000 },
];

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`market-tabpanel-${index}`}
      aria-labelledby={`market-tab-${index}`}
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

const MarketData = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const {
    symbols,
    data,
    collectionDate,
    status,
    error
  } = useSelector((state) => state.market);
  
  // Local state
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [dataType, setDataType] = useState('price');
  const [timeRange, setTimeRange] = useState('1w');
  const [tabValue, setTabValue] = useState(0);
  const [sectorDistributionData, setSectorDistributionData] = useState(DEFAULT_SECTOR_DATA);
  const sectorFetched = useRef(false);
  
  // Data type options
  const dataTypeOptions = [
    { value: 'price', label: 'السعر' },
    { value: 'volume', label: 'الحجم' },
    { value: 'market_cap', label: 'القيمة السوقية' },
    { value: 'pe', label: 'مضاعف الربحية' },
    { value: 'dividend_yield', label: 'عائد التوزيعات' }
  ];
  
  // Time range options
  const timeRangeOptions = [
    { value: '1d', label: 'يوم واحد' },
    { value: '1w', label: 'أسبوع' },
    { value: '1m', label: 'شهر' },
    { value: '3m', label: 'ثلاثة أشهر' },
    { value: '6m', label: 'ستة أشهر' },
    { value: '1y', label: 'سنة' },
    { value: '5y', label: 'خمس سنوات' }
  ];
  
  // Handle form changes
  const handleStocksChange = (event, newValue) => {
    setSelectedStocks(newValue);
  };
  
  const handleDataTypeChange = (event) => {
    setDataType(event.target.value);
  };
  
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Fetch market data
  const fetchData = () => {
    if (selectedStocks.length > 0) {
      dispatch(fetchMarketData({
        symbols: selectedStocks.map(stock => stock.symbol),
        dataTypes: [dataType]
      }));
    }
  };
  
  // Fetch sector data from API
  useEffect(() => {
    if (sectorFetched.current) return;
    sectorFetched.current = true;
    axios.get('/api/v1/market/sectors').then((res) => {
      const sectors = Array.isArray(res.data)
        ? res.data
        : res.data?.data ?? res.data?.sectors ?? [];
      if (sectors.length > 0) {
        setSectorDistributionData(
          sectors.map((s) => ({ name: s.name, value: Math.abs(s.change_percent ?? 0) || 1 }))
        );
      }
    }).catch(() => {});
  }, []);

  // Set initial stocks
  useEffect(() => {
    if (selectedStocks.length === 0 && stockSymbols.length > 0) {
      const initialStocks = [
        stockSymbols.find(s => s.symbol === '2222.SR'),
        stockSymbols.find(s => s.symbol === '1211.SR')
      ].filter(Boolean);
      
      setSelectedStocks(initialStocks);
    }
  }, [selectedStocks]);
  
  // Fetch data when component mounts
  useEffect(() => {
    if (status === 'idle' && selectedStocks.length > 0) {
      fetchData();
    }
  }, [status, selectedStocks, dispatch]);
  
  // Clear data on unmount
  useEffect(() => {
    return () => {
      dispatch(clearMarketData());
    };
  }, [dispatch]);
  
  // Generate colors for pie chart
  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
    theme.palette.info.main
  ];
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('market.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Market Overview */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="نظرة عامة على السوق" 
              titleTypographyProps={{ variant: 'h6' }}
              subheader={`آخر تحديث: ${new Date().toLocaleDateString('ar-SA')}`}
            />
            <Divider />
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="market data tabs">
                  <Tab label="مؤشر السوق" />
                  <Tab label="توزيع القطاعات" />
                  <Tab label="حجم التداول" />
                </Tabs>
              </Box>
              
              {/* Market Index Tab */}
              <TabPanel value={tabValue} index={0}>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={marketIndexData}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke={theme.palette.primary.main} 
                        fill={theme.palette.primary.light} 
                        name="مؤشر السوق"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </TabPanel>
              
              {/* Sector Distribution Tab */}
              <TabPanel value={tabValue} index={1}>
                <Box sx={{ height: 400, display: 'flex', justifyContent: 'center' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sectorDistributionData}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={150}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {sectorDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </TabPanel>
              
              {/* Market Volume Tab */}
              <TabPanel value={tabValue} index={2}>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={marketVolumeData}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke={theme.palette.secondary.main} 
                        fill={theme.palette.secondary.light} 
                        name="حجم التداول"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </TabPanel>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Stock Comparison */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="مقارنة الأسهم" 
              titleTypographyProps={{ variant: 'h6' }}
              action={
                <IconButton onClick={fetchData}>
                  <RefreshIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Autocomplete
                    multiple
                    id="stocks-select"
                    options={stockSymbols}
                    getOptionLabel={(option) => `${option.name} (${option.symbol})`}
                    value={selectedStocks}
                    onChange={handleStocksChange}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="اختر الأسهم للمقارنة"
                        variant="outlined"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="data-type-label">
                      نوع البيانات
                    </InputLabel>
                    <Select
                      labelId="data-type-label"
                      id="data-type"
                      value={dataType}
                      label="نوع البيانات"
                      onChange={handleDataTypeChange}
                    >
                      {dataTypeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="time-range-label">
                      النطاق الزمني
                    </InputLabel>
                    <Select
                      labelId="time-range-label"
                      id="time-range"
                      value={timeRange}
                      label="النطاق الزمني"
                      onChange={handleTimeRangeChange}
                    >
                      {timeRangeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={fetchData}
                      startIcon={<FilterIcon />}
                    >
                      تطبيق
                    </Button>
                  </Box>
                </Grid>
              </Grid>
              
              {/* Comparison Chart */}
              <Box sx={{ mt: 4, height: 400 }}>
                {status === 'loading' ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                    <CircularProgress />
                  </Box>
                ) : status === 'failed' ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error || 'حدث خطأ أثناء جلب بيانات السوق'}
                  </Alert>
                ) : status === 'succeeded' && Object.keys(data).length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      {selectedStocks.map((stock, index) => (
                        <Line
                          key={stock.symbol}
                          type="monotone"
                          dataKey="value"
                          data={data[stock.symbol]?.[dataType] || []}
                          name={`${stock.name} (${stock.symbol})`}
                          stroke={COLORS[index % COLORS.length]}
                          activeDot={{ r: 8 }}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <Alert severity="info">
                    اختر الأسهم ونوع البيانات والنطاق الزمني ثم اضغط على "تطبيق" لعرض البيانات.
                  </Alert>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Market Data Table */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="جدول بيانات السوق" 
              titleTypographyProps={{ variant: 'h6' }}
              subheader={collectionDate ? `تاريخ البيانات: ${collectionDate}` : ''}
            />
            <Divider />
            <CardContent>
              {status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : status === 'failed' ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error || 'حدث خطأ أثناء جلب بيانات السوق'}
                </Alert>
              ) : status === 'succeeded' && Object.keys(data).length > 0 ? (
                <TableContainer component={Paper} sx={{ mt: 2 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>الرمز</TableCell>
                        <TableCell>الاسم</TableCell>
                        <TableCell>السعر الحالي</TableCell>
                        <TableCell>التغير</TableCell>
                        <TableCell>نسبة التغير</TableCell>
                        <TableCell>الحجم</TableCell>
                        <TableCell>القيمة السوقية</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(data).map(([symbol, stockData]) => {
                        const stock = stockSymbols.find(s => s.symbol === symbol);
                        // API returns flat format: {price, change, change_percent, volume, value}
                        const price = parseFloat(stockData.price ?? 0);
                        const change = parseFloat(stockData.change ?? 0);
                        const changePercent = parseFloat(stockData.change_percent ?? 0);
                        const volume = parseFloat(stockData.volume ?? 0);
                        const marketCap = parseFloat(stockData.value ?? 0);
                        
                        return (
                          <TableRow key={symbol}>
                            <TableCell>{symbol}</TableCell>
                            <TableCell>{stock?.name || ''}</TableCell>
                            <TableCell>{price.toFixed(2)} ريال</TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                {change >= 0 ? (
                                  <ArrowUpIcon fontSize="small" color="success" />
                                ) : (
                                  <ArrowDownIcon fontSize="small" color="error" />
                                )}
                                {Math.abs(change).toFixed(2)} ريال
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={`${changePercent.toFixed(2)}%`}
                                color={changePercent >= 0 ? 'success' : 'error'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{volume.toLocaleString()} سهم</TableCell>
                            <TableCell>{marketCap.toLocaleString()} ريال</TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  لا توجد بيانات متاحة. يرجى اختيار الأسهم وتطبيق الفلتر.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketData;
