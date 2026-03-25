import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  TextField,
  Autocomplete,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  useTheme
} from '@mui/material';
import {
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon
} from '@mui/icons-material';
// استيراد مكتبة الرسوم البيانية
import { createChart, ColorType } from 'lightweight-charts';

// Redux actions
import { fetchTechnicalAnalysis, setSymbol, setTimeframe } from '../store/slices/technicalSlice';

// Fallback: بيانات وهمية تُستخدم فقط إذا فشل جلب البيانات الحقيقية
const generateFallbackData = (days = 90) => {
  const data = [];
  let price = 100;
  const today = new Date();
  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const change = (Math.random() - 0.5) * 3;
    price = Math.max(1, price + change);
    const open = price;
    const high = price + Math.random() * 2;
    const low = Math.max(0.01, price - Math.random() * 2);
    const close = Math.max(0.01, price + (Math.random() - 0.5) * 1.5);
    data.push({ time: date.toISOString().split('T')[0], open, high, low, close });
  }
  return data;
};

// قائمة أسهم سعودية شائعة للبحث السريع
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

const TechnicalAnalysis = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Chart container ref
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  
  // Redux state
  const {
    symbol,
    name,
    timeframe,
    indicators,
    analysisDate,
    trend,
    supportLevels,
    resistanceLevels,
    status,
    error
  } = useSelector((state) => state.technical);
  
  // Local state
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedIndicators, setSelectedIndicators] = useState(['SMA', 'RSI', 'MACD']);
  const [chartType, setChartType] = useState('candles');
  const [candlestickData, setCandlestickData] = useState([]);
  
  // Timeframe options
  const timeframeOptions = [
    { value: 'daily', label: 'يومي' },
    { value: 'weekly', label: 'أسبوعي' },
    { value: 'monthly', label: 'شهري' }
  ];
  
  // Indicator options
  const indicatorOptions = [
    { value: 'SMA', label: 'المتوسط المتحرك البسيط' },
    { value: 'EMA', label: 'المتوسط المتحرك الأسي' },
    { value: 'RSI', label: 'مؤشر القوة النسبية' },
    { value: 'MACD', label: 'تقارب وتباعد المتوسطات المتحركة' },
    { value: 'Bollinger', label: 'نطاقات بولينجر' },
    { value: 'Stochastic', label: 'مؤشر ستوكاستك' }
  ];
  
  // Chart type options
  const chartTypeOptions = [
    { value: 'candles', label: 'شموع' },
    { value: 'line', label: 'خط' },
    { value: 'area', label: 'منطقة' },
    { value: 'bars', label: 'أعمدة' }
  ];
  
  // Handle form changes
  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
    if (newValue) {
      dispatch(setSymbol(newValue.symbol));
    }
  };
  
  const handleTimeframeChange = (event) => {
    dispatch(setTimeframe(event.target.value));
  };
  
  const handleIndicatorsChange = (event) => {
    setSelectedIndicators(event.target.value);
  };
  
  const handleChartTypeChange = (event, newValue) => {
    if (newValue !== null) {
      setChartType(newValue);
    }
  };
  
  // Analyze stock
  const analyzeStock = () => {
    if (symbol) {
      dispatch(fetchTechnicalAnalysis({
        symbol,
        indicators: selectedIndicators,
        timeframe
      }));
    }
  };
  
  // دالة لإنشاء الرسم البياني
  const createChartInstance = useCallback(() => {
    if (!chartContainerRef.current) return;
    
    // تنظيف أي رسم بياني سابق
    if (chartInstanceRef.current) {
      try {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      } catch (error) {
        console.error('Error removing previous chart:', error);
      }
    }
    
    try {
      // إنشاء رسم بياني جديد
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: theme.palette.background.paper },
          textColor: theme.palette.text.primary,
        },
        grid: {
          vertLines: { color: theme.palette.divider },
          horzLines: { color: theme.palette.divider },
        },
        rightPriceScale: {
          borderColor: theme.palette.divider,
        },
        timeScale: {
          borderColor: theme.palette.divider,
        },
        crosshair: {
          mode: 0,
        },
        width: chartContainerRef.current.clientWidth || 800,
        height: 400,
      });
      
      // حفظ مرجع الرسم البياني
      chartInstanceRef.current = chart;
      
      return chart;
    } catch (error) {
      console.error('Error creating chart:', error);
      return null;
    }
  }, [theme]);
  
  // دالة لإضافة سلسلة بيانات إلى الرسم البياني
  const addChartSeries = useCallback((chart, data, type) => {
    if (!chart) return null;
    
    try {
      let series;
      
      switch (type) {
        case 'line':
          series = chart.addLineSeries({
            color: theme.palette.primary.main,
            lineWidth: 2,
          });
          series.setData(data.map(item => ({
            time: item.time,
            value: item.close,
          })));
          break;
          
        case 'area':
          series = chart.addAreaSeries({
            topColor: theme.palette.primary.light,
            bottomColor: theme.palette.primary.light + '00',
            lineColor: theme.palette.primary.main,
            lineWidth: 2,
          });
          series.setData(data.map(item => ({
            time: item.time,
            value: item.close,
          })));
          break;
          
        case 'bars':
          series = chart.addBarSeries({
            upColor: theme.palette.success.main,
            downColor: theme.palette.error.main,
          });
          series.setData(data);
          break;
          
        default: // candles
          series = chart.addCandlestickSeries({
            upColor: theme.palette.success.main,
            downColor: theme.palette.error.main,
            borderVisible: false,
            wickUpColor: theme.palette.success.main,
            wickDownColor: theme.palette.error.main,
          });
          series.setData(data);
          break;
      }
      
      return series;
    } catch (error) {
      console.error(`Error adding ${type} series:`, error);
      return null;
    }
  }, [theme]);
  
  // دالة لإضافة مؤشرات إلى الرسم البياني
  const addIndicators = useCallback((chart, data) => {
    if (!chart) return;
    
    try {
      // إضافة SMA 20
      const sma20Series = chart.addLineSeries({
        color: '#2962FF',
        lineWidth: 2,
        title: 'SMA 20',
      });
      
      const sma20Data = data.map((item, index, arr) => {
        if (index < 20) return null;
        
        const sum = arr.slice(index - 20, index).reduce((acc, val) => acc + val.close, 0);
        return {
          time: item.time,
          value: sum / 20,
        };
      }).filter(Boolean);
      
      sma20Series.setData(sma20Data);
      
      // إضافة SMA 50
      const sma50Series = chart.addLineSeries({
        color: '#FF6D00',
        lineWidth: 2,
        title: 'SMA 50',
      });
      
      const sma50Data = data.map((item, index, arr) => {
        if (index < 50) return null;
        
        const sum = arr.slice(index - 50, index).reduce((acc, val) => acc + val.close, 0);
        return {
          time: item.time,
          value: sum / 50,
        };
      }).filter(Boolean);
      
      sma50Series.setData(sma50Data);
    } catch (error) {
      console.error('Error adding indicators:', error);
    }
  }, []);
  
  // جلب البيانات التاريخية الحقيقية ثم رسمها
  useEffect(() => {
    let cancelled = false;

    const loadChartData = async () => {
      let data = generateFallbackData(); // fallback افتراضي

      if (symbol) {
        try {
          const response = await axios.get(`/api/v1/stocks/${encodeURIComponent(symbol)}/historical`, {
            params: { interval: timeframe },
            timeout: 10000,
          });
          const raw = response.data?.data ?? [];
          if (raw.length > 0) {
            // تحويل إلى الشكل المطلوب من lightweight-charts
            data = raw.map(d => ({
              time:  d.date,
              open:  Number(d.open),
              high:  Number(d.high),
              low:   Number(d.low),
              close: Number(d.close),
            })).filter(d => d.time && !isNaN(d.close));
          }
        } catch {
          // نستخدم الـ fallback المحدد أعلاه
        }
      }

      if (!cancelled) {
        setCandlestickData(data);
      }
    };

    loadChartData();
    return () => { cancelled = true; };
  }, [symbol, timeframe]);

  // رسم البيانات على الـ chart عند تغيّرها
  useEffect(() => {
    if (!candlestickData.length) return;

    // إنشاء الرسم البياني
    const chart = createChartInstance();
    
    if (chart) {
      // إضافة سلسلة البيانات الرئيسية
      addChartSeries(chart, candlestickData, chartType);

      // إضافة المؤشرات
      addIndicators(chart, candlestickData);
      
      // ضبط المقياس الزمني
      chart.timeScale().fitContent();
      
      // معالجة تغيير حجم النافذة
      const handleResize = () => {
        if (chart && chartContainerRef.current) {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };
      
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('resize', handleResize);
        if (chart) {
          chart.remove();
        }
      };
    }
  }, [candlestickData, createChartInstance, addChartSeries, addIndicators, chartType]);
  
  // تحديث الرسم البياني عند تغيير نوع الرسم البياني
  useEffect(() => {
    if (!chartInstanceRef.current || !candlestickData.length) return;
    
    try {
      // إزالة جميع السلاسل الموجودة
      try {
        const series = chartInstanceRef.current.series();
        if (series && series.length) {
          series.forEach(s => {
            chartInstanceRef.current.removeSeries(s);
          });
        }
      } catch (error) {
        console.error('Error removing series:', error);
        // إذا فشلت إزالة السلاسل، أعد إنشاء الرسم البياني
        createChartInstance();
      }
      
      // إضافة سلسلة البيانات الرئيسية
      addChartSeries(chartInstanceRef.current, candlestickData, chartType);
      
      // إضافة المؤشرات
      addIndicators(chartInstanceRef.current, candlestickData);
      
      // ضبط المقياس الزمني
      chartInstanceRef.current.timeScale().fitContent();
    } catch (error) {
      console.error('Error updating chart type:', error);
      
      // إذا فشل التحديث، أعد إنشاء الرسم البياني
      const chart = createChartInstance();
      
      if (chart) {
        addChartSeries(chart, candlestickData, chartType);
        addIndicators(chart, candlestickData);
        chart.timeScale().fitContent();
      }
    }
  }, [chartType, candlestickData, addChartSeries, addIndicators, createChartInstance]);
  
  // Fetch analysis when symbol changes
  useEffect(() => {
    if (symbol && status === 'idle') {
      analyzeStock();
    }
  }, [symbol, status, dispatch]);
  
  // Set initial stock
  useEffect(() => {
    if (!selectedStock && stockSymbols.length > 0) {
      const initialStock = stockSymbols.find(s => s.symbol === '2222.SR') || stockSymbols[0];
      setSelectedStock(initialStock);
      dispatch(setSymbol(initialStock.symbol));
    }
  }, [selectedStock, dispatch]);
  
  // Get trend icon
  const getTrendIcon = () => {
    switch (trend) {
      case 'صاعد':
        return <TrendingUpIcon color="success" />;
      case 'هابط':
        return <TrendingDownIcon color="error" />;
      default:
        return <TrendingFlatIcon color="warning" />;
    }
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('technical.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stock Selection and Controls */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="اختيار السهم والمؤشرات" 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
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
                    <InputLabel id="timeframe-label">
                      {t('technical.timeframe')}
                    </InputLabel>
                    <Select
                      labelId="timeframe-label"
                      id="timeframe"
                      value={timeframe}
                      label={t('technical.timeframe')}
                      onChange={handleTimeframeChange}
                    >
                      {timeframeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="indicators-label">
                      {t('technical.indicators')}
                    </InputLabel>
                    <Select
                      labelId="indicators-label"
                      id="indicators"
                      multiple
                      value={selectedIndicators}
                      label={t('technical.indicators')}
                      onChange={handleIndicatorsChange}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip 
                              key={value} 
                              label={indicatorOptions.find(option => option.value === value)?.label} 
                              size="small" 
                            />
                          ))}
                        </Box>
                      )}
                    >
                      {indicatorOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={2}>
                  <Box sx={{ display: 'flex', height: '100%', alignItems: 'center' }}>
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
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title={selectedStock ? `${selectedStock.name} (${selectedStock.symbol})` : 'الرسم البياني'}
              titleTypographyProps={{ variant: 'h6' }}
              subheader={analysisDate ? `تاريخ التحليل: ${analysisDate}` : ''}
              action={
                <ToggleButtonGroup
                  value={chartType}
                  exclusive
                  onChange={handleChartTypeChange}
                  size="small"
                  aria-label="chart type"
                >
                  {chartTypeOptions.map((option) => (
                    <ToggleButton key={option.value} value={option.value}>
                      {option.label}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
              }
            />
            <Divider />
            <CardContent>
              {status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3, height: 400 }}>
                  <CircularProgress />
                </Box>
              ) : status === 'failed' ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error || 'حدث خطأ أثناء جلب بيانات التحليل الفني'}
                </Alert>
              ) : (
                <Box ref={chartContainerRef} sx={{ height: 400 }} />
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Analysis Results */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Trend */}
            <Grid item xs={12}>
              <Card>
                <CardHeader 
                  title={t('technical.trend')}
                  titleTypographyProps={{ variant: 'h6' }}
                  avatar={getTrendIcon()}
                />
                <Divider />
                <CardContent>
                  {status === 'loading' ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 1 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : status === 'succeeded' ? (
                    <Typography variant="h5" align="center" sx={{ fontWeight: 'bold' }}>
                      {trend}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center">
                      لا توجد بيانات متاحة
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            {/* Support Levels */}
            <Grid item xs={12} sm={6} md={12}>
              <Card>
                <CardHeader 
                  title={t('technical.support')}
                  titleTypographyProps={{ variant: 'h6' }}
                />
                <Divider />
                <CardContent>
                  {status === 'loading' ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 1 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : status === 'succeeded' && supportLevels?.length > 0 ? (
                    <List dense>
                      {supportLevels.map((level, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={`المستوى ${index + 1}: ${level} ريال`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center">
                      لا توجد بيانات متاحة
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            {/* Resistance Levels */}
            <Grid item xs={12} sm={6} md={12}>
              <Card>
                <CardHeader 
                  title={t('technical.resistance')}
                  titleTypographyProps={{ variant: 'h6' }}
                />
                <Divider />
                <CardContent>
                  {status === 'loading' ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 1 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : status === 'succeeded' && resistanceLevels?.length > 0 ? (
                    <List dense>
                      {resistanceLevels.map((level, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={`المستوى ${index + 1}: ${level} ريال`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center">
                      لا توجد بيانات متاحة
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Indicators */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title={t('technical.indicators')}
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              {status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : status === 'failed' ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error || 'حدث خطأ أثناء جلب بيانات المؤشرات الفنية'}
                </Alert>
              ) : status === 'succeeded' && Object.keys(indicators).length > 0 ? (
                <Grid container spacing={3}>
                  {/* SMA */}
                  {indicators.SMA && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          المتوسط المتحرك البسيط (SMA)
                        </Typography>
                        <List dense>
                          {Object.entries(indicators.SMA).map(([period, value]) => (
                            <ListItem key={period}>
                              <ListItemText
                                primary={`SMA ${period}: ${value.toFixed(2)} ريال`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Grid>
                  )}
                  
                  {/* RSI */}
                  {indicators.RSI && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          مؤشر القوة النسبية (RSI)
                        </Typography>
                        <List dense>
                          {Object.entries(indicators.RSI).map(([period, value]) => (
                            <ListItem key={period}>
                              <ListItemText
                                primary={`RSI ${period}: ${value.toFixed(2)}`}
                                secondary={
                                  value > 70 ? 'ذروة شراء' : 
                                  value < 30 ? 'ذروة بيع' : 
                                  'منطقة محايدة'
                                }
                                secondaryTypographyProps={{
                                  color: 
                                    value > 70 ? 'error.main' : 
                                    value < 30 ? 'success.main' : 
                                    'text.secondary'
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Grid>
                  )}
                  
                  {/* MACD */}
                  {indicators.MACD && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          تقارب وتباعد المتوسطات المتحركة (MACD)
                        </Typography>
                        <List dense>
                          <ListItem>
                            <ListItemText
                              primary={`خط MACD: ${indicators.MACD.line.toFixed(2)}`}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText
                              primary={`خط الإشارة: ${indicators.MACD.signal.toFixed(2)}`}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText
                              primary={`الهيستوجرام: ${indicators.MACD.histogram.toFixed(2)}`}
                              secondary={
                                indicators.MACD.histogram > 0 ? 'إشارة شراء' : 'إشارة بيع'
                              }
                              secondaryTypographyProps={{
                                color: indicators.MACD.histogram > 0 ? 'success.main' : 'error.main'
                              }}
                            />
                          </ListItem>
                        </List>
                      </Paper>
                    </Grid>
                  )}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  لا توجد بيانات متاحة للمؤشرات الفنية
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TechnicalAnalysis;