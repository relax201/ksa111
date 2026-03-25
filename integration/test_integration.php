<?php
/**
 * TASI3 Integration Test Script
 * 
 * This script tests the integration system by calling various functions
 * and displaying the results.
 */

// Include the integration bridge
require_once __DIR__ . '/bridge.php';

// Function to display test results
function displayTestResult($title, $result) {
    echo "=== $title ===\n";
    echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    echo "\n\n";
}

// Test 1: Get investment recommendations
echo "اختبار 1: الحصول على توصيات الاستثمار\n";
$recommendations = getRecommendations(
    'moderate',
    'medium',
    ['technology', 'healthcare'],
    ['AAPL', 'MSFT'],
    5
);
displayTestResult("نتائج التوصيات", $recommendations);

// Test 2: Get technical analysis
echo "اختبار 2: الحصول على التحليل الفني\n";
$technicalAnalysis = getTechnicalAnalysis(
    '2222.SR',
    ['SMA', 'RSI', 'MACD'],
    'daily'
);
displayTestResult("نتائج التحليل الفني", $technicalAnalysis);

// Test 3: Get fundamental analysis
echo "اختبار 3: الحصول على التحليل الأساسي\n";
$fundamentalAnalysis = getFundamentalAnalysis(
    '2222.SR',
    ['PE', 'PB', 'ROE', 'EPS']
);
displayTestResult("نتائج التحليل الأساسي", $fundamentalAnalysis);

// Test 4: Collect market data
echo "اختبار 4: جمع بيانات السوق\n";
$marketData = collectMarketData(
    ['2222.SR', '1211.SR'],
    ['price', 'volume', 'market_cap']
);
displayTestResult("نتائج بيانات السوق", $marketData);

// Test 5: Collect financial data
echo "اختبار 5: جمع البيانات المالية\n";
$financialData = collectFinancialData(
    ['2222.SR', '1211.SR'],
    ['income', 'balance', 'cash_flow'],
    ['annual', 'quarterly']
);
displayTestResult("نتائج البيانات المالية", $financialData);

// Test 6: Analyze sentiment
echo "اختبار 6: تحليل المشاعر\n";
$sentimentAnalysis = analyzeSentiment(
    ['2222.SR', '1211.SR'],
    ['news', 'social_media', 'analyst_ratings'],
    '1w'
);
displayTestResult("نتائج تحليل المشاعر", $sentimentAnalysis);

// Test 7: Process financial data
echo "اختبار 7: معالجة البيانات المالية\n";
$sampleData = [
    'symbol' => '2222.SR',
    'financials' => [
        'income' => [
            'revenue' => [100000000, 120000000, 150000000],
            'net_income' => [10000000, 15000000, 20000000]
        ],
        'balance' => [
            'total_assets' => [500000000, 550000000, 600000000],
            'total_liabilities' => [300000000, 320000000, 350000000]
        ]
    ]
];
$processedData = processFinancialData(
    $sampleData,
    'normalization',
    ['method' => 'min_max']
);
displayTestResult("نتائج معالجة البيانات", $processedData);

echo "تم الانتهاء من جميع الاختبارات بنجاح!\n";