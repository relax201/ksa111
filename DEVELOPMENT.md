# دليل المطور لنظام TASI3

هذا الدليل مخصص للمطورين الذين يرغبون في المساهمة في تطوير نظام TASI3 أو تخصيصه حسب احتياجاتهم. يوفر هذا الدليل نظرة عامة على هيكل المشروع، وتقنيات التطوير المستخدمة، وأفضل الممارسات للتطوير.

## هيكل المشروع

```
tasi3/
├── api.php                  # نقطة دخول API الرئيسية
├── config/                  # ملفات التكوين
│   ├── config.php           # إعدادات التطبيق الرئيسية
│   └── database.php         # إعدادات قاعدة البيانات
├── database/                # ملفات قاعدة البيانات
│   ├── migrations/          # ملفات ترحيل قاعدة البيانات
│   └── schema.sql           # هيكل قاعدة البيانات
├── integration/             # تكامل مع Python
│   ├── bridge.php           # جسر بين PHP و Python
│   ├── mock_integration.py  # محاكاة للتكامل (للتطوير)
│   └── requirements.txt     # متطلبات Python
├── public/                  # الملفات العامة (واجهة المستخدم المبنية)
├── src/                     # كود PHP الأساسي
│   ├── Controllers/         # وحدات التحكم
│   ├── Models/              # النماذج
│   ├── Services/            # الخدمات
│   └── Utils/               # أدوات مساعدة
├── tests/                   # اختبارات
│   ├── Unit/                # اختبارات الوحدة
│   └── Integration/         # اختبارات التكامل
├── vendor/                  # حزم Composer (تم تجاهلها في Git)
├── client/                  # مشروع واجهة المستخدم (React)
│   ├── public/              # ملفات عامة لواجهة المستخدم
│   ├── src/                 # كود المصدر لواجهة المستخدم
│   │   ├── components/      # مكونات React
│   │   ├── pages/           # صفحات التطبيق
│   │   ├── store/           # إدارة الحالة (Redux)
│   │   ├── services/        # خدمات API
│   │   ├── utils/           # أدوات مساعدة
│   │   └── App.js           # مكون التطبيق الرئيسي
│   ├── package.json         # تبعيات Node.js
│   └── .env                 # متغيرات البيئة
├── logs/                    # سجلات التطبيق
├── composer.json            # تبعيات PHP
├── .gitignore               # ملفات مستثناة من Git
└── README.md                # توثيق المشروع
```

## التقنيات المستخدمة

### الخلفية (Backend)
- **PHP 7.4+**: لغة البرمجة الأساسية للخلفية
- **MySQL/MariaDB**: قاعدة البيانات الرئيسية
- **Python 3.8+**: لعمليات التحليل المتقدمة
- **Composer**: لإدارة تبعيات PHP

### واجهة المستخدم (Frontend)
- **React 18**: مكتبة JavaScript لبناء واجهات المستخدم
- **Redux**: لإدارة حالة التطبيق
- **Material-UI**: مكتبة مكونات واجهة المستخدم
- **Lightweight Charts**: مكتبة للرسوم البيانية المالية
- **Axios**: لطلبات HTTP
- **i18next**: للترجمة وتعدد اللغات

## إعداد بيئة التطوير

### متطلبات التطوير
- **IDE/محرر النصوص**: Visual Studio Code, PhpStorm, أو أي محرر آخر
- **أدوات التحكم بالإصدار**: Git
- **أدوات التطوير**: Node.js, npm, Composer, Python
- **أدوات الاختبار**: PHPUnit, Jest
- **أدوات التصحيح**: Xdebug, React Developer Tools, Redux DevTools

### إعداد بيئة التطوير المحلية

1. **استنساخ المستودع**:
```bash
git clone https://github.com/your-repo/tasi3.git
cd tasi3
```

2. **إعداد الخلفية**:
```bash
composer install
cp config/config.example.php config/config.php
# قم بتعديل ملف config.php حسب إعدادات بيئتك المحلية
```

3. **إعداد قاعدة البيانات**:
```bash
# إنشاء قاعدة بيانات للتطوير
mysql -u root -p -e "CREATE DATABASE tasi3_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON tasi3_dev.* TO 'tasi3_user'@'localhost';"
mysql -u tasi3_user -p tasi3_dev < database/schema.sql
```

4. **إعداد بيئة Python**:
```bash
pip install -r integration/requirements.txt
```

5. **إعداد واجهة المستخدم**:
```bash
cd client
npm install
cp .env.example .env
# قم بتعديل ملف .env حسب إعدادات بيئتك المحلية
```

6. **تشغيل خوادم التطوير**:
```bash
# تشغيل خادم الخلفية (استخدم خادم PHP المدمج للتطوير)
cd /path/to/tasi3
php -S localhost:8000

# تشغيل خادم واجهة المستخدم
cd /path/to/tasi3/client
npm start
```

