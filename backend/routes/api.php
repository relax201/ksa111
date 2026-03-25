<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Auth\AuthController;
use App\Http\Controllers\Market\MarketController;
use App\Http\Controllers\Stock\StockController;
use App\Http\Controllers\Analysis\AnalysisController;
use App\Http\Controllers\Recommendation\RecommendationController;
use App\Http\Controllers\News\NewsController;
use App\Http\Controllers\Integration\IntegrationController;
use App\Http\Controllers\Portfolio\PortfolioController;
use App\Http\Controllers\Notification\NotificationController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| هنا يمكنك تسجيل مسارات API لتطبيقك. تقوم هذه المسارات بتحميل
| RouteServiceProvider ضمن مجموعة تحتوي على وسيط "api".
|
*/

// مسارات عامة لا تتطلب مصادقة
Route::prefix('v1')->group(function () {
    // مسارات المصادقة
    Route::prefix('auth')->group(function () {
        Route::post('login', [AuthController::class, 'login']);
        Route::post('register', [AuthController::class, 'register']);
        Route::post('forgot-password', [AuthController::class, 'forgotPassword']);
        Route::post('reset-password', [AuthController::class, 'resetPassword']);
    });

    // بيانات السوق العامة
    Route::prefix('market')->group(function () {
        Route::get('overview', [MarketController::class, 'getOverview']);
        Route::get('indices', [MarketController::class, 'getIndices']);
        Route::get('sectors', [MarketController::class, 'getSectors']);
        Route::get('top-gainers', [MarketController::class, 'getTopGainers']);
        Route::get('top-losers', [MarketController::class, 'getTopLosers']);
        Route::get('most-active', [MarketController::class, 'getMostActive']);
    });

    // بيانات الأسهم العامة
    Route::prefix('stocks')->group(function () {
        Route::get('/', [StockController::class, 'index']);
        Route::get('/{symbol}', [StockController::class, 'show']);
        Route::get('/{symbol}/historical', [StockController::class, 'getHistoricalData']);
        Route::get('/{symbol}/financials', [StockController::class, 'getFinancials']);
        Route::get('/{symbol}/sentiment', [StockController::class, 'getSentiment']);
        Route::get('/{symbol}/profile', [StockController::class, 'getProfile']);
    });

    // الأخبار
    Route::prefix('news')->group(function () {
        Route::get('/', [NewsController::class, 'index']);
        Route::get('/{id}', [NewsController::class, 'show']);
        Route::get('/categories', [NewsController::class, 'getCategories']);
    });

    // تكامل النظام (للقراءة فقط - لا تتطلب مصادقة)
    Route::prefix('integration')->group(function () {
        Route::post('/recommendations', [IntegrationController::class, 'getRecommendations']);
        Route::post('/technical-analysis', [IntegrationController::class, 'getTechnicalAnalysis']);
        Route::post('/fundamental-analysis', [IntegrationController::class, 'getFundamentalAnalysis']);
    });
});

// مسارات تتطلب مصادقة
Route::prefix('v1')->middleware('auth:sanctum')->group(function () {
    // معلومات المستخدم
    Route::get('/user', function (Request $request) {
        return $request->user();
    });

    // تسجيل الخروج
    Route::post('/auth/logout', [AuthController::class, 'logout']);
    Route::post('/auth/refresh', [AuthController::class, 'refresh']);

    // التحليلات
    Route::prefix('analysis')->group(function () {
        Route::get('/{symbol}/technical', [AnalysisController::class, 'getTechnicalAnalysis']);
        Route::get('/{symbol}/fundamental', [AnalysisController::class, 'getFundamentalAnalysis']);
        Route::get('/{symbol}/indicators', [AnalysisController::class, 'getIndicators']);
        Route::post('/custom', [AnalysisController::class, 'getCustomAnalysis']);
    });

    // التوصيات
    Route::prefix('recommendations')->group(function () {
        Route::get('/', [RecommendationController::class, 'index']);
        Route::get('/{symbol}', [RecommendationController::class, 'getStockRecommendation']);
        Route::get('/portfolio', [RecommendationController::class, 'getPortfolioRecommendations']);
        Route::post('/settings', [RecommendationController::class, 'updateSettings']);
    });

    // المحفظة
    Route::prefix('portfolio')->group(function () {
        Route::get('/', [PortfolioController::class, 'index']);
        Route::post('/', [PortfolioController::class, 'store']);
        Route::get('/{id}', [PortfolioController::class, 'show']);
        Route::put('/{id}', [PortfolioController::class, 'update']);
        Route::delete('/{id}', [PortfolioController::class, 'destroy']);
        Route::post('/{id}/stocks', [PortfolioController::class, 'addStock']);
        Route::delete('/{id}/stocks/{stockId}', [PortfolioController::class, 'removeStock']);
    });

    // الإشعارات
    Route::prefix('notifications')->group(function () {
        Route::get('/', [NotificationController::class, 'index']);
        Route::put('/{id}/read', [NotificationController::class, 'markAsRead']);
        Route::put('/read-all', [NotificationController::class, 'markAllAsRead']);
        Route::post('/settings', [NotificationController::class, 'updateSettings']);
    });
    
    // تكامل النظام (عمليات تتطلب مصادقة)
    Route::prefix('integration')->group(function () {
        Route::post('/collect-data', [IntegrationController::class, 'collectData']);
        Route::post('/process-data', [IntegrationController::class, 'processData']);
    });
});