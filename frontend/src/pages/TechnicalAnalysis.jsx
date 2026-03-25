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
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  Timeline,
  ArrowUpward,
  ArrowDownward,
  Remove,
  Info
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import ReactApexChart from 'react-apexcharts';
import { stockApi, technicalApi } from '../utils/api';
import { CHART_COLORS, TIME_FRAMES, TECHNICAL_INDICATORS } from '../utils/constants';

const TechnicalAnalysis = () => {
  const { t } = useTranslation();
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [timeFrame, setTimeFrame] = useState('1m');
  const [selectedIndicators, setSelectedIndicators] = useState(['sma', 'ema']);
  const [stockData, setStockData] = useState(null);
  const [indicatorData, setIndicatorData] = useState(null);
  const [patterns, setPatterns] = useState([]);
  const [supportResistance, setSupportResistance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  // Fetch stock data when stock or timeframe changes
  useEffect(() => {
    if (selectedStock) {
      fetchStockData();
    }
  }, [selectedStock, timeFrame]);

  const fetchStockData = async () => {
    if (!selectedStock) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch historical prices
      const pricesResponse = await stockApi.getHistoricalPrices(selectedStock.symbol, timeFrame);
      setStockData(pricesResponse.data.data);

      // Fetch technical indicators
      const indicatorsResponse = await technicalApi.getIndicators(
        selectedStock.symbol,
        selectedIndicators,
        timeFrame
      );
      setIndicatorData(indicatorsResponse.data.data);

      // Fetch chart patterns
      const patternsResponse = await technicalApi.getChartPatterns(
        selectedStock.symbol,
        timeFrame
      );
      setPatterns(patternsResponse.data.data);

      // Fetch support and resistance levels
      const supportResistanceResponse = await technicalApi.getSupportResistance(
        selectedStock.symbol
      );
      setSupportResistance(supportResistanceResponse.data.data);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching technical data:', error);
      setError(t('error_fetching_technical_data'));
      setLoading(false);
    }
  };

  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
  };

  const handleTimeFrameChange = (event) => {
    setTimeFrame(event.target.value);
  };

  const handleIndicatorChange = (event, newValue) => {
    setSelectedIndicators(newValue);
  };

  const handleAnalyze = () => {
    fetchStockData();
  };

  // Prepare chart options and series
  const chartOptions = {
    chart: {
      type: 'candlestick',
      height: 500,
      id: 'candles',
      toolbar: {
        autoSelected: 'pan',
        show: true
      },
      zoom: {
        enabled: true
      },
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    title: {
      text: selectedStock ? `${selectedStock.name} (${selectedStock.symbol})` : '',
      align: 'center',
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    },
    xaxis: {
      type: 'datetime',
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    yaxis: {
      tooltip: {
        enabled: true
      },
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    grid: {
      borderColor: CHART_COLORS.grid,
    },
    plotOptions: {
      candlestick: {
        colors: {
          upward: CHART_COLORS.upTrend,
          downward: CHART_COLORS.downTrend
        }
      }
    },
    annotations: {
      yaxis: supportResistance ? [
        ...supportResistance.support.map((level, index) => ({
          y: level,
          borderColor: '#00E396',
          label: {
            borderColor: '#00E396',
            style: {
              color: '#fff',
              background: '#00E396'
            },
            text: `S${index + 1}`
          }
        })),
        ...supportResistance.resistance.map((level, index) => ({
          y: level,
          borderColor: '#FEB019',
          label: {
            borderColor: '#FEB019',
            style: {
              color: '#fff',
              background: '#FEB019'
            },
            text: `R${index + 1}`
          }
        }))
      ] : [],
      xaxis: patterns ? patterns.map((pattern, index) => ({
        x: new Date(pattern.date).getTime(),
        borderColor: pattern.type === 'bullish' ? '#00E396' : '#FF4560',
        label: {
          borderColor: pattern.type === 'bullish' ? '#00E396' : '#FF4560',
          style: {
            color: '#fff',
            background: pattern.type === 'bullish' ? '#00E396' : '#FF4560'
          },
          text: pattern.name
        }
      })) : []
    },
    tooltip: {
      enabled: true,
      theme: 'dark',
      style: {
        fontFamily: 'Tajawal, Arial, sans-serif',
      }
    }
  };

  const candleSeries = stockData ? [{
    name: 'candles',
    data: stockData.map(item => ({
      x: new Date(item.date).getTime(),
      y: [item.open, item.high, item.low, item.close]
    }))
  }] : [];

  // Prepare indicator series
  const indicatorSeries = [];
  if (indicatorData) {
    if (indicatorData.sma && selectedIndicators.includes('sma')) {
      indicatorSeries.push({
        name: 'SMA',
        type: 'line',
        data: indicatorData.sma.map(item => ({
          x: new Date(item.date).getTime(),
          y: item.value
        }))
      });
    }
    if (indicatorData.ema && selectedIndicators.includes('ema')) {
      indicatorSeries.push({
        name: 'EMA',
        type: 'line',
        data: indicatorData.ema.map(item => ({
          x: new Date(item.date).getTime(),
          y: item.value
        }))
      });
    }
    // Add other indicators as needed
  }

  // Combine candle series with indicator series
  const combinedSeries = [...candleSeries, ...indicatorSeries];

  // Determine overall trend
  const calculateTrend = () => {
    if (!stockData || stockData.length < 2) return 'neutral';
    
    const firstClose = stockData[0].close;
    const lastClose = stockData[stockData.length - 1].close;
    
    if (lastClose > firstClose) return 'bullish';
    if (lastClose < firstClose) return 'bearish';
    return 'neutral';
  };

  const trend = calculateTrend();

  // Calculate technical signals
  const calculateSignals = () => {
    if (!indicatorData) return {};
    
    const signals = {
      sma: 'neutral',
      ema: 'neutral',
      macd: 'neutral',
      rsi: 'neutral'
    };
    
    // Example signal calculations (simplified)
    if (indicatorData.sma && stockData) {
      const lastPrice = stockData[stockData.length - 1].close;
      const lastSMA = indicatorData.sma[indicatorData.sma.length - 1].value;
      
      if (lastPrice > lastSMA) signals.sma = 'bullish';
      else if (lastPrice < lastSMA) signals.sma = 'bearish';
    }
    
    if (indicatorData.ema && stockData) {
      const lastPrice = stockData[stockData.length - 1].close;
      const lastEMA = indicatorData.ema[indicatorData.ema.length - 1].value;
      
      if (lastPrice > lastEMA) signals.ema = 'bullish';
      else if (lastPrice < lastEMA) signals.ema = 'bearish';
    }
    
    // Add other indicator signals
    
    return signals;
  };

  const signals = calculateSignals();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('technical_analysis')}
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
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
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel id="time-frame-label">{t('time_frame')}</InputLabel>
              <Select
                labelId="time-frame-label"
                id="time-frame"
                value={timeFrame}
                label={t('time_frame')}
                onChange={handleTimeFrameChange}
              >
                {TIME_FRAMES.map((frame) => (
                  <MenuItem key={frame.value} value={frame.value}>
                    {frame.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Autocomplete
              multiple
              options={TECHNICAL_INDICATORS.map(indicator => indicator.value)}
              getOptionLabel={(option) => {
                const indicator = TECHNICAL_INDICATORS.find(ind => ind.value === option);
                return indicator ? indicator.label : option;
              }}
              value={selectedIndicators}
              onChange={handleIndicatorChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('select_indicators')}
                  variant="outlined"
                  fullWidth
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => {
                  const indicator = TECHNICAL_INDICATORS.find(ind => ind.value === option);
                  return (
                    <Chip
                      label={indicator ? indicator.label : option}
                      {...getTagProps({ index })}
                      key={option}
                    />
                  );
                })
              }
            />
          </Grid>
          <Grid item xs={12} md={1}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleAnalyze}
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

      {selectedStock && stockData && (
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {t('price_chart')}
              </Typography>
              <Box sx={{ height: 500 }}>
                <ReactApexChart
                  options={chartOptions}
                  series={combinedSeries}
                  type="candlestick"
                  height={500}
                />
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardHeader title={t('technical_summary')} />
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ mr: 2 }}>
                        {t('overall_trend')}:
                      </Typography>
                      <Chip
                        icon={
                          trend === 'bullish' ? (
                            <TrendingUp />
                          ) : trend === 'bearish' ? (
                            <TrendingDown />
                          ) : (
                            <Remove />
                          )
                        }
                        label={t(trend)}
                        color={
                          trend === 'bullish'
                            ? 'success'
                            : trend === 'bearish'
                            ? 'error'
                            : 'default'
                        }
                      />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle1" gutterBottom>
                      {t('price_levels')}:
                    </Typography>
                    {stockData && stockData.length > 0 && (
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('current')}:
                          </Typography>
                          <Typography variant="body1">
                            {stockData[stockData.length - 1].close.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('previous_close')}:
                          </Typography>
                          <Typography variant="body1">
                            {stockData[stockData.length - 2]?.close.toFixed(2) || '-'}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('high')} ({timeFrame}):
                          </Typography>
                          <Typography variant="body1">
                            {Math.max(...stockData.map(item => item.high)).toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('low')} ({timeFrame}):
                          </Typography>
                          <Typography variant="body1">
                            {Math.min(...stockData.map(item => item.low)).toFixed(2)}
                          </Typography>
                        </Grid>
                      </Grid>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle1" gutterBottom>
                      {t('support_resistance')}:
                    </Typography>
                    {supportResistance && (
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('resistance')}:
                          </Typography>
                          {supportResistance.resistance.map((level, index) => (
                            <Typography key={index} variant="body1">
                              R{index + 1}: {level.toFixed(2)}
                            </Typography>
                          ))}
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            {t('support')}:
                          </Typography>
                          {supportResistance.support.map((level, index) => (
                            <Typography key={index} variant="body1">
                              S{index + 1}: {level.toFixed(2)}
                            </Typography>
                          ))}
                        </Grid>
                      </Grid>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardHeader title={t('technical_signals')} />
                  <CardContent>
                    <List>
                      {Object.entries(signals).map(([indicator, signal]) => {
                        const indicatorObj = TECHNICAL_INDICATORS.find(
                          ind => ind.value === indicator
                        );
                        if (!indicatorObj || !selectedIndicators.includes(indicator)) return null;
                        
                        return (
                          <ListItem key={indicator}>
                            <ListItemIcon>
                              {signal === 'bullish' ? (
                                <ArrowUpward color="success" />
                              ) : signal === 'bearish' ? (
                                <ArrowDownward color="error" />
                              ) : (
                                <Remove />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={indicatorObj.label}
                              secondary={t(signal)}
                            />
                            <Tooltip title={t(`${indicator}_explanation`)}>
                              <Info color="action" />
                            </Tooltip>
                          </ListItem>
                        );
                      })}
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardHeader title={t('chart_patterns')} />
                  <CardContent>
                    {patterns && patterns.length > 0 ? (
                      <List>
                        {patterns.map((pattern, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {pattern.type === 'bullish' ? (
                                <ArrowUpward color="success" />
                              ) : (
                                <ArrowDownward color="error" />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={pattern.name}
                              secondary={`${t('detected_on')}: ${new Date(pattern.date).toLocaleDateString()}`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body1" align="center">
                        {t('no_patterns_detected')}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default TechnicalAnalysis;