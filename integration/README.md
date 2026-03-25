# نظام تكامل TASI3

## نظرة عامة

يوفر نظام التكامل واجهة موحدة للتفاعل بين مكونات النظام المختلفة، بما في ذلك:

- محرك التوصيات (Recommendation Engine)
- أنظمة التحليل الفني والأساسي (Technical & Fundamental Analysis)
- أنظمة جمع ومعالجة البيانات (Data Collection & Processing)

## هيكل النظام

يتكون نظام التكامل من المكونات التالية:

### 1. نظام التكامل الرئيسي (Python)

موقع الملف: `integration/system_integration.py`

هذا النظام يوفر واجهة برمجية موحدة للتفاعل مع جميع مكونات النظام. يقوم بتحميل المكونات المطلوبة ديناميكيًا وتنفيذ العمليات المطلوبة.

### 2. خدمة التكامل في الواجهة الخلفية (Backend Integration Service)

موقع الملف: `backend/app/Services/Integration/SystemIntegrationService.php`

هذه الخدمة توفر واجهة برمجية للتفاعل مع مكونات النظام المختلفة من خلال PHP. تتضمن الوظائف التالية:

- `executeRecommendationEngine`: تنفيذ محرك التوصيات
- `executeTechnicalAnalysis`: تنفيذ التحليل الفني
- `executeFundamentalAnalysis`: تنفيذ التحليل الأساسي
- `collectData`: جمع البيانات المالية والسوقية
- `processFinancialData`: معالجة البيانات المالية

### 3. واجهة برمجة التطبيقات للتكامل (Integration API)

موقع الملف: `backend/app/Http/Controllers/Integration/IntegrationController.php`

هذا المتحكم يوفر نقاط نهاية RESTful API للتفاعل مع خدمة التكامل:

- `POST /api/v1/integration/recommendations`: الحصول على توصيات الاستثمار
- `POST /api/v1/integration/technical-analysis`: الحصول على التحليل الفني
- `POST /api/v1/integration/fundamental-analysis`: الحصول على التحليل الأساسي
- `POST /api/v1/integration/collect-data`: جمع البيانات المالية
- `POST /api/v1/integration/process-data`: معالجة البيانات المالية

## كيفية الاستخدام

### استخدام واجهة برمجة التطبيقات للتكامل

#### الحصول على توصيات الاستثمار

```http
POST /api/v1/integration/recommendations
Content-Type: application/json

{
  "risk_profile": "moderate",
  "investment_horizon": "medium",
  "sectors": ["technology", "healthcare"],
  "exclude_symbols": ["AAPL", "MSFT"],
  "max_results": 10
}
```

#### الحصول على التحليل الفني

```http
POST /api/v1/integration/technical-analysis
Content-Type: application/json

{
  "symbol": "2222.SR",
  "indicators": ["SMA", "RSI", "MACD"],
  "timeframe": "daily"
}
```

#### الحصول على التحليل الأساسي

```http
POST /api/v1/integration/fundamental-analysis
Content-Type: application/json

{
  "symbol": "2222.SR",
  "metrics": ["PE", "PB", "ROE", "EPS"]
}
```

#### جمع البيانات المالية

```http
POST /api/v1/integration/collect-data
Content-Type: application/json

{
  "symbols": ["2222.SR", "1211.SR"],
  "data_type": "market"
}
```

#### معالجة البيانات المالية

```http
POST /api/v1/integration/process-data
Content-Type: application/json

{
  "data": { ... },
  "processing_type": "normalization"
}
```

## استخدام نظام التكامل الرئيسي مباشرة

يمكن استخدام نظام التكامل الرئيسي مباشرة من خلال استدعاء البرنامج النصي مع معلمات JSON:

```bash
python integration/system_integration.py '{"action": "recommend", "risk_profile": "moderate", "investment_horizon": "medium"}'
```

```bash
python integration/system_integration.py '{"action": "technical_analysis", "symbol": "2222.SR", "indicators": ["SMA", "RSI"]}'
```

```bash
python integration/system_integration.py '{"action": "fundamental_analysis", "symbol": "2222.SR", "metrics": ["PE", "PB"]}'
```

```bash
python integration/system_integration.py '{"action": "collect_market_data", "symbols": ["2222.SR", "1211.SR"]}'
```

## ملاحظات التنفيذ

- جميع وحدات التكامل تستخدم JSON لتبادل البيانات
- يتم التعامل مع الأخطاء بشكل موحد عبر جميع المكونات
- تتضمن جميع الاستجابات حقل `success` للإشارة إلى نجاح أو فشل العملية
- في حالة الفشل، يتم تضمين رسالة خطأ في حقل `error`
- يتم تسجيل جميع الأخطاء في ملفات السجل للتشخيص

## متطلبات النظام

- PHP 7.4 أو أحدث
- Python 3.8 أو أحدث
- Laravel 8.x أو أحدث
- حزم Python المطلوبة:
  - pandas
  - numpy
  - scikit-learn
  - matplotlib
  - ta-lib (للتحليل الفني)