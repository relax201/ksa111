# دليل تثبيت وتشغيل نظام TASI3

هذا الدليل يشرح بالتفصيل كيفية تثبيت وتشغيل نظام TASI3 لتحليل سوق الأسهم السعودية.

## المتطلبات التقنية

### متطلبات الخادم
- **نظام التشغيل**: Windows Server 2019/2022 أو Ubuntu 20.04/22.04 LTS
- **المعالج**: 4 أنوية على الأقل
- **الذاكرة**: 8 جيجابايت RAM على الأقل
- **مساحة التخزين**: 50 جيجابايت على الأقل (SSD مفضل)
- **اتصال إنترنت**: اتصال مستقر وسريع (10 ميجابت/ثانية على الأقل)

### البرمجيات المطلوبة
- **خادم ويب**: Apache 2.4+ أو Nginx 1.18+
- **PHP**: الإصدار 7.4 أو 8.0+
  - امتدادات PHP المطلوبة: mysqli, PDO, curl, json, mbstring, xml
- **قاعدة البيانات**: MySQL 5.7+ أو MariaDB 10.5+
- **Node.js**: الإصدار 14.x أو 16.x أو 18.x
- **Python**: الإصدار 3.8 أو 3.9 أو 3.10
  - حزم Python المطلوبة موجودة في ملف `integration/requirements.txt`

## خطوات التثبيت المفصلة

### 1. إعداد بيئة الخادم

