import React, { useState, useEffect } from 'react';
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
  Alert
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { marketApi, recommendationApi } from '../utils/api';
import { Link } from 'react-router-dom';
import ReactApexChart from 'react-apexcharts';
import { CHART_COLORS } from '../utils/constants';

const Dashboard = () => {
  const { t } = useTranslation();
  const [marketData, setMarketData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [topGainers, setTopGainers] = useState([]);
  const [topLosers, setTopLosers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch market overview
        const marketResponse = await marketApi.getOverview();
        setMarketData(marketResponse.data.data);
        
        // Fetch top recommendations
        const recommendationsResponse = await recommendationApi.getAll({
          limit: 5,
          min_confidence: 70,
          order_by: 'confidence',
          order_direction: 'desc'
        });
        setRecommendations(recommendationsResponse.data.data);
        
        // Fetch top gainers
        const gainersResponse = await marketApi.getTopGainers(5);
        setTopGainers(gainersResponse.data.data);
        
        // Fetch top losers
        const losersResponse = await marketApi.getTopLosers(5);
        setTopLosers(losersResponse.data.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError(t('error_occurred'));
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [t]);

  // Chart options for market performance
  const marketChartOptions = {
    chart: {
      type: 'area',
      height: 250,
      toolbar: {
        show: false
      },
      fontFamily: 'Tajawal, Arial, sans-serif',
    },
    colors: [CHART_COLORS.primary],
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 2
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
    xaxis: {
      categories: marketData?.performance?.dates || [],
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
    tooltip: {
      x: {
        format: 'dd/MM/yy'
      },
    },
  };

  // Chart series for market performance
  const marketChartSeries = [
    {
      name: t('market_index'),
      data: marketData?.performance?.values || []
    }
  ];

  // Chart options for sector performance
  const sectorChartOptions = {
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
        horizontal: true,
        barHeight: '70%',
        distributed: true,
        dataLabels: {
          position: 'bottom'
        },
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
    ],
    dataLabels: {
      enabled: true,
      textAnchor: 'start',
      style: {
        colors: ['#fff'],
        fontFamily: 'Tajawal, Arial, sans-serif',
      },
      formatter: function(val, opt) {
        return val.toFixed(2) + '%';
      },
      offsetX: 0,
      dropShadow: {
        enabled: true
      }
    },
    stroke: {
      width: 1,
      colors: ['#fff']
    },
    xaxis: {
      categories: marketData?.sectors?.map(sector => sector.name) || [],
      labels: {
        style: {
          fontFamily: 'Tajawal, Arial, sans-serif',
        }
      }
    },
    yaxis: {
      labels: {
        show: false
      }
    },
    tooltip: {
      theme: 'dark',
      x: {
        show: false
      },
      y: {
        title: {
          formatter: function() {
            return '';
          }
        }
      }
    }
  };

  // Chart series for sector performance
  const sectorChartSeries = [
    {
      name: t('change_percent'),
      data: marketData?.sectors?.map(sector => parseFloat(sector.change_percent)) || []
    }
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('dashboard')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Market Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {t('market_summary')}
            </Typography>
            {marketData && (
              <Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('market_index')}
                    </Typography>
                    <Typography variant="h5">
                      {marketData.index.value.toFixed(2)}
                    </Typography>
                    <Chip 
                      label={`${marketData.index.change_percent > 0 ? '+' : ''}${marketData.index.change_percent.toFixed(2)}%`} 
                      color={marketData.index.change_percent > 0 ? 'success' : 'error'}
                      size="small"
                      sx={{ mt: 0.5 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('volume')}
                    </Typography>
                    <Typography variant="h5">
                      {(marketData.volume / 1000000).toFixed(2)}M
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('market_cap')}
                    </Typography>
                    <Typography variant="h5">
                      {(marketData.market_cap / 1000000000).toFixed(2)}B
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('traded_stocks')}
                    </Typography>
                    <Typography variant="h5">
                      {marketData.traded_stocks}
                    </Typography>
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {t('market_performance')}
                  </Typography>
                  <ReactApexChart 
                    options={marketChartOptions} 
                    series={marketChartSeries} 
                    type="area" 
                    height={250} 
                  />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Top Recommendations */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {t('top_recommendations')}
            </Typography>
            {recommendations.length > 0 ? (
              <List>
                {recommendations.map((recommendation) => (
                  <React.Fragment key={recommendation.id}>
                    <ListItem 
                      component={Link} 
                      to={`/stock/${recommendation.stock.symbol}`}
                      sx={{ 
                        textDecoration: 'none', 
                        color: 'inherit',
                        '&:hover': {
                          backgroundColor: 'rgba(0, 0, 0, 0.04)'
                        }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle1">
                              {recommendation.stock.name} ({recommendation.stock.symbol})
                            </Typography>
                            <Chip 
                              label={t(recommendation.action)} 
                              color={recommendation.action === 'buy' ? 'success' : recommendation.action === 'sell' ? 'error' : 'warning'}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Grid container spacing={1}>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  {t('current_price')}: {recommendation.price.toFixed(2)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  {t('target_price')}: {recommendation.target_price.toFixed(2)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  {t('confidence')}: {recommendation.confidence}%
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  {t('potential_return')}: {((recommendation.target_price - recommendation.price) / recommendation.price * 100).toFixed(2)}%
                                </Typography>
                              </Grid>
                            </Grid>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Typography variant="body1" sx={{ textAlign: 'center', py: 4 }}>
                {t('no_recommendations')}
              </Typography>
            )}
          </Paper>
        </Grid>
        
        {/* Top Gainers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title={t('top_gainers')} />
            <CardContent>
              {topGainers.length > 0 ? (
                <List>
                  {topGainers.map((stock) => (
                    <React.Fragment key={stock.symbol}>
                      <ListItem 
                        component={Link} 
                        to={`/stock/${stock.symbol}`}
                        sx={{ 
                          textDecoration: 'none', 
                          color: 'inherit',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 0, 0, 0.04)'
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="subtitle1">
                                {stock.name} ({stock.symbol})
                              </Typography>
                              <Typography variant="subtitle1" color="success.main">
                                +{stock.change_percent.toFixed(2)}%
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                              <Typography variant="body2" color="text.secondary">
                                {t('price')}: {stock.price.toFixed(2)}
                              </Typography>
                              <Typography variant="body2" color="success.main">
                                +{stock.change.toFixed(2)}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body1" sx={{ textAlign: 'center', py: 2 }}>
                  {t('no_stocks')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Top Losers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title={t('top_losers')} />
            <CardContent>
              {topLosers.length > 0 ? (
                <List>
                  {topLosers.map((stock) => (
                    <React.Fragment key={stock.symbol}>
                      <ListItem 
                        component={Link} 
                        to={`/stock/${stock.symbol}`}
                        sx={{ 
                          textDecoration: 'none', 
                          color: 'inherit',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 0, 0, 0.04)'
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="subtitle1">
                                {stock.name} ({stock.symbol})
                              </Typography>
                              <Typography variant="subtitle1" color="error.main">
                                {stock.change_percent.toFixed(2)}%
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                              <Typography variant="body2" color="text.secondary">
                                {t('price')}: {stock.price.toFixed(2)}
                              </Typography>
                              <Typography variant="body2" color="error.main">
                                {stock.change.toFixed(2)}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body1" sx={{ textAlign: 'center', py: 2 }}>
                  {t('no_stocks')}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sector Performance */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('sector_performance')}
            </Typography>
            {marketData?.sectors && (
              <ReactApexChart 
                options={sectorChartOptions} 
                series={sectorChartSeries} 
                type="bar" 
                height={350} 
              />
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;