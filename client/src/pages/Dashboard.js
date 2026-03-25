import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  useTheme
} from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon, 
  TrendingDown as TrendingDownIcon,
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon
} from '@mui/icons-material';

// Charts
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
  Legend
} from 'recharts';

// Redux actions
import { fetchMarketData } from '../store/slices/marketSlice';
import { fetchRecommendations } from '../store/slices/recommendationsSlice';
import { fetchSentimentAnalysis } from '../store/slices/sentimentSlice';

// Static fallback for market index chart (no dedicated historical index API)
const marketIndexData = [
  { date: '2025-01', value: 10500 },
  { date: '2025-02', value: 10800 },
  { date: '2025-03', value: 11200 },
  { date: '2025-04', value: 11000 },
  { date: '2025-05', value: 11500 },
  { date: '2025-06', value: 11300 },
  { date: '2025-07', value: 11800 },
  { date: '2025-08', value: 12200 },
];

const SECTOR_COLORS = ['#1976d2','#388e3c','#f57c00','#d32f2f','#7b1fa2','#0097a7'];

const Dashboard = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const marketData = useSelector((state) => state.market);
  const recommendations = useSelector((state) => state.recommendations);
  const sentiment = useSelector((state) => state.sentiment);

  // Local state for sector performance (fetched from API)
  const [sectorPerformanceData, setSectorPerformanceData] = useState([
    { name: 'البنوك', value: 8.5, fill: '#1976d2' },
    { name: 'الطاقة', value: 5.2, fill: '#388e3c' },
    { name: 'الاتصالات', value: 3.7, fill: '#f57c00' },
    { name: 'التأمين', value: -2.1, fill: '#d32f2f' },
    { name: 'العقارات', value: 1.8, fill: '#7b1fa2' },
    { name: 'الصناعة', value: 4.3, fill: '#0097a7' },
  ]);

  // Derive marketSentimentData from Redux sentiment state
  const marketSentimentData = useMemo(() => {
    const allSentiments = Object.values(sentiment?.sentiment ?? {});
    if (allSentiments.length === 0) {
      return [
        { name: 'إيجابي', value: 55, fill: '#4caf50' },
        { name: 'محايد', value: 30, fill: '#ff9800' },
        { name: 'سلبي', value: 15, fill: '#f44336' },
      ];
    }
    const avg = (key) =>
      Math.round((allSentiments.reduce((s, x) => s + (x[key] ?? 0), 0) / allSentiments.length) * 100);
    const pos = avg('positive_ratio');
    const neg = avg('negative_ratio');
    const neu = Math.max(0, 100 - pos - neg);
    return [
      { name: 'إيجابي', value: pos || 1, fill: '#4caf50' },
      { name: 'محايد', value: neu, fill: '#ff9800' },
      { name: 'سلبي', value: neg || 1, fill: '#f44336' },
    ];
  }, [sentiment?.sentiment]);

  // Fetch sector performance from API
  useEffect(() => {
    axios.get('/api/v1/market/sectors').then((res) => {
      const sectors = Array.isArray(res.data)
        ? res.data
        : res.data?.data ?? res.data?.sectors ?? [];
      if (sectors.length > 0) {
        setSectorPerformanceData(
          sectors.map((s, i) => ({
            name: s.name,
            value: s.change_percent ?? 0,
            fill: SECTOR_COLORS[i % SECTOR_COLORS.length],
          }))
        );
      }
    }).catch(() => {});
  }, []);

  // Fetch data on component mount
  useEffect(() => {
    dispatch(fetchMarketData({ symbols: ['2222.SR', '1211.SR', '2010.SR', '1150.SR', '1010.SR'] }));
    dispatch(fetchRecommendations({ maxResults: 3 }));
    dispatch(fetchSentimentAnalysis({ symbols: ['2222.SR', '1211.SR'] }));
  }, [dispatch]);
  
  // Prepare top gainers and losers
  const topGainers = [];
  const topLosers = [];
  
  if (marketData.status === 'succeeded') {
    // Process market data to get top gainers and losers
    const stocksArray = Object.entries(marketData.data).map(([symbol, data]) => ({
      symbol,
      ...data
    }));
    
    // Sort by change percentage
    const sortedStocks = [...stocksArray].sort((a, b) => {
      const aChange = parseFloat(a.change_percent);
      const bChange = parseFloat(b.change_percent);
      return bChange - aChange;
    });
    
    // Get top 3 gainers and losers
    topGainers.push(...sortedStocks.slice(0, 3));
    topLosers.push(...sortedStocks.slice(-3).reverse());
  }
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('nav.dashboard')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Market Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title={t('dashboard.marketOverview')} 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={marketIndexData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke={theme.palette.primary.main} 
                      fill={theme.palette.primary.light} 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Market Sentiment */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader 
              title={t('dashboard.marketSentiment')} 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={marketSentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    />
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Top Gainers */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardHeader 
              title={t('dashboard.topGainers')} 
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<TrendingUpIcon color="success" />}
            />
            <Divider />
            <CardContent>
              {marketData.status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress />
                </Box>
              ) : marketData.status === 'succeeded' && topGainers.length > 0 ? (
                <List>
                  {topGainers.map((stock) => (
                    <ListItem key={stock.symbol} divider>
                      <ListItemText
                        primary={stock.symbol}
                        secondary={`${stock.price} ريال`}
                      />
                      <Chip
                        icon={<ArrowUpIcon />}
                        label={stock.change_percent}
                        color="success"
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  {t('status.noData')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Top Losers */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardHeader 
              title={t('dashboard.topLosers')} 
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<TrendingDownIcon color="error" />}
            />
            <Divider />
            <CardContent>
              {marketData.status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress />
                </Box>
              ) : marketData.status === 'succeeded' && topLosers.length > 0 ? (
                <List>
                  {topLosers.map((stock) => (
                    <ListItem key={stock.symbol} divider>
                      <ListItemText
                        primary={stock.symbol}
                        secondary={`${stock.price} ريال`}
                      />
                      <Chip
                        icon={<ArrowDownIcon />}
                        label={stock.change_percent}
                        color="error"
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  {t('status.noData')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Recommendations */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardHeader 
              title={t('dashboard.recentRecommendations')} 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              {recommendations.status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress />
                </Box>
              ) : recommendations.status === 'succeeded' && recommendations.recommendations.length > 0 ? (
                <List>
                  {recommendations.recommendations.slice(0, 3).map((rec) => (
                    <ListItem key={rec.symbol} divider>
                      <ListItemText
                        primary={`${rec.name} (${rec.symbol})`}
                        secondary={rec.sector}
                      />
                      <Chip
                        label={t(`stock.${rec.recommendation.toLowerCase()}`)}
                        color={
                          rec.recommendation === 'شراء' ? 'success' :
                          rec.recommendation === 'بيع' ? 'error' : 'warning'
                        }
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  {t('status.noData')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sector Performance */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title={t('dashboard.sectorPerformance')} 
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={sectorPerformanceData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value}%`, 'التغير']} />
                    <Bar dataKey="value">
                      {sectorPerformanceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;