#### لنظام Windows:
1. قم بتثبيت [XAMPP](https://www.apachefriends.org/download.html) أو [WampServer](https://www.wampserver.com/en/) للحصول على Apache, PHP, MySQL
2. قم بتثبيت [Node.js](https://nodejs.org/) (اختر الإصدار LTS)
3. قم بتثبيت [Python](https://www.python.org/downloads/) (تأكد من تفعيل خيار "Add Python to PATH")
4. قم بتثبيت [Git for Windows](https://git-scm.com/download/win)

#### لنظام Ubuntu:
```bash
# تثبيت Apache, PHP ومكتباته
sudo apt update
sudo apt install apache2 php php-cli php-fpm php-mysql php-curl php-json php-mbstring php-xml

# تثبيت MySQL
sudo apt install mysql-server

# تثبيت Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# تثبيت Python وأدواته
sudo apt install python3 python3-pip python3-dev

# تثبيت Git
sudo apt install git
```

### 2. الحصول على الكود المصدري

```bash
# استنساخ المستودع
git clone https://github.com/your-repo/tasi3.git
cd tasi3
```

### 3. إعداد قاعدة البيانات

#### إنشاء قاعدة البيانات والمستخدم:

```sql
CREATE DATABASE tasi3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tasi3_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON tasi3.* TO 'tasi3_user'@'localhost';
FLUSH PRIVILEGES;
```

#### استيراد هيكل قاعدة البيانات:

```bash
# لنظام Windows (باستخدام XAMPP)
C:\xampp\mysql\bin\mysql -u tasi3_user -p tasi3 < database/schema.sql

# لنظام Ubuntu
mysql -u tasi3_user -p tasi3 < database/schema.sql
```

### 4. إعداد الخلفية (Backend)

#### تثبيت اعتماديات PHP:

```bash
# تثبيت Composer إذا لم يكن موجودًا
# لنظام Windows: قم بتنزيل وتثبيت Composer من https://getcomposer.org/download/

# لنظام Ubuntu
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# تثبيت اعتماديات PHP
composer install
```

#### تكوين ملفات الإعدادات:

```bash
# نسخ ملف الإعدادات النموذجي
cp config/config.example.php config/config.php
```

قم بتعديل ملف `config/config.php` وتحديث المعلومات التالية:
- بيانات اتصال قاعدة البيانات (اسم المستخدم، كلمة المرور، اسم قاعدة البيانات)
- مسار تثبيت Python
- إعدادات API الخارجية (إن وجدت)
- مفاتيح الأمان

### 5. إعداد بيئة Python

```bash
# تثبيت حزم Python المطلوبة
pip install -r integration/requirements.txt

# تثبيت TA-Lib (مكتبة التحليل الفني)
# لنظام Windows:
# قم بتنزيل الملف المناسب من https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# ثم قم بتثبيته باستخدام pip
pip install TA_Lib‑0.4.24‑cp39‑cp39‑win_amd64.whl

# لنظام Ubuntu:
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### 6. إعداد واجهة المستخدم (Frontend)

```bash
# الانتقال إلى مجلد العميل
cd client

# تثبيت اعتماديات Node.js
npm install

# إنشاء ملف الإعدادات البيئية
cp .env.example .env
```

قم بتعديل ملف `.env` وتحديث المعلومات التالية:
- عنوان API الخلفية
- إعدادات البيئة (development أو production)

### 7. بناء واجهة المستخدم

```bash
# بناء الإصدار النهائي
npm run build
```

### 8. تكوين خادم الويب

#### لنظام Windows (XAMPP):

1. انسخ محتويات المشروع إلى مجلد `C:\xampp\htdocs\tasi3`
2. تأكد من أن محتويات مجلد `client/build` موجودة في `C:\xampp\htdocs\tasi3\public`

#### لنظام Ubuntu (Apache):

1. قم بإنشاء ملف تكوين لموقع الويب:

```bash
sudo nano /etc/apache2/sites-available/tasi3.conf
```

2. أضف التكوين التالي:

```apache
<VirtualHost *:80>
    ServerName tasi3.yourdomain.com
    DocumentRoot /var/www/html/tasi3
    
    <Directory /var/www/html/tasi3>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/tasi3_error.log
    CustomLog ${APACHE_LOG_DIR}/tasi3_access.log combined
</VirtualHost>
```

3. تفعيل الموقع وإعادة تشغيل Apache:

```bash
sudo a2ensite tasi3.conf
sudo a2enmod rewrite
sudo systemctl restart apache2
```

4. نسخ ملفات المشروع:

```bash
sudo mkdir -p /var/www/html/tasi3
sudo cp -r * /var/www/html/tasi3/
sudo cp -r client/build/* /var/www/html/tasi3/public/
sudo chown -R www-data:www-data /var/www/html/tasi3
```

## تشغيل المشروع

### تشغيل في بيئة التطوير

#### تشغيل الخادم الخلفي:
```bash
# تأكد من أن خادم الويب وقاعدة البيانات تعمل
# لنظام Windows (XAMPP)
# قم بتشغيل لوحة تحكم XAMPP وتشغيل Apache و MySQL

# لنظام Ubuntu
sudo systemctl start apache2
sudo systemctl start mysql
```

#### تشغيل واجهة المستخدم للتطوير:
```bash
cd client
npm start
```

### تشغيل في بيئة الإنتاج

1. تأكد من أن جميع الملفات في المكان الصحيح:
   - ملفات الخلفية في المجلد الرئيسي للمشروع
   - ملفات واجهة المستخدم المبنية في مجلد `public`

2. تأكد من أن خادم الويب وقاعدة البيانات تعمل:
   ```bash
   # لنظام Ubuntu
   sudo systemctl status apache2
   sudo systemctl status mysql
   ```

3. تأكد من صلاحيات الملفات:
   ```bash
   # لنظام Ubuntu
   sudo chown -R www-data:www-data /var/www/html/tasi3
   sudo chmod -R 755 /var/www/html/tasi3
   sudo chmod -R 777 /var/www/html/tasi3/logs
   sudo chmod -R 777 /var/www/html/tasi3/uploads
   ```

## التحقق من التثبيت

1. افتح المتصفح وانتقل إلى:
   - بيئة التطوير: `http://localhost:3000`
   - بيئة الإنتاج: `http://your-server-domain/tasi3` أو `http://tasi3.yourdomain.com`

2. تحقق من عمل API:
   - اختبر نقطة نهاية API: `http://your-server-domain/tasi3/api.php?action=technical&symbol=2222.SR`
   - يجب أن تحصل على استجابة JSON صالحة

## استكشاف الأخطاء وإصلاحها

### مشاكل الخادم الخلفي

1. **خطأ في الاتصال بقاعدة البيانات**:
   - تحقق من إعدادات قاعدة البيانات في `config/config.php`
   - تأكد من أن خدمة قاعدة البيانات تعمل
   - تحقق من صلاحيات المستخدم

   ```bash
   # اختبار اتصال قاعدة البيانات
   mysql -u tasi3_user -p -h localhost tasi3
   ```

2. **خطأ في تنفيذ سكريبت Python**:
   - تحقق من مسار Python في ملف التكوين
   - تأكد من تثبيت جميع الحزم المطلوبة
   - تحقق من سجلات الأخطاء

   ```bash
   # اختبار تثبيت حزم Python
   pip list | grep -E "pandas|numpy|scikit-learn|matplotlib|yfinance|ta-lib"
   
   # اختبار تنفيذ سكريبت Python
   python integration/test_integration.py
   ```

3. **مشاكل في صلاحيات الملفات**:
   - تأكد من أن مستخدم خادم الويب لديه صلاحيات القراءة والكتابة على الملفات والمجلدات المطلوبة

   ```bash
   # لنظام Ubuntu
   sudo chown -R www-data:www-data /var/www/html/tasi3
   sudo chmod -R 755 /var/www/html/tasi3
   ```

### مشاكل واجهة المستخدم

1. **خطأ في الاتصال بـ API**:
   - تحقق من إعدادات الوكيل في `client/src/setupProxy.js`
   - تأكد من أن الخادم الخلفي يعمل ويمكن الوصول إليه
   - تحقق من سجلات وحدة تحكم المتصفح للأخطاء

2. **مشاكل في عرض الرسوم البيانية**:
   - تأكد من تحميل مكتبة الرسوم البيانية بشكل صحيح
   - تحقق من تنسيق البيانات المرسلة إلى مكونات الرسم البياني
   - تحقق من توافق المتصفح

## تحديث النظام

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

# نسخ الملفات المبنية إلى المجلد العام
# لنظام Windows (XAMPP)
xcopy /E /Y build\* ..\public\

# لنظام Ubuntu
cp -r build/* ../public/
```

## النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
# لنظام Windows (XAMPP)
C:\xampp\mysql\bin\mysqldump -u tasi3_user -p tasi3 > backup/tasi3_$(date +%Y%m%d).sql

# لنظام Ubuntu
mysqldump -u tasi3_user -p tasi3 > backup/tasi3_$(date +%Y%m%d).sql

# نسخ احتياطي للملفات
# لنظام Windows
xcopy /E /Y C:\xampp\htdocs\tasi3 backup\tasi3_files_$(date +%Y%m%d)\

# لنظام Ubuntu
tar -czf backup/tasi3_files_$(date +%Y%m%d).tar.gz /var/www/html/tasi3
```

## الأمان والحماية

1. **تأمين قاعدة البيانات**:
   - استخدم كلمة مرور قوية لمستخدم قاعدة البيانات
   - امنح الحد الأدنى من الصلاحيات المطلوبة فقط

2. **تأمين الخادم**:
   - قم بتحديث النظام والبرامج بانتظام
   - استخدم جدار حماية لتقييد الوصول
   - فعّل HTTPS باستخدام شهادة SSL

3. **تأمين التطبيق**:
   - تأكد من التحقق من صحة جميع المدخلات
   - استخدم آليات مكافحة هجمات CSRF و XSS
   - قم بتشفير البيانات الحساسة

## الدعم والمساعدة

إذا واجهت أي مشاكل أثناء التثبيت أو التشغيل، يرجى التواصل عبر:
- البريد الإلكتروني: support@tasi3.example.com
- تويتر: @TASI3_Support
- قسم المشكلات (Issues) في مستودع GitHub