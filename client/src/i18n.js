import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translations
const resources = {
  ar: {
    translation: {
      // Common
      'app.title': 'نظام تحليل الأسهم السعودية',
      'app.shortTitle': 'تاسي3',
      'app.footer': '© 2025 نظام تاسي3 - جميع الحقوق محفوظة',
      
      // Navigation
      'nav.dashboard': 'لوحة المعلومات',
      'nav.recommendations': 'التوصيات',
      'nav.technical': 'التحليل الفني',
      'nav.fundamental': 'التحليل الأساسي',
      'nav.market': 'بيانات السوق',
      'nav.financial': 'البيانات المالية',
      'nav.sentiment': 'تحليل المشاعر',
      'nav.portfolio': 'المحفظة',
      'nav.settings': 'الإعدادات',
      
      // Dashboard
      'dashboard.marketOverview': 'نظرة عامة على السوق',
      'dashboard.topGainers': 'الأكثر ارتفاعاً',
      'dashboard.topLosers': 'الأكثر انخفاضاً',
      'dashboard.marketSentiment': 'مشاعر السوق',
      'dashboard.sectorPerformance': 'أداء القطاعات',
      'dashboard.recentRecommendations': 'أحدث التوصيات',
      
      // Recommendations
      'recommendations.title': 'توصيات الاستثمار',
      'recommendations.riskProfile': 'ملف المخاطر',
      'recommendations.investmentHorizon': 'أفق الاستثمار',
      'recommendations.sectors': 'القطاعات',
      'recommendations.generate': 'إنشاء التوصيات',
      
      // Technical Analysis
      'technical.title': 'التحليل الفني',
      'technical.indicators': 'المؤشرات',
      'technical.timeframe': 'الإطار الزمني',
      'technical.trend': 'الاتجاه',
      'technical.support': 'مستويات الدعم',
      'technical.resistance': 'مستويات المقاومة',
      
      // Fundamental Analysis
      'fundamental.title': 'التحليل الأساسي',
      'fundamental.metrics': 'المقاييس',
      'fundamental.valuation': 'التقييم',
      'fundamental.comparison': 'المقارنة القطاعية',
      
      // Market Data
      'market.title': 'بيانات السوق',
      'market.price': 'السعر',
      'market.volume': 'الحجم',
      'market.marketCap': 'القيمة السوقية',
      'market.change': 'التغيير',
      
      // Financial Data
      'financial.title': 'البيانات المالية',
      'financial.income': 'قائمة الدخل',
      'financial.balance': 'الميزانية العمومية',
      'financial.cashFlow': 'التدفق النقدي',
      'financial.revenue': 'الإيرادات',
      'financial.netIncome': 'صافي الدخل',
      'financial.eps': 'ربحية السهم',
      
      // Sentiment Analysis
      'sentiment.title': 'تحليل المشاعر',
      'sentiment.news': 'الأخبار',
      'sentiment.socialMedia': 'وسائل التواصل الاجتماعي',
      'sentiment.analystRatings': 'تقييمات المحللين',
      'sentiment.overallScore': 'النتيجة الإجمالية',
      
      // Settings
      'settings.title': 'الإعدادات',
      'settings.profile': 'الملف الشخصي',
      'settings.appearance': 'المظهر',
      'settings.language': 'اللغة',
      'settings.darkMode': 'الوضع الليلي',
      'settings.notifications': 'الإشعارات',
      'settings.security': 'الأمان',
      'settings.dataManagement': 'إدارة البيانات',
      'settings.saveChanges': 'حفظ التغييرات',
      
      // Status messages
      'status.loading': 'جاري التحميل...',
      'status.error': 'حدث خطأ',
      'status.success': 'تم بنجاح',
      'status.noData': 'لا توجد بيانات متاحة',
      
      // Actions
      'action.search': 'بحث',
      'action.filter': 'تصفية',
      'action.apply': 'تطبيق',
      'action.reset': 'إعادة تعيين',
      'action.save': 'حفظ',
      'action.cancel': 'إلغاء',
      'action.edit': 'تعديل',
      'action.delete': 'حذف',
      'action.add': 'إضافة',
      'action.view': 'عرض',
      'action.download': 'تنزيل',
      'action.share': 'مشاركة',
      
      // Stock recommendations
      'stock.buy': 'شراء',
      'stock.sell': 'بيع',
      'stock.hold': 'احتفاظ',
      'stock.targetPrice': 'السعر المستهدف',
      'stock.potential': 'الإمكانات',
      'stock.riskScore': 'درجة المخاطرة',
      'stock.confidence': 'مستوى الثقة',
    }
  },
  en: {
    translation: {
      // Common
      'app.title': 'Saudi Stock Market Analysis System',
      'app.shortTitle': 'TASI3',
      'app.footer': '© 2025 TASI3 - All rights reserved',
      
      // Navigation
      'nav.dashboard': 'Dashboard',
      'nav.recommendations': 'Recommendations',
      'nav.technical': 'Technical Analysis',
      'nav.fundamental': 'Fundamental Analysis',
      'nav.market': 'Market Data',
      'nav.financial': 'Financial Data',
      'nav.sentiment': 'Sentiment Analysis',
      'nav.portfolio': 'Portfolio',
      'nav.settings': 'Settings',
      
      // Dashboard
      'dashboard.marketOverview': 'Market Overview',
      'dashboard.topGainers': 'Top Gainers',
      'dashboard.topLosers': 'Top Losers',
      'dashboard.marketSentiment': 'Market Sentiment',
      'dashboard.sectorPerformance': 'Sector Performance',
      'dashboard.recentRecommendations': 'Recent Recommendations',
      
      // Recommendations
      'recommendations.title': 'Investment Recommendations',
      'recommendations.riskProfile': 'Risk Profile',
      'recommendations.investmentHorizon': 'Investment Horizon',
      'recommendations.sectors': 'Sectors',
      'recommendations.generate': 'Generate Recommendations',
      
      // Technical Analysis
      'technical.title': 'Technical Analysis',
      'technical.indicators': 'Indicators',
      'technical.timeframe': 'Timeframe',
      'technical.trend': 'Trend',
      'technical.support': 'Support Levels',
      'technical.resistance': 'Resistance Levels',
      
      // Fundamental Analysis
      'fundamental.title': 'Fundamental Analysis',
      'fundamental.metrics': 'Metrics',
      'fundamental.valuation': 'Valuation',
      'fundamental.comparison': 'Sector Comparison',
      
      // Market Data
      'market.title': 'Market Data',
      'market.price': 'Price',
      'market.volume': 'Volume',
      'market.marketCap': 'Market Cap',
      'market.change': 'Change',
      
      // Financial Data
      'financial.title': 'Financial Data',
      'financial.income': 'Income Statement',
      'financial.balance': 'Balance Sheet',
      'financial.cashFlow': 'Cash Flow',
      'financial.revenue': 'Revenue',
      'financial.netIncome': 'Net Income',
      'financial.eps': 'EPS',
      
      // Sentiment Analysis
      'sentiment.title': 'Sentiment Analysis',
      'sentiment.news': 'News',
      'sentiment.socialMedia': 'Social Media',
      'sentiment.analystRatings': 'Analyst Ratings',
      'sentiment.overallScore': 'Overall Score',
      
      // Settings
      'settings.title': 'Settings',
      'settings.profile': 'Profile',
      'settings.appearance': 'Appearance',
      'settings.language': 'Language',
      'settings.darkMode': 'Dark Mode',
      'settings.notifications': 'Notifications',
      'settings.security': 'Security',
      'settings.dataManagement': 'Data Management',
      'settings.saveChanges': 'Save Changes',
      
      // Status messages
      'status.loading': 'Loading...',
      'status.error': 'An error occurred',
      'status.success': 'Success',
      'status.noData': 'No data available',
      
      // Actions
      'action.search': 'Search',
      'action.filter': 'Filter',
      'action.apply': 'Apply',
      'action.reset': 'Reset',
      'action.save': 'Save',
      'action.cancel': 'Cancel',
      'action.edit': 'Edit',
      'action.delete': 'Delete',
      'action.add': 'Add',
      'action.view': 'View',
      'action.download': 'Download',
      'action.share': 'Share',
      
      // Stock recommendations
      'stock.buy': 'Buy',
      'stock.sell': 'Sell',
      'stock.hold': 'Hold',
      'stock.targetPrice': 'Target Price',
      'stock.potential': 'Potential',
      'stock.riskScore': 'Risk Score',
      'stock.confidence': 'Confidence',
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ar',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;