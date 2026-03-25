<?php
/**
 * TASI3 Integration Example
 * 
 * This file demonstrates how to use the integration bridge to interact with
 * different components of the TASI3 system.
 */

// Include the integration bridge
require_once __DIR__ . '/bridge.php';

// Example 1: Get investment recommendations
echo "Example 1: Get investment recommendations\n";
$recommendations = getRecommendations(
    'moderate',
    'medium',
    ['technology', 'healthcare'],
    ['AAPL', 'MSFT'],
    5
);
echo "Recommendations result: " . json_encode($recommendations, JSON_PRETTY_PRINT) . "\n\n";

// Example 2: Get technical analysis
echo "Example 2: Get technical analysis\n";
$technicalAnalysis = getTechnicalAnalysis(
    '2222.SR',
    ['SMA', 'RSI', 'MACD'],
    'daily'
);
echo "Technical analysis result: " . json_encode($technicalAnalysis, JSON_PRETTY_PRINT) . "\n\n";

// Example 3: Get fundamental analysis
echo "Example 3: Get fundamental analysis\n";
$fundamentalAnalysis = getFundamentalAnalysis(
    '2222.SR',
    ['PE', 'PB', 'ROE', 'EPS']
);
echo "Fundamental analysis result: " . json_encode($fundamentalAnalysis, JSON_PRETTY_PRINT) . "\n\n";

// Example 4: Collect market data
echo "Example 4: Collect market data\n";
$marketData = collectMarketData(
    ['2222.SR', '1211.SR'],
    ['price', 'volume', 'market_cap']
);
echo "Market data result: " . json_encode($marketData, JSON_PRETTY_PRINT) . "\n\n";

// Example 5: Collect financial data
echo "Example 5: Collect financial data\n";
$financialData = collectFinancialData(
    ['2222.SR', '1211.SR'],
    ['income', 'balance', 'cash_flow'],
    ['annual', 'quarterly']
);
echo "Financial data result: " . json_encode($financialData, JSON_PRETTY_PRINT) . "\n\n";

// Example 6: Analyze sentiment
echo "Example 6: Analyze sentiment\n";
$sentimentAnalysis = analyzeSentiment(
    ['2222.SR', '1211.SR'],
    ['news', 'social_media', 'analyst_ratings'],
    '1w'
);
echo "Sentiment analysis result: " . json_encode($sentimentAnalysis, JSON_PRETTY_PRINT) . "\n\n";

// Example 7: Process financial data
echo "Example 7: Process financial data\n";
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
echo "Processed data result: " . json_encode($processedData, JSON_PRETTY_PRINT) . "\n\n";