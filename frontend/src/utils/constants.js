// API URLs
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Chart colors
export const CHART_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
  background: '#f5f5f5',
  text: '#333333',
  grid: '#dddddd',
  upTrend: '#4caf50',
  downTrend: '#f44336',
  neutral: '#9e9e9e'
};

// Time frames
export const TIME_FRAMES = [
  { value: '1d', label: 'يوم واحد' },
  { value: '1w', label: 'أسبوع' },
  { value: '1m', label: 'شهر' },
  { value: '3m', label: 'ثلاثة أشهر' },
  { value: '6m', label: 'ستة أشهر' },
  { value: '1y', label: 'سنة' },
  { value: '5y', label: 'خمس سنوات' },
  { value: 'max', label: 'الكل' }
];

// Technical indicators
export const TECHNICAL_INDICATORS = [
  { value: 'sma', label: 'المتوسط المتحرك البسيط (SMA)' },
  { value: 'ema', label: 'المتوسط المتحرك الأسي (EMA)' },
  { value: 'macd', label: 'تقارب وتباعد المتوسطات المتحركة (MACD)' },
  { value: 'rsi', label: 'مؤشر القوة النسبية (RSI)' },
  { value: 'bollinger', label: 'نطاقات بولينجر (Bollinger Bands)' },
  { value: 'stochastic', label: 'مذبذب ستوكاستيك (Stochastic Oscillator)' },
  { value: 'adx', label: 'مؤشر الاتجاه المتوسط (ADX)' },
  { value: 'fibonacci', label: 'مستويات فيبوناتشي (Fibonacci)' }
];

// Recommendation types
export const RECOMMENDATION_TYPES = [
  { value: 'technical', label: 'فني' },
  { value: 'fundamental', label: 'أساسي' },
  { value: 'mixed', label: 'مختلط' }
];

// Recommendation actions
export const RECOMMENDATION_ACTIONS = [
  { value: 'buy', label: 'شراء' },
  { value: 'sell', label: 'بيع' },
  { value: 'hold', label: 'احتفاظ' }
];

// Sectors
export const SECTORS = [
  { value: 'energy', label: 'الطاقة' },
  { value: 'materials', label: 'المواد الأساسية' },
  { value: 'industrials', label: 'الصناعات' },
  { value: 'consumer_discretionary', label: 'السلع الكمالية' },
  { value: 'consumer_staples', label: 'السلع الاستهلاكية الأساسية' },
  { value: 'healthcare', label: 'الرعاية الصحية' },
  { value: 'financials', label: 'المالية' },
  { value: 'information_technology', label: 'تقنية المعلومات' },
  { value: 'communication_services', label: 'خدمات الاتصالات' },
  { value: 'utilities', label: 'المرافق العامة' },
  { value: 'real_estate', label: 'العقارات' }
];