## أدلة التطوير

### 1. تطوير الخلفية (Backend)

#### إضافة نقطة نهاية API جديدة

1. افتح ملف `api.php` وأضف حالة جديدة في التعبير الشرطي switch:

```php
case 'new_endpoint':
    // الحصول على المعلمات من الطلب
    $param1 = $_GET['param1'] ?? 'default_value';
    $param2 = $_GET['param2'] ?? 'default_value';
    
    // معالجة المصفوفات بشكل صحيح
    $arrayParam = isset($_GET['array_param']) ? 
        (is_array($_GET['array_param']) ? $_GET['array_param'] : [$_GET['array_param']]) : [];
    
    // استدعاء دالة الجسر
    $result = callBridgeFunction($param1, $param2, $arrayParam);
    
    // تنسيق الاستجابة
    if ($result['success']) {
        $response = [
            'success' => true,
            'data' => $result['data']
        ];
    } else {
        throw new Exception($result['error'] ?? 'Failed to process request');
    }
    break;
```

2. أضف دالة جديدة في ملف `integration/bridge.php`:

```php
/**
 * وصف الدالة الجديدة
 * 
 * @param string $param1 وصف المعلمة الأولى
 * @param string $param2 وصف المعلمة الثانية
 * @param array $arrayParam وصف معلمة المصفوفة
 * @return array نتيجة العملية
 */
function callBridgeFunction(
    string $param1,
    string $param2,
    array $arrayParam = []
): array {
    $params = [
        'action' => 'new_action',
        'param1' => $param1,
        'param2' => $param2,
        'array_param' => $arrayParam
    ];
    
    return executeIntegration($params);
}
```

3. أضف معالجة للإجراء الجديد في ملف `integration/mock_integration.py`:

```python
elif action == 'new_action':
    param1 = params.get('param1', 'default_value')
    param2 = params.get('param2', 'default_value')
    array_param = params.get('array_param', [])
    
    # معالجة البيانات
    result_data = {
        'processed_param1': process_param1(param1),
        'processed_param2': process_param2(param2),
        'processed_array': process_array(array_param)
    }
    
    result = {
        'success': True,
        'data': result_data
    }
```

#### إضافة نموذج جديد

1. أنشئ ملف جديد في مجلد `src/Models`:

```php
<?php
// src/Models/NewModel.php

namespace TASI3\Models;

class NewModel {
    private $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    /**
     * وصف الدالة
     * 
     * @param int $id معرف العنصر
     * @return array بيانات العنصر
     */
    public function getItem(int $id): array {
        $stmt = $this->db->prepare("SELECT * FROM items WHERE id = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows === 0) {
            return [];
        }
        
        return $result->fetch_assoc();
    }
    
    /**
     * إضافة عنصر جديد
     * 
     * @param string $name اسم العنصر
     * @param string $description وصف العنصر
     * @return int معرف العنصر الجديد
     */
    public function addItem(string $name, string $description): int {
        $stmt = $this->db->prepare("INSERT INTO items (name, description) VALUES (?, ?)");
        $stmt->bind_param("ss", $name, $description);
        $stmt->execute();
        
        return $this->db->insert_id;
    }
}
```

### 2. تطوير واجهة المستخدم (Frontend)

#### إضافة صفحة جديدة

1. أنشئ ملف جديد في مجلد `client/src/pages`:

```jsx
// client/src/pages/NewPage.js
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button
} from '@mui/material';
import { fetchData } from '../store/slices/dataSlice';

const NewPage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { data, status, error } = useSelector((state) => state.data);
  
  useEffect(() => {
    dispatch(fetchData());
  }, [dispatch]);
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('newPage.title')}
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">
                {t('newPage.cardTitle')}
              </Typography>
              
              {status === 'loading' && <p>{t('common.loading')}</p>}
              {status === 'failed' && <p>{t('common.error')}: {error}</p>}
              
              {status === 'succeeded' && (
                <div>
                  {/* عرض البيانات */}
                  <pre>{JSON.stringify(data, null, 2)}</pre>
                </div>
              )}
              
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => dispatch(fetchData())}
              >
                {t('common.refresh')}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NewPage;
```

2. أضف الصفحة إلى ملف التوجيه `client/src/App.js`:

```jsx
import NewPage from './pages/NewPage';

// في مكون Routes
<Route path="/new-page" element={<NewPage />} />
```

3. أضف رابط للصفحة في القائمة الجانبية `client/src/components/Sidebar.js`:

```jsx
<ListItem 
  button 
  component={Link} 
  to="/new-page"
  selected={location.pathname === '/new-page'}
>
  <ListItemIcon>
    <NewIcon />
  </ListItemIcon>
  <ListItemText primary={t('sidebar.newPage')} />
</ListItem>
```

