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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Rating,
  Tooltip,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

// Redux actions
import { 
  fetchRecommendations, 
  setRiskProfile, 
  setInvestmentHorizon 
} from '../store/slices/recommendationsSlice';

const Recommendations = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const dispatch = useDispatch();
  
  // Redux state
  const { 
    recommendations, 
    riskProfile, 
    investmentHorizon, 
    analysisDate, 
    status, 
    error 
  } = useSelector((state) => state.recommendations);
  
  // Local state
  const [selectedSectors, setSelectedSectors] = useState(['technology', 'healthcare']);
  const [excludedSymbols, setExcludedSymbols] = useState([]);
  const [maxResults, setMaxResults] = useState(5);
  
  // Risk profile options
  const riskProfileOptions = [
    { value: 'conservative', label: 'متحفظ' },
    { value: 'moderate', label: 'معتدل' },
    { value: 'aggressive', label: 'مخاطر' }
  ];
  
  // Investment horizon options
  const investmentHorizonOptions = [
    { value: 'short', label: 'قصير المدى' },
    { value: 'medium', label: 'متوسط المدى' },
    { value: 'long', label: 'طويل المدى' }
  ];
  
  // Sector options
  const sectorOptions = [
    { value: 'technology', label: 'تقنية المعلومات' },
    { value: 'healthcare', label: 'الرعاية الصحية' },
    { value: 'finance', label: 'المالية' },
    { value: 'energy', label: 'الطاقة' },
    { value: 'consumer', label: 'السلع الاستهلاكية' },
    { value: 'telecom', label: 'الاتصالات' },
    { value: 'industrial', label: 'الصناعة' },
    { value: 'materials', label: 'المواد الأساسية' },
    { value: 'realestate', label: 'العقارات' }
  ];
  
  // Handle form changes
  const handleRiskProfileChange = (event) => {
    dispatch(setRiskProfile(event.target.value));
  };
  
  const handleInvestmentHorizonChange = (event) => {
    dispatch(setInvestmentHorizon(event.target.value));
  };
  
  const handleSectorsChange = (event) => {
    setSelectedSectors(event.target.value);
  };
  
  const handleMaxResultsChange = (event) => {
    setMaxResults(event.target.value);
  };
  
  // Generate recommendations
  const generateRecommendations = () => {
    dispatch(fetchRecommendations({
      riskProfile,
      investmentHorizon,
      sectors: selectedSectors,
      excludeSymbols: excludedSymbols,
      maxResults
    }));
  };
  
  // Get recommendation color
  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'شراء':
        return theme.palette.success.main;
      case 'بيع':
        return theme.palette.error.main;
      case 'احتفاظ':
        return theme.palette.warning.main;
      default:
        return theme.palette.text.primary;
    }
  };
  
  // Get risk score rating
  const getRiskRating = (riskScore) => {
    return riskScore * 5; // Convert 0-1 to 0-5 scale
  };
  
  // Get confidence rating
  const getConfidenceRating = (confidence) => {
    return confidence * 5; // Convert 0-1 to 0-5 scale
  };
  
  // Fetch recommendations on component mount
  useEffect(() => {
    if (status === 'idle') {
      generateRecommendations();
    }
  }, [status, dispatch]);
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('recommendations.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Filters */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="معايير التوصية" 
              titleTypographyProps={{ variant: 'h6' }}
              action={
                <IconButton onClick={generateRecommendations}>
                  <RefreshIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="risk-profile-label">
                      {t('recommendations.riskProfile')}
                    </InputLabel>
                    <Select
                      labelId="risk-profile-label"
                      id="risk-profile"
                      value={riskProfile}
                      label={t('recommendations.riskProfile')}
                      onChange={handleRiskProfileChange}
                    >
                      {riskProfileOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="investment-horizon-label">
                      {t('recommendations.investmentHorizon')}
                    </InputLabel>
                    <Select
                      labelId="investment-horizon-label"
                      id="investment-horizon"
                      value={investmentHorizon}
                      label={t('recommendations.investmentHorizon')}
                      onChange={handleInvestmentHorizonChange}
                    >
                      {investmentHorizonOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="sectors-label">
                      {t('recommendations.sectors')}
                    </InputLabel>
                    <Select
                      labelId="sectors-label"
                      id="sectors"
                      multiple
                      value={selectedSectors}
                      label={t('recommendations.sectors')}
                      onChange={handleSectorsChange}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip 
                              key={value} 
                              label={sectorOptions.find(option => option.value === value)?.label} 
                              size="small" 
                            />
                          ))}
                        </Box>
                      )}
                    >
                      {sectorOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="max-results-label">
                      عدد النتائج
                    </InputLabel>
                    <Select
                      labelId="max-results-label"
                      id="max-results"
                      value={maxResults}
                      label="عدد النتائج"
                      onChange={handleMaxResultsChange}
                    >
                      <MenuItem value={5}>5</MenuItem>
                      <MenuItem value={10}>10</MenuItem>
                      <MenuItem value={15}>15</MenuItem>
                      <MenuItem value={20}>20</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={generateRecommendations}
                      startIcon={<FilterIcon />}
                    >
                      {t('recommendations.generate')}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recommendations Table */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="نتائج التوصيات" 
              titleTypographyProps={{ variant: 'h6' }}
              subheader={analysisDate ? `تاريخ التحليل: ${analysisDate}` : ''}
            />
            <Divider />
            <CardContent>
              {status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : status === 'failed' ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error || 'حدث خطأ أثناء جلب التوصيات'}
                </Alert>
              ) : recommendations.length > 0 ? (
                <TableContainer component={Paper} sx={{ mt: 2 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>الرمز</TableCell>
                        <TableCell>الاسم</TableCell>
                        <TableCell>القطاع</TableCell>
                        <TableCell>التوصية</TableCell>
                        <TableCell>السعر الحالي</TableCell>
                        <TableCell>السعر المستهدف</TableCell>
                        <TableCell>الإمكانات</TableCell>
                        <TableCell>المخاطرة</TableCell>
                        <TableCell>الثقة</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recommendations.map((rec) => (
                        <TableRow key={rec.symbol}>
                          <TableCell>{rec.symbol}</TableCell>
                          <TableCell>{rec.name}</TableCell>
                          <TableCell>{rec.sector}</TableCell>
                          <TableCell>
                            <Chip
                              label={rec.recommendation}
                              sx={{
                                bgcolor: getRecommendationColor(rec.recommendation),
                                color: 'white',
                              }}
                            />
                          </TableCell>
                          <TableCell>{rec.current_price != null ? `${rec.current_price} ريال` : '--'}</TableCell>
                          <TableCell>{rec.target_price != null ? `${rec.target_price} ريال` : '--'}</TableCell>
                          <TableCell>{rec.potential != null ? rec.potential : '--'}</TableCell>
                          <TableCell>
                            <Tooltip title={`درجة المخاطرة: ${((rec.risk_score ?? 0) * 100).toFixed(0)}%`}>
                              <Box>
                                <Rating
                                  value={getRiskRating(rec.risk_score ?? 0)}
                                  precision={0.5}
                                  readOnly
                                  size="small"
                                />
                              </Box>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={`مستوى الثقة: ${((rec.confidence ?? 0) * 100).toFixed(0)}%`}>
                              <Box>
                                <Rating
                                  value={getConfidenceRating(rec.confidence ?? 0)}
                                  precision={0.5}
                                  readOnly
                                  size="small"
                                />
                              </Box>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">
                  لا توجد توصيات متاحة. يرجى تعديل معايير البحث وإعادة المحاولة.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Recommendations;