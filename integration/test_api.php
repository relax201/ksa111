<?php
/**
 * TASI3 Integration API Test Script
 * 
 * This script tests the integration API endpoints by making HTTP requests
 * and displaying the results.
 */

// Function to make a POST request to the API
function makePostRequest($url, $data) {
    $ch = curl_init($url);
    
    $payload = json_encode($data);
    
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $result = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    curl_close($ch);
    
    return [
        'status_code' => $httpCode,
        'response' => $result ? json_decode($result, true) : null
    ];
}

// Function to display test results
function displayTestResult($title, $result) {
    echo "=== $title ===\n";
    echo "Status Code: " . $result['status_code'] . "\n";
    echo "Response: " . json_encode($result['response'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    echo "\n\n";
}

// Base URL for the API
$baseUrl = 'http://localhost/tasi3/public/api/v1';

// Test 1: Get investment recommendations
echo "اختبار 1: الحصول على توصيات الاستثمار\n";
$recommendationsResult = makePostRequest("$baseUrl/integration/recommendations", [
    'risk_profile' => 'moderate',
    'investment_horizon' => 'medium',
    'sectors' => ['technology', 'healthcare'],
    'exclude_symbols' => ['AAPL', 'MSFT'],
    'max_results' => 5
]);
displayTestResult("نتائج التوصيات", $recommendationsResult);

// Test 2: Get technical analysis
echo "اختبار 2: الحصول على التحليل الفني\n";
$technicalAnalysisResult = makePostRequest("$baseUrl/integration/technical-analysis", [
    'symbol' => '2222.SR',
    'indicators' => ['SMA', 'RSI', 'MACD'],
    'timeframe' => 'daily'
]);
displayTestResult("نتائج التحليل الفني", $technicalAnalysisResult);

// Test 3: Get fundamental analysis
echo "اختبار 3: الحصول على التحليل الأساسي\n";
$fundamentalAnalysisResult = makePostRequest("$baseUrl/integration/fundamental-analysis", [
    'symbol' => '2222.SR',
    'metrics' => ['PE', 'PB', 'ROE', 'EPS']
]);
displayTestResult("نتائج التحليل الأساسي", $fundamentalAnalysisResult);

// Test 4: Collect market data
echo "اختبار 4: جمع بيانات السوق\n";
$marketDataResult = makePostRequest("$baseUrl/integration/collect-data", [
    'symbols' => ['2222.SR', '1211.SR'],
    'data_type' => 'market',
    'data_types' => ['price', 'volume', 'market_cap']
]);
displayTestResult("نتائج بيانات السوق", $marketDataResult);

// Test 5: Collect financial data
echo "اختبار 5: جمع البيانات المالية\n";
$financialDataResult = makePostRequest("$baseUrl/integration/collect-data", [
    'symbols' => ['2222.SR', '1211.SR'],
    'data_type' => 'financial',
    'statement_types' => ['income', 'balance', 'cash_flow'],
    'periods' => ['annual', 'quarterly']
]);
displayTestResult("نتائج البيانات المالية", $financialDataResult);

// Test 6: Process financial data
echo "اختبار 6: معالجة البيانات المالية\n";
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
$processDataResult = makePostRequest("$baseUrl/integration/process-data", [
    'data' => $sampleData,
    'processing_type' => 'normalization',
    'options' => ['method' => 'min_max']
]);
displayTestResult("نتائج معالجة البيانات", $processDataResult);

echo "تم الانتهاء من جميع اختبارات واجهة برمجة التطبيقات!\n";