#### إضافة شريحة Redux جديدة

1. أنشئ ملف جديد في مجلد `client/src/store/slices`:

```jsx
// client/src/store/slices/newSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk للحصول على البيانات
export const fetchNewData = createAsyncThunk(
  'new/fetchNewData',
  async (params, { rejectWithValue }) => {
    try {
      const urlParams = new URLSearchParams();
      urlParams.append('action', 'new_endpoint');
      
      // إضافة المعلمات
      if (params.param1) urlParams.append('param1', params.param1);
      if (params.param2) urlParams.append('param2', params.param2);
      
      // معالجة المصفوفات
      if (params.arrayParam) {
        params.arrayParam.forEach(item => {
          urlParams.append('array_param[]', item);
        });
      }
      
      const response = await axios.get('/api.php', { params: urlParams });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch data');
    }
  }
);

const initialState = {
  data: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const newSlice = createSlice({
  name: 'new',
  initialState,
  reducers: {
    resetData: (state) => {
      state.data = null;
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNewData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchNewData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.data = action.payload;
        state.error = null;
      })
      .addCase(fetchNewData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unknown error';
      });
  }
});

export const { resetData } = newSlice.actions;
export default newSlice.reducer;
```

2. أضف الشريحة الجديدة إلى متجر Redux في `client/src/store/index.js`:

```jsx
import newReducer from './slices/newSlice';

export const store = configureStore({
  reducer: {
    // الشرائح الموجودة
    new: newReducer
  }
});
```

#### إضافة مكون جديد

1. أنشئ ملف جديد في مجلد `client/src/components`:

```jsx
// client/src/components/NewComponent.js
import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Paper } from '@mui/material';

const NewComponent = ({ title, data, onAction }) => {
  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      <Box sx={{ mt: 2 }}>
        {/* محتوى المكون */}
        {data && (
          <pre>{JSON.stringify(data, null, 2)}</pre>
        )}
      </Box>
      
      <Box sx={{ mt: 2 }}>
        <Button 
          variant="contained" 
          color="primary"
          onClick={onAction}
        >
          Perform Action
        </Button>
      </Box>
    </Paper>
  );
};

NewComponent.propTypes = {
  title: PropTypes.string.isRequired,
  data: PropTypes.object,
  onAction: PropTypes.func.isRequired
};

NewComponent.defaultProps = {
  data: null
};

export default NewComponent;
```

### 3. تطوير تكامل Python

#### إضافة وظيفة تحليل جديدة

1. أنشئ ملف جديد في مجلد `integration`:

```python
# integration/analysis_module.py
import pandas as pd
import numpy as np
from datetime import datetime

def perform_new_analysis(data, params):
    """
    تنفيذ تحليل جديد على البيانات
    
    Args:
        data (dict): البيانات المراد تحليلها
        params (dict): معلمات التحليل
    
    Returns:
        dict: نتائج التحليل
    """
    try:
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(data)
        
        # استخراج المعلمات
        window_size = params.get('window_size', 20)
        threshold = params.get('threshold', 0.05)
        
        # تنفيذ التحليل
        df['rolling_mean'] = df['value'].rolling(window=window_size).mean()
        df['rolling_std'] = df['value'].rolling(window=window_size).std()
        df['z_score'] = (df['value'] - df['rolling_mean']) / df['rolling_std']
        
        # تحديد الإشارات
        df['signal'] = np.where(df['z_score'] > threshold, 1, 
                               np.where(df['z_score'] < -threshold, -1, 0))
        
        # تحويل النتائج إلى قاموس
        result = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signals': df['signal'].dropna().to_dict(),
            'metrics': {
                'mean': df['value'].mean(),
                'std': df['value'].std(),
                'min': df['value'].min(),
                'max': df['value'].max()
            }
        }
        
        return {
            'success': True,
            'data': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

2. استدعاء الوظيفة الجديدة في ملف `integration/mock_integration.py`:

```python
from analysis_module import perform_new_analysis

# في الدالة الرئيسية
elif action == 'new_analysis':
    data = params.get('data', {})
    analysis_params = params.get('analysis_params', {})
    
    result = perform_new_analysis(data, analysis_params)
