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
  FilterList as FilterIcon,
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon
} from '@mui/icons-material';

// Charts
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend
} from 'recharts';

// Redux actions
import { fetchFinancialData, setSymbols, clearFinancialData } from '../store/slices/financialSlice';

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

// Empty fallback structure when API data is unavailable
const EMPTY_FINANCIAL_DATA = {
  income:    { annual: [], quarterly: [] },
  balance:   { annual: [], quarterly: [] },
  cash_flow: { annual: [], quarterly: [] },
};

// Tab panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`financial-tabpanel-${index}`}
      aria-labelledby={`financial-tab-${index}`}
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

const FinancialData = () => {
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
  } = useSelector((state) => state.financial);
  
  // Local state
  const [selectedStock, setSelectedStock] = useState(null);
  const [statementType, setStatementType] = useState('income');
  const [period, setPeriod] = useState('annual');
  const [tabValue, setTabValue] = useState(0);
  
  // Statement type options
  const statementTypeOptions = [
    { value: 'income', label: 'قائمة الدخل' },
    { value: 'balance', label: 'الميزانية العمومية' },
    { value: 'cash_flow', label: 'التدفقات النقدية' }
  ];
  
  // Period options
  const periodOptions = [
    { value: 'annual', label: 'سنوي' },
    { value: 'quarterly', label: 'ربع سنوي' }
  ];
  
  // Handle form changes
  const handleStockChange = (event, newValue) => {
    setSelectedStock(newValue);
  };
  
  const handleStatementTypeChange = (event) => {
    setStatementType(event.target.value);
  };
  
  const handlePeriodChange = (event) => {
    setPeriod(event.target.value);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Fetch financial data
  const fetchData = () => {
    if (selectedStock) {
      dispatch(fetchFinancialData({
        symbols: [selectedStock.symbol],
        statementTypes: [statementType],
        periods: [period]
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
      dispatch(clearFinancialData());
    };
  }, [dispatch]);
  
  // Format large numbers
  const formatNumber = (num) => {
    if (num >= 1000000000) {
      return `${(num / 1000000000).toFixed(2)} مليار`;
    } else if (num >= 1000000) {
      return `${(num / 1000000).toFixed(2)} مليون`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(2)} ألف`;
    }
    return num.toFixed(2);
  };
  
  // Compute financial ratios from API data
  const financialRatios = useMemo(() => {
    const incomeAnnual = data?.income?.annual ?? [];
    const balanceAnnual = data?.balance?.annual ?? [];
    if (incomeAnnual.length === 0 || balanceAnnual.length === 0) return null;

    const income  = incomeAnnual[0]  ?? {};
    const balance = balanceAnnual[0] ?? {};

    const revenue          = parseFloat(income.revenue ?? 0);
    const netIncome        = parseFloat(income.netIncome ?? 0);
    const totalAssets      = parseFloat(balance.assets ?? balance.totalAssets ?? 0);
    const totalLiabilities = parseFloat(balance.liabilities ?? balance.totalLiabilities ?? 0);
    const equity           = parseFloat(balance.equity ?? balance.totalEquity ?? 0);
    const currentAssets    = parseFloat(balance.currentAssets ?? 0);
    const currentLiab      = parseFloat(balance.currentLiabilities ?? 0);

    return {
      currentRatio: currentLiab  ? +(currentAssets / currentLiab).toFixed(2)      : null,
      debtToEquity: equity       ? +(totalLiabilities / equity).toFixed(2)         : null,
      roa:          totalAssets  ? +(netIncome / totalAssets * 100).toFixed(2)      : null,
      roe:          equity       ? +(netIncome / equity * 100).toFixed(2)           : null,
      npm:          revenue      ? +(netIncome / revenue * 100).toFixed(2)          : null,
    };
  }, [data]);

  // Derive ratio trend chart from annual income + balance data
  const ratioChartData = useMemo(() => {
    const incomeAnnual  = data?.income?.annual  ?? [];
    const balanceAnnual = data?.balance?.annual ?? [];
    if (incomeAnnual.length === 0) return [];

    return [...incomeAnnual].reverse().slice(0, 5).map((income) => {
      const balance  = balanceAnnual.find(b => b.period === income.period) ?? {};
      const revenue  = parseFloat(income.revenue  ?? 0);
      const net      = parseFloat(income.netIncome ?? 0);
      const assets   = parseFloat(balance.assets  ?? balance.totalAssets  ?? 0);
      const eq       = parseFloat(balance.equity  ?? balance.totalEquity  ?? 0);
      return {
        period: income.period ?? '',
        roe: eq     ? +(net / eq     * 100).toFixed(2) : 0,
        roa: assets ? +(net / assets * 100).toFixed(2) : 0,
        npm: revenue? +(net / revenue* 100).toFixed(2) : 0,
      };
    }).filter(d => d.period);
  }, [data]);

  // Evaluate ratio quality
  const evalRatio = (key, value) => {
    if (value === null) return '—';
    if (key === 'currentRatio')  return value >= 1.5 ? 'جيد' : value >= 1 ? 'متوسط' : 'ضعيف';
    if (key === 'debtToEquity')  return value <= 0.5 ? 'جيد' : value <= 1 ? 'متوسط' : 'ضعيف';
    if (key === 'roa')           return value >= 8   ? 'جيد' : value >= 4  ? 'متوسط' : 'ضعيف';
    if (key === 'roe')           return value >= 12  ? 'جيد' : value >= 6  ? 'متوسط' : 'ضعيف';
    if (key === 'npm')           return value >= 15  ? 'جيد' : value >= 7  ? 'متوسط' : 'ضعيف';
    return '—';
  };

  // Get financial statement data from Redux state (falls back to empty array)
  const getFinancialData = () => {
    const source = (data && Object.keys(data).length > 0) ? data : EMPTY_FINANCIAL_DATA;
    return source?.[statementType]?.[period] ?? [];
  };
  
  // Get chart data based on statement type
  const getChartData = () => {
    const financialData = getFinancialData();
    
    switch (statementType) {
      case 'income':
        return financialData.map(item => ({
          period: item.period,
          revenue: item.revenue,
          netIncome: item.netIncome,
          grossProfit: item.grossProfit
        }));
      case 'balance':
        return financialData.map(item => ({
          period: item.period,
          assets: item.assets,
          liabilities: item.liabilities,
          equity: item.equity
        }));
      case 'cash_flow':
        return financialData.map(item => ({
          period: item.period,
          operatingCashFlow: item.operatingCashFlow,
          investingCashFlow: Math.abs(item.investingCashFlow), // Make positive for chart
          financingCashFlow: Math.abs(item.financingCashFlow), // Make positive for chart
          netCashFlow: item.netCashFlow
        }));
      default:
        return [];
    }
  };
  
  // Get table columns based on statement type
  const getTableColumns = () => {
    switch (statementType) {
      case 'income':
        return [
          { id: 'period', label: 'الفترة' },
          { id: 'revenue', label: 'الإيرادات' },
          { id: 'cogs', label: 'تكلفة المبيعات' },
          { id: 'grossProfit', label: 'إجمالي الربح' },
          { id: 'operatingExpenses', label: 'مصاريف التشغيل' },
          { id: 'operatingIncome', label: 'الدخل التشغيلي' },
          { id: 'netIncome', label: 'صافي الدخل' }
        ];
      case 'balance':
        return [
          { id: 'period', label: 'الفترة' },
          { id: 'assets', label: 'الأصول' },
          { id: 'liabilities', label: 'الالتزامات' },
          { id: 'equity', label: 'حقوق الملكية' }
        ];
      case 'cash_flow':
        return [
          { id: 'period', label: 'الفترة' },
          { id: 'operatingCashFlow', label: 'التدفق النقدي التشغيلي' },
          { id: 'investingCashFlow', label: 'التدفق النقدي الاستثماري' },
          { id: 'financingCashFlow', label: 'التدفق النقدي التمويلي' },
          { id: 'netCashFlow', label: 'صافي التدفق النقدي' }
        ];
      default:
        return [];
    }
  };
  
  // Get chart colors based on statement type
  const getChartColors = () => {
    switch (statementType) {
      case 'income':
        return {
          revenue: theme.palette.primary.main,
          netIncome: theme.palette.success.main,
          grossProfit: theme.palette.info.main
        };
      case 'balance':
        return {
          assets: theme.palette.primary.main,
          liabilities: theme.palette.error.main,
          equity: theme.palette.success.main
        };
      case 'cash_flow':
        return {
          operatingCashFlow: theme.palette.success.main,
          investingCashFlow: theme.palette.error.main,
          financingCashFlow: theme.palette.warning.main,
          netCashFlow: theme.palette.primary.main
        };
      default:
        return {};
    }
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('financial.title')}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stock Selection */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="اختيار البيانات المالية" 
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
                    <InputLabel id="statement-type-label">
                      نوع القائمة المالية
                    </InputLabel>
                    <Select
                      labelId="statement-type-label"
                      id="statement-type"
                      value={statementType}
                      label="نوع القائمة المالية"
                      onChange={handleStatementTypeChange}
                    >
                      {statementTypeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel id="period-label">
                      الفترة
                    </InputLabel>
                    <Select
                      labelId="period-label"
                      id="period"
                      value={period}
                      label="الفترة"
                      onChange={handlePeriodChange}
                    >
                      {periodOptions.map((option) => (
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
                      عرض البيانات
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Financial Data */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title={selectedStock ? `البيانات المالية لـ ${selectedStock.name} (${selectedStock.symbol})` : 'البيانات المالية'}
              titleTypographyProps={{ variant: 'h6' }}
              subheader={`${statementTypeOptions.find(opt => opt.value === statementType)?.label} - ${periodOptions.find(opt => opt.value === period)?.label}`}
            />
            <Divider />
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="financial data tabs">
                  <Tab label="الرسم البياني" />
                  <Tab label="الجدول" />
                </Tabs>
              </Box>
              
              {/* Chart Tab */}
              <TabPanel value={tabValue} index={0}>
                <Box sx={{ height: 400 }}>
                  {status === 'loading' ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                      <CircularProgress />
                    </Box>
                  ) : status === 'failed' ? (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {error || 'حدث خطأ أثناء جلب البيانات المالية'}
                    </Alert>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      {statementType === 'income' ? (
                        <BarChart
                          data={getChartData()}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period" />
                          <YAxis />
                          <RechartsTooltip formatter={(value) => formatNumber(value)} />
                          <Legend />
                          <Bar dataKey="revenue" name="الإيرادات" fill={getChartColors().revenue} />
                          <Bar dataKey="grossProfit" name="إجمالي الربح" fill={getChartColors().grossProfit} />
                          <Bar dataKey="netIncome" name="صافي الدخل" fill={getChartColors().netIncome} />
                        </BarChart>
                      ) : statementType === 'balance' ? (
                        <BarChart
                          data={getChartData()}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period" />
                          <YAxis />
                          <RechartsTooltip formatter={(value) => formatNumber(value)} />
                          <Legend />
                          <Bar dataKey="assets" name="الأصول" fill={getChartColors().assets} />
                          <Bar dataKey="liabilities" name="الالتزامات" fill={getChartColors().liabilities} />
                          <Bar dataKey="equity" name="حقوق الملكية" fill={getChartColors().equity} />
                        </BarChart>
                      ) : (
                        <BarChart
                          data={getChartData()}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period" />
                          <YAxis />
                          <RechartsTooltip formatter={(value, name) => {
                            if (name === 'investingCashFlow' || name === 'financingCashFlow') {
                              return [`${formatNumber(value * -1)} (سالب)`, name === 'investingCashFlow' ? 'التدفق النقدي الاستثماري' : 'التدفق النقدي التمويلي'];
                            }
                            return [formatNumber(value), name === 'operatingCashFlow' ? 'التدفق النقدي التشغيلي' : 'صافي التدفق النقدي'];
                          }} />
                          <Legend />
                          <Bar dataKey="operatingCashFlow" name="التدفق النقدي التشغيلي" fill={getChartColors().operatingCashFlow} />
                          <Bar dataKey="investingCashFlow" name="التدفق النقدي الاستثماري (سالب)" fill={getChartColors().investingCashFlow} />
                          <Bar dataKey="financingCashFlow" name="التدفق النقدي التمويلي (سالب)" fill={getChartColors().financingCashFlow} />
                          <Line type="monotone" dataKey="netCashFlow" name="صافي التدفق النقدي" stroke={getChartColors().netCashFlow} strokeWidth={2} />
                        </BarChart>
                      )}
                    </ResponsiveContainer>
                  )}
                </Box>
              </TabPanel>
              
              {/* Table Tab */}
              <TabPanel value={tabValue} index={1}>
                {status === 'loading' ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                  </Box>
                ) : status === 'failed' ? (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error || 'حدث خطأ أثناء جلب البيانات المالية'}
                  </Alert>
                ) : (
                  <TableContainer component={Paper} sx={{ mt: 2 }}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          {getTableColumns().map((column) => (
                            <TableCell key={column.id}>{column.label}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {getFinancialData().map((row, index) => (
                          <TableRow key={index}>
                            {getTableColumns().map((column) => (
                              <TableCell key={column.id}>
                                {column.id === 'period' ? row[column.id] : formatNumber(row[column.id])}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </TabPanel>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Financial Ratios */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="النسب المالية" 
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
                  {error || 'حدث خطأ أثناء جلب البيانات المالية'}
                </Alert>
              ) : !financialRatios ? (
                <Alert severity="info">
                    اختر سهماً لعرض النسب المالية المحسوبة من البيانات الفعلية.
                  </Alert>
              ) : (
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>النسبة</TableCell>
                              <TableCell>القيمة</TableCell>
                              <TableCell>التقييم</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {[
                              { key: 'currentRatio', label: 'نسبة السيولة',                  suffix: ''  },
                              { key: 'debtToEquity', label: 'الديون إلى حقوق الملكية',       suffix: ''  },
                              { key: 'roa',          label: 'العائد على الأصول (ROA)',        suffix: '%' },
                              { key: 'roe',          label: 'العائد على حقوق الملكية (ROE)', suffix: '%' },
                              { key: 'npm',          label: 'هامش الربح الصافي',             suffix: '%' },
                            ].map(({ key, label, suffix }) => {
                              const val  = financialRatios[key];
                              const eval_ = evalRatio(key, val);
                              return (
                                <TableRow key={key}>
                                  <TableCell>{label}</TableCell>
                                  <TableCell>{val !== null ? `${val}${suffix}` : '—'}</TableCell>
                                  <TableCell
                                    sx={{ color:
                                      eval_ === 'جيد'   ? 'success.main' :
                                      eval_ === 'ضعيف'  ? 'error.main'   : 'warning.main' }}
                                  >
                                    {eval_}
                                  </TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Box sx={{ height: 300 }}>
                        {ratioChartData.length > 0 ? (
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={ratioChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="period" />
                              <YAxis />
                              <RechartsTooltip formatter={(value) => `${value}%`} />
                              <Legend />
                              <Line type="monotone" dataKey="roe" name="العائد على حقوق الملكية" stroke={theme.palette.primary.main} activeDot={{ r: 8 }} />
                              <Line type="monotone" dataKey="roa" name="العائد على الأصول"        stroke={theme.palette.success.main} activeDot={{ r: 8 }} />
                              <Line type="monotone" dataKey="npm" name="هامش الربح الصافي"        stroke={theme.palette.warning.main} activeDot={{ r: 8 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        ) : (
                          <Alert severity="info">لا توجد بيانات كافية لرسم اتجاه النسب.</Alert>
                        )}
                      </Box>
                    </Grid>
                  </Grid>
                )
              }
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FinancialData;
