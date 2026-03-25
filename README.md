# TASI3 - نظام تحليل سوق الأسهم السعودية

## نظرة عامة

TASI3 هو نظام متكامل لتحليل سوق الأسهم السعودية (تداول) يوفر أدوات للتحليل الفني والأساسي، وتوصيات الاستثمار، ومتابعة أداء الأسهم. يتكون النظام من واجهة مستخدم مبنية بـ React وخلفية مبنية بـ PHP مع تكامل مع Python لعمليات التحليل المتقدمة.

## المتطلبات الأساسية

### متطلبات النظام
- PHP 7.4 أو أحدث
- Node.js 14 أو أحدث
- Python 3.8 أو أحدث
- خادم ويب (Apache أو Nginx)
- قاعدة بيانات MySQL 5.7 أو أحدث

### المكتبات والحزم المطلوبة
- **PHP**: 
  - Composer
  - Extension: mysqli, curl, json, mbstring
  
- **Node.js**: 
  - npm أو yarn
  
- **Python**: 
  - pip
  - حزم: pandas, numpy, scikit-learn, matplotlib, yfinance, ta-lib

## تثبيت وإعداد المشروع

### 1. إعداد الخادم

#### تثبيت الخادم (Apache)
```bash
# لنظام Ubuntu/Debian
sudo apt update
sudo apt install apache2 php php-mysql php-curl php-json php-mbstring

# لنظام CentOS/RHEL
sudo yum install httpd php php-mysql php-curl php-json php-mbstring
```

#### تثبيت قاعدة البيانات
```bash
# لنظام Ubuntu/Debian
sudo apt install mysql-server

# لنظام CentOS/RHEL
sudo yum install mariadb-server
```

### 2. إعداد قاعدة البيانات

```sql
CREATE DATABASE tasi3;
CREATE USER 'tasi3_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON tasi3.* TO 'tasi3_user'@'localhost';
FLUSH PRIVILEGES;
```

استيراد هيكل قاعدة البيانات:
```bash
mysql -u tasi3_user -p tasi3 < database/schema.sql
```

### 3. تثبيت الخلفية (Backend)

```bash
# استنساخ المشروع
git clone https://github.com/your-repo/tasi3.git
cd tasi3

# تثبيت اعتماديات PHP
composer install

# تكوين ملف الإعدادات
cp config/config.example.php config/config.php
# قم بتعديل ملف config.php بإعدادات قاعدة البيانات الخاصة بك
```

### 4. إعداد بيئة Python

```bash
# تثبيت حزم Python المطلوبة
pip install -r integration/requirements.txt

# تثبيت TA-Lib (قد يتطلب خطوات إضافية حسب نظام التشغيل)
# لنظام Ubuntu/Debian
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### 5. تثبيت واجهة المستخدم (Frontend)

```bash
# الانتقال إلى مجلد العميل
cd client

# تثبيت اعتماديات Node.js
npm install

# بناء الإصدار النهائي
npm run build

# أو تشغيل خادم التطوير
npm start
```

## تكوين المشروع

### 1. إعداد ملف التكوين الرئيسي

قم بتعديل ملف `config/config.php` لتكوين:
- اتصال قاعدة البيانات
- مسارات API
- إعدادات الأمان
- معلمات التكامل مع Python

### 2. إعداد تكامل Python

قم بتعديل ملف `integration/config.py` لتكوين:
- مصادر البيانات
- معلمات التحليل
- مسارات الملفات المؤقتة

### 3. إعداد واجهة المستخدم

قم بتعديل ملف `client/.env` لتكوين:
- عنوان API
- معلمات الواجهة

## تشغيل المشروع

### تشغيل الخادم الخلفي

```bash
# تأكد من أن خادم الويب يعمل
sudo systemctl start apache2  # أو httpd لـ CentOS/RHEL