```

## أفضل الممارسات للتطوير

### 1. إدارة الكود المصدري

- استخدم Git Flow كنموذج للتفرع:
  - `main`: فرع الإنتاج المستقر
  - `develop`: فرع التطوير الرئيسي
  - `feature/*`: فروع للميزات الجديدة
  - `bugfix/*`: فروع لإصلاح الأخطاء
  - `release/*`: فروع للإصدارات

- اتبع اتفاقية تسمية واضحة للـ commits:
  - `feat:` للميزات الجديدة
  - `fix:` لإصلاح الأخطاء
  - `docs:` للتوثيق
  - `style:` للتغييرات التي لا تؤثر على المنطق
  - `refactor:` لإعادة هيكلة الكود
  - `test:` لإضافة أو تعديل الاختبارات
  - `chore:` للتغييرات في عملية البناء أو الأدوات المساعدة

### 2. معايير الكود

#### PHP
- اتبع معايير PSR-1 و PSR-12 لتنسيق الكود
- استخدم التعليقات التوثيقية PHPDoc
- استخدم الأنواع الصريحة للمعلمات وقيم الإرجاع
- استخدم الاستثناءات لمعالجة الأخطاء

#### JavaScript/React
- استخدم ESLint مع تكوين Airbnb أو Standard
- استخدم Prettier لتنسيق الكود
- استخدم PropTypes للتحقق من أنواع الخصائص
- استخدم الدوال المسماة بدلاً من الدوال السهمية المجهولة
- استخدم الخطافات (Hooks) بشكل صحيح

#### Python
- اتبع PEP 8 لتنسيق الكود
- استخدم docstrings لتوثيق الدوال والفئات
- استخدم التعليقات النصية للأنواع (type hints)
- استخدم الاستثناءات لمعالجة الأخطاء

### 3. الاختبار

#### اختبارات الوحدة
- اكتب اختبارات للدوال والفئات المهمة
- استخدم PHPUnit لاختبار كود PHP
- استخدم Jest لاختبار كود JavaScript/React
- استخدم pytest لاختبار كود Python

#### اختبارات التكامل
- اختبر تكامل المكونات المختلفة
- اختبر تكامل الخلفية مع قاعدة البيانات
- اختبر تكامل واجهة المستخدم مع API

#### اختبارات واجهة المستخدم
- استخدم React Testing Library لاختبار مكونات React
- اختبر تفاعلات المستخدم والتغييرات في واجهة المستخدم

### 4. الأمان

- تحقق دائمًا من صحة مدخلات المستخدم
- استخدم التحضير المسبق للاستعلامات (prepared statements) لمنع هجمات حقن SQL
- استخدم CSRF tokens لمنع هجمات CSRF
- استخدم تشفير HTTPS لحماية البيانات أثناء النقل
- لا تخزن كلمات المرور بشكل نصي، استخدم دوال التجزئة المناسبة
- قم بتحديث المكتبات والتبعيات بانتظام

### 5. الأداء

- استخدم التخزين المؤقت (caching) للبيانات المتكررة
- قم بتحسين استعلامات قاعدة البيانات
- استخدم التحميل الكسول (lazy loading) للمكونات والبيانات
- قم بتحسين حجم حزم JavaScript
- استخدم تقنيات تحسين الصور

## التوثيق

- وثق جميع الدوال والفئات والمكونات
- حافظ على تحديث ملف README.md
- أضف تعليقات للكود المعقد
- وثق التغييرات المهمة في CHANGELOG.md
- أضف توثيقًا للـ API

## النشر والتحديث

### النشر
1. قم ببناء واجهة المستخدم للإنتاج:
```bash
cd client
npm run build
```

2. انسخ ملفات البناء إلى المجلد العام:
```bash
cp -r build/* ../public/
```

3. تأكد من تكوين الخادم بشكل صحيح للإنتاج:
```php
// config/config.php
return [
    'environment' => 'production',
    'debug' => false,
    // إعدادات أخرى للإنتاج
];
```

### التحديث
1. قم بعمل نسخة احتياطية قبل التحديث:
```bash
# نسخة احتياطية لقاعدة البيانات
mysqldump -u tasi3_user -p tasi3 > backup/tasi3_$(date +%Y%m%d).sql

# نسخة احتياطية للملفات
tar -czf backup/tasi3_files_$(date +%Y%m%d).tar.gz /path/to/tasi3
```

2. قم بتحديث الكود المصدري:
```bash
git pull origin main
```

3. قم بتحديث التبعيات:
```bash
composer update
cd client
npm update
```

4. قم بتنفيذ ترحيلات قاعدة البيانات (إن وجدت):
```bash
php database/migrate.php
```

5. أعد بناء واجهة المستخدم:
```bash
npm run build
cp -r build/* ../public/
```

## الخاتمة

هذا الدليل يوفر نظرة عامة على تطوير نظام TASI3. يرجى الرجوع إلى الوثائق الخاصة بكل تقنية للحصول على معلومات أكثر تفصيلاً. إذا كان لديك أي أسئلة أو اقتراحات، فلا تتردد في التواصل مع فريق التطوير.

نتطلع إلى مساهماتكم في تحسين وتطوير نظام TASI3!