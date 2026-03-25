---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
تاسي3 (Tasi3) هو نظام متكامل لتحليل وتقديم توصيات للأسهم في السوق السعودي (تداول). يتكون المشروع من واجهة خلفية مبنية على Laravel وعدة مكونات تحليلية مكتوبة بلغة Python.

## Repository Structure
- **analysis**: مكونات التحليل الفني والأساسي مكتوبة بلغة Python
- **backend**: واجهة خلفية مبنية على Laravel تقدم واجهة برمجة التطبيقات (API)
- **data**: أدوات جمع ومعالجة وتخزين البيانات
- **frontend**: هيكل أولي للواجهة الأمامية (غير مكتمل)
- **recommendation**: مكونات نظام التوصيات مكتوبة بلغة Python

### Main Repository Components
- **التحليل الفني**: أدوات لحساب المؤشرات الفنية وتحليل الرسوم البيانية
- **التحليل الأساسي**: أدوات لتحليل البيانات المالية وتقييم الشركات
- **نظام التوصيات**: محرك لتوليد توصيات استثمارية بناءً على التحليلات
- **واجهة API**: واجهة برمجة تطبيقات RESTful لتقديم البيانات والتوصيات

## Projects

### Backend (Laravel API)
**Configuration File**: composer.json

#### Language & Runtime
**Language**: PHP
**Version**: ^8.1
**Framework**: Laravel ^10.0
**Package Manager**: Composer

#### Dependencies
**Main Dependencies**:
- laravel/framework: ^10.0
- laravel/sanctum: ^3.2
- tymon/jwt-auth: ^2.0
- spatie/laravel-permission: ^5.10
- league/fractal: ^0.20.1
- predis/predis: ^2.1

#### Build & Installation
```bash
composer install
php artisan key:generate
php artisan migrate
php artisan db:seed
php artisan serve
```

### Analysis Components (Python)
**Configuration File**: N/A (Python modules)

#### Language & Runtime
**Language**: Python
**Build System**: N/A (Python modules)
**Package Manager**: N/A (Implicit dependencies)

#### Dependencies
**Main Dependencies**:
- pandas
- numpy
- matplotlib
- scikit-learn

#### Structure
**Technical Analysis**:
- indicators.py: مكتبة لحساب المؤشرات الفنية
- analyzer.py: محلل للرسوم البيانية والأنماط

**Fundamental Analysis**:
- statements.py: أدوات لمعالجة البيانات المالية
- ratios.py: حساب النسب المالية
- valuation.py: نماذج تقييم الشركات

### Recommendation System (Python)
**Configuration File**: N/A (Python modules)

#### Language & Runtime
**Language**: Python
**Build System**: N/A (Python modules)
**Package Manager**: N/A (Implicit dependencies)

#### Dependencies
**Main Dependencies**:
- pandas
- numpy
- scikit-learn

#### Structure
**Components**:
- engine.py: محرك التوصيات الرئيسي
- models.py: نماذج التوصيات
- portfolio.py: إدارة المحافظ الاستثمارية
- alerts.py: نظام التنبيهات
- screener.py: أداة فرز الأسهم

## Development Status
- **Backend API**: مكتمل جزئياً مع وجود نماذج وخدمات أساسية
- **Analysis Components**: مكتمل جزئياً مع وجود مكتبات للتحليل الفني والأساسي
- **Recommendation System**: مكتمل جزئياً مع وجود محرك توصيات أساسي
- **Frontend**: هيكل أولي فقط، غير مكتمل
- **Data Collection**: هيكل أولي فقط، غير مكتمل

## Notes
- المشروع في مرحلة التطوير وليس جاهزاً للإنتاج
- الواجهة الأمامية تحتاج إلى تطوير كامل
- نظام جمع البيانات يحتاج إلى تنفيذ
- يجب إضافة اختبارات وتوثيق أفضل