# تأكد من أن قاعدة البيانات تعمل
sudo systemctl start mysql  # أو mariadb لـ CentOS/RHEL
```

### تشغيل واجهة المستخدم للتطوير

```bash
cd client
npm start
```

### نشر واجهة المستخدم للإنتاج

```bash
cd client
npm run build
# انقل محتويات مجلد build إلى المجلد العام للخادم
cp -r build/* /var/www/html/tasi3/
```

## الوصول إلى التطبيق

- **واجهة المستخدم للتطوير**: http://localhost:3000
- **واجهة المستخدم للإنتاج**: http://your-server-domain/tasi3
- **واجهة API**: http://your-server-domain/tasi3/api.php

## الميزات الرئيسية

1. **لوحة المعلومات**: عرض نظرة عامة على السوق والأسهم المتابعة
2. **التحليل الفني**: أدوات للتحليل الفني مع مؤشرات متعددة ورسوم بيانية تفاعلية
3. **التحليل الأساسي**: تحليل البيانات المالية والمؤشرات الأساسية للشركات
4. **توصيات الاستثمار**: توصيات مخصصة بناءً على ملف المخاطر وأفق الاستثمار
5. **متابعة المحفظة**: تتبع أداء المحفظة الاستثمارية وتحليلها
6. **تنبيهات الأسعار**: إعداد تنبيهات لتغيرات الأسعار والأحداث المهمة

## استخدام API

### نقاط النهاية الرئيسية

- `api.php?action=recommend`: الحصول على توصيات الاستثمار
- `api.php?action=technical`: الحصول على التحليل الفني لسهم معين
- `api.php?action=fundamental`: الحصول على التحليل الأساسي لسهم معين
- `api.php?action=market_data`: الحصول على بيانات السوق
- `api.php?action=portfolio`: إدارة محفظة المستخدم

### مثال على استخدام API

```javascript
// مثال على طلب التحليل الفني
fetch('/api.php?action=technical&symbol=2222.SR&timeframe=daily')
  .then(response => response.json())
  .then(data => console.log(data));
```

## استكشاف الأخطاء وإصلاحها

### مشاكل الخادم الخلفي

1. **خطأ في الاتصال بقاعدة البيانات**:
   - تحقق من إعدادات قاعدة البيانات في `config/config.php`
   - تأكد من أن خدمة قاعدة البيانات تعمل

2. **خطأ في تنفيذ سكريبت Python**:
   - تحقق من تثبيت جميع حزم Python المطلوبة
   - تأكد من صلاحيات الملفات والمجلدات
   - راجع سجلات الأخطاء في `logs/integration.log`

### مشاكل واجهة المستخدم

1. **خطأ في الاتصال بـ API**:
   - تحقق من إعدادات الوكيل في `client/src/setupProxy.js`
   - تأكد من أن الخادم الخلفي يعمل ويمكن الوصول إليه

2. **مشاكل في عرض الرسوم البيانية**:
   - تأكد من تحميل مكتبة الرسوم البيانية بشكل صحيح
   - تحقق من تنسيق البيانات المرسلة إلى مكونات الرسم البياني

## الصيانة والتحديث

### النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
mysqldump -u tasi3_user -p tasi3 > backup/tasi3_$(date +%Y%m%d).sql

# نسخ احتياطي للملفات
tar -czf backup/tasi3_files_$(date +%Y%m%d).tar.gz /var/www/html/tasi3
```

### التحديث

```bash
# تحديث الكود المصدري
git pull origin main

# تحديث اعتماديات PHP
composer update

# تحديث اعتماديات Node.js
cd client
npm update

# إعادة بناء واجهة المستخدم
npm run build
cp -r build/* /var/www/html/tasi3/
```

## المساهمة في المشروع

نرحب بمساهماتكم في تطوير هذا المشروع! يرجى اتباع الخطوات التالية:

1. انشئ fork للمشروع
2. أنشئ فرعًا جديدًا (`git checkout -b feature/amazing-feature`)
3. قم بعمل commit للتغييرات (`git commit -m 'Add some amazing feature'`)
4. ادفع إلى الفرع (`git push origin feature/amazing-feature`)
5. افتح طلب سحب (Pull Request)

## الترخيص

هذا المشروع مرخص بموجب [رخصة MIT](LICENSE).

## الاتصال والدعم

للأسئلة والاستفسارات، يرجى التواصل عبر:
- البريد الإلكتروني: support@tasi3.example.com
- تويتر: @TASI3_Support