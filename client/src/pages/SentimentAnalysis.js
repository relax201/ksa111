import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Article as ArticleIcon,
  Twitter as TwitterIcon,
  Person as PersonIcon
} from '@mui/icons-material';

// Charts
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
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
import { fetchSentimentAnalysis, setSymbols, clearSentimentAnalysis } from '../store/slices/sentimentSlice';

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

// No mock data — all data comes from the API via Redux

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`sentiment-tabpanel-${index}`}
      aria-labelledby={`sentiment-tab-${index}`}
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

const SentimentAnalysis = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const {
    symbols,
    sentiment,
    analysisDate,
    status,
    error
  } = useSelector((state) => state.sentiment);
  
  // Local state
  const [selectedStock, setSelectedStock] = useState(null);
  const [timeRange, setTimeRange] = useState('1w');
  const [sources, setSources] = useState(['news', 'social_media', 'analyst_ratings']);
  const [tabValue, setTabValue] = useState(0);
  
  // Time range options
  const timeRangeOptions = [
    { value: '1d', label: 'يوم واحد' },
    { value: '1w', label: 'أسبوع' },
    { value: '1m', label: 'شهر' },
    { value: '3m', label: 'ثلاثة أشهر' },
    { value: '6m', label: 'ستة أشهر' },
    { value: '1y', label: 'سنة' }
  ];
  
  // Source options
  const sourceOptions = [
    { value: 'news', label: 'الأخبار' },
    { value: 'social_media', label: 'وسائل التواصل الاجتماعي' },
    { value: 'analyst_ratings', label: 'تقييمات المحللين' }
  ];
  
  // Handle form changes
  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
  };
  
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };
  
  const handleSourcesChange = (event) => {
    setSources(event.target.value);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Fetch sentiment data
  const fetchData = () => {
    if (selectedStock) {
      dispatch(fetchSentimentAnalysis({
        symbols: [selectedStock.symbol],
        sources,
        timeRange
      }));
    }
  };
  
  // Set initial stock
  useEffect(() => {
    if (!selectedStock && stockSymbols.length > 0) {
      const initialStock = stockSymbols.find(s => s.symbol === '2222.SR') || stockSymbols[0];
      setSelectedStock(initialStock);
    }
  }, [selectedStock]);
  
  // Fetch data when selected stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStock]);
  
  // Clear data on unmount
  useEffect(() => {
    return () => {
      dispatch(clearSentimentAnalysis());
    };
  }, [dispatch]);
  
  // Get sentiment color
  const getSentimentColor = (value) => {
    if (value >= 0.7) {
      return theme.palette.success.main;
    } else if (value >= 0.4) {
      return theme.palette.warning.main;
    } else {
      return theme.palette.error.main;
    }
  };
  
  // Get sentiment label
  const getSentimentLabel = (value) => {
    if (value >= 0.7) {
      return 'إيجابي';
    } else if (value >= 0.4) {
      return 'محايد';
    } else {
      return 'سلبي';
    }
  };
  
  // Get sentiment icon
  const getSentimentIcon = (value) => {
    if (value >= 0.7) {
      return <TrendingUpIcon />;
    } else if (value >= 0.4) {
      return <TrendingFlatIcon />;
    } else {
      return <TrendingDownIcon />;
    }
  };
  
  // Generate colors for pie chart
  const COLORS = [
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main
  ];
  
  // Resolve current symbol's sentiment from Redux
  const currentSymbol = selectedStock ? selectedStock.symbol.replace('.SR', '') : null;
  const symbolSentiment = currentSymbol ? (sentiment?.[currentSymbol] ?? {}) : {};
  const newsSource = symbolSentiment?.sources?.news ?? {};
  const socialSource = symbolSentiment?.sources?.social_media ?? {};

  // Distribution: positive / neutral / negative ratios from API
  const getSentimentDistribution = () => {
    const pos = symbolSentiment?.positive_ratio ?? 0;
    const neg = symbolSentiment?.negative_ratio ?? 0;
    const neu = symbolSentiment?.neutral_ratio ?? 1;
    const total = pos + neg + neu || 1;
    return [
      { name: 'إيجابي', value: Math.round((pos / total) * 100) },
      { name: 'محايد',  value: Math.round((neu / total) * 100) },
      { name: 'سلبي',   value: Math.round((neg / total) * 100) },
    ];
  };

  // Trend: single point from overall score (expand to chart-compatible array)
  const getSentimentTrendData = () => {
    const overall = symbolSentiment?.overall;
    if (overall === undefined || overall === null) return [];
    return [{ date: analysisDate ?? new Date().toISOString().split('T')[0], value: overall }];
  };

  // Source comparison
  const getSourceComparisonData = () => {
    return [
      { name: 'الأخبار',         value: newsSource?.sentiment   ?? 0 },
      { name: 'وسائل التواصل',   value: socialSource?.sentiment ?? 0 },
    ];
  };

  // News items from API
  const getNewsItems = () => newsSource?.items ?? [];
  const getSocialPosts = () => socialSource?.items ?? [];
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('sentiment.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stock Selection */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="اختيار السهم ومصادر التحليل" 
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
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="sources-label">
                      مصادر التحليل
                    </InputLabel>
                    <Select
                      labelId="sources-label"
                      id="sources"
                      multiple
                      value={sources}
                      label="مصادر التحليل"
                      onChange={handleSourcesChange}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip 
                              key={value} 
                              label={sourceOptions.find(option => option.value === value)?.label} 
                              size="small" 
                            />
                          ))}
                        </Box>
                      )}
                    >
                      {sourceOptions.map((option) => (
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
                      تحليل
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sentiment Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title={selectedStock ? `تحليل المشاعر لـ ${selectedStock.name} (${selectedStock.symbol})` : 'تحليل المشاعر'}
              titleTypographyProps={{ variant: 'h6' }}
              subheader={analysisDate ? `تاريخ التحليل: ${analysisDate}` : ''}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 400 }}>
                {status === 'loading' ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                    <CircularProgress />
                  </Box>
                ) : status === 'failed' ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error || 'حدث خطأ أثناء جلب بيانات تحليل المشاعر'}
                  </Alert>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={getSentimentTrendData()}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis domain={[0, 1]} />
                      <RechartsTooltip 
                        formatter={(value) => [
                          `${(value * 100).toFixed(1)}%`, 
                          'مؤشر المشاعر'
                        ]} 
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        name="مؤشر المشاعر" 
                        stroke={theme.palette.primary.main} 
                        activeDot={{ r: 8 }} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sentiment Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader 
              title="توزيع المشاعر" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                {status === 'loading' ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                    <CircularProgress />
                  </Box>
                ) : status === 'failed' ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error || 'حدث خطأ أثناء جلب بيانات تحليل المشاعر'}
                  </Alert>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getSentimentDistribution()}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {getSentimentDistribution().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Source Comparison */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="مقارنة المصادر" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300 }}>
                {status === 'loading' ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                    <CircularProgress />
                  </Box>
                ) : status === 'failed' ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error || 'حدث خطأ أثناء جلب بيانات تحليل المشاعر'}
                  </Alert>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={getSourceComparisonData()}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis domain={[0, 1]} />
                      <RechartsTooltip 
                        formatter={(value) => [
                          `${(value * 100).toFixed(1)}%`, 
                          'مؤشر المشاعر'
                        ]} 
                      />
                      <Legend />
                      <Bar 
                        dataKey="value" 
                        name="مؤشر المشاعر" 
                        fill={theme.palette.primary.main} 
                      />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Detailed Sources */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="تفاصيل المصادر" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="sentiment sources tabs">
                  <Tab label="الأخبار" icon={<ArticleIcon />} iconPosition="start" />
                  <Tab label="وسائل التواصل" icon={<TwitterIcon />} iconPosition="start" />
                  <Tab label="تقييمات المحللين" icon={<PersonIcon />} iconPosition="start" />
                </Tabs>
              </Box>
              
              {/* News Tab */}
              <TabPanel value={tabValue} index={0}>
                {getNewsItems().length === 0 ? (
                  <Alert severity="info">لا توجد أخبار متاحة لهذا السهم حالياً</Alert>
                ) : (
                  <List>
                    {getNewsItems().map((item, idx) => (
                      <ListItem key={idx} divider>
                        <ListItemText
                          primary={item.title}
                          secondary={item.date ?? ''}
                        />
                        <Chip
                          icon={getSentimentIcon(item.sentiment)}
                          label={`${getSentimentLabel(item.sentiment)} (${((item.sentiment ?? 0) * 100).toFixed(0)}%)`}
                          sx={{ bgcolor: getSentimentColor(item.sentiment), color: 'white' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </TabPanel>

              {/* Social Media Tab */}
              <TabPanel value={tabValue} index={1}>
                {getSocialPosts().length === 0 ? (
                  <Alert severity="info">لا توجد منشورات من وسائل التواصل الاجتماعي حالياً</Alert>
                ) : (
                  <List>
                    {getSocialPosts().map((post, idx) => (
                      <ListItem key={idx} divider>
                        <ListItemText primary={post.text ?? post.title ?? ''} secondary={post.date ?? ''} />
                        <Chip
                          icon={getSentimentIcon(post.sentiment)}
                          label={`${getSentimentLabel(post.sentiment)} (${((post.sentiment ?? 0) * 100).toFixed(0)}%)`}
                          sx={{ bgcolor: getSentimentColor(post.sentiment), color: 'white' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </TabPanel>

              {/* Analyst Ratings Tab */}
              <TabPanel value={tabValue} index={2}>
                <Alert severity="info">تقييمات المحللين غير متاحة حالياً — يتم جلب البيانات من yfinance news</Alert>
              </TabPanel>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SentimentAnalysis;
