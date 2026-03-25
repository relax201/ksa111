<?php
/**
 * TASI3 API Bridge
 * 
 * This file serves as a bridge between the frontend and the backend API.
 * It receives requests from the frontend and forwards them to the appropriate backend endpoints.
 */

// Set headers for JSON response and CORS
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// تسجيل معلومات الطلب للتصحيح
error_log("API Request: " . $_SERVER['REQUEST_METHOD'] . " " . $_SERVER['REQUEST_URI']);
error_log("GET Parameters: " . print_r($_GET, true));

// Include the integration bridge
require_once __DIR__ . '/integration/bridge.php';

// Get the action from the request
$action = $_GET['action'] ?? '';

try {
    $response = [];
    
    switch ($action) {
        case 'recommend':
            // Get parameters from the request
            $riskProfile = $_GET['risk_profile'] ?? 'moderate';
            $investmentHorizon = $_GET['investment_horizon'] ?? 'medium';
            
            // Handle array parameters correctly
            $sectors = isset($_GET['sectors']) ? (is_array($_GET['sectors']) ? $_GET['sectors'] : [$_GET['sectors']]) : [];
            $excludeSymbols = isset($_GET['exclude_symbols']) ? (is_array($_GET['exclude_symbols']) ? $_GET['exclude_symbols'] : [$_GET['exclude_symbols']]) : [];
            $maxResults = (int)($_GET['max_results'] ?? 5);
            
            // Call the bridge function
            $result = getRecommendations($riskProfile, $investmentHorizon, $sectors, $excludeSymbols, $maxResults);
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'recommendations' => $result['data']['recommendations'] ?? [],
                    'risk_profile' => $riskProfile,
                    'investment_horizon' => $investmentHorizon,
                    'analysis_date' => $result['data']['analysis_date'] ?? date('Y-m-d H:i:s')
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get recommendations');
            }
            break;
            
        case 'technical':
            // Get parameters from the request
            $symbol = $_GET['symbol'] ?? '2222.SR';
            $timeframe = $_GET['timeframe'] ?? 'daily';
            
            // Handle array parameters correctly - check for both indicators[] and indicators
            if (isset($_GET['indicators']) && is_array($_GET['indicators'])) {
                $indicators = $_GET['indicators'];
            } elseif (isset($_GET['indicators'])) {
                $indicators = [$_GET['indicators']];
            } elseif (isset($_GET['indicators[]']) && is_array($_GET['indicators[]'])) {
                $indicators = $_GET['indicators[]'];
            } elseif (isset($_GET['indicators[]'])) {
                $indicators = [$_GET['indicators[]']];
            } else {
                $indicators = ['SMA', 'RSI', 'MACD'];
            }
            
            // تسجيل المعلمات للتصحيح
            error_log("Technical Analysis Request - Symbol: $symbol, Timeframe: $timeframe");
            error_log("Indicators: " . print_r($indicators, true));
            
            // Call the bridge function
            $result = getTechnicalAnalysis($symbol, $indicators, $timeframe);
            
            // تسجيل النتيجة للتصحيح
            error_log("Technical Analysis Result: " . print_r($result, true));
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'symbol' => $symbol,
                    'name' => $result['data']['name'] ?? 'Sample Stock',
                    'timeframe' => $timeframe,
                    'indicators' => $result['data']['indicators'] ?? [],
                    'analysis_date' => $result['data']['analysis_date'] ?? date('Y-m-d H:i:s'),
                    'trend' => $result['data']['trend'] ?? 'neutral',
                    'support_levels' => $result['data']['support_levels'] ?? [],
                    'resistance_levels' => $result['data']['resistance_levels'] ?? []
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get technical analysis');
            }
            break;
            
        case 'fundamental':
            // Get parameters from the request
            $symbol = $_GET['symbol'] ?? '2222.SR';
            
            // Handle array parameters correctly
            $metrics = isset($_GET['metrics']) ? (is_array($_GET['metrics']) ? $_GET['metrics'] : [$_GET['metrics']]) : ['PE', 'PB', 'ROE', 'EPS'];
            
            // Call the bridge function
            $result = getFundamentalAnalysis($symbol, $metrics);
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'symbol' => $symbol,
                    'name' => $result['data']['name'] ?? 'Sample Stock',
                    'metrics' => $result['data']['metrics'] ?? [],
                    'analysis_date' => $result['data']['analysis_date'] ?? date('Y-m-d H:i:s'),
                    'valuation' => $result['data']['valuation'] ?? 'fair',
                    'sector_comparison' => $result['data']['sector_comparison'] ?? []
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get fundamental analysis');
            }
            break;
            
        case 'market':
            // Get parameters from the request
            // Handle array parameters correctly
            $symbols = isset($_GET['symbols']) ? (is_array($_GET['symbols']) ? $_GET['symbols'] : [$_GET['symbols']]) : ['2222.SR', '1211.SR'];
            $dataTypes = isset($_GET['data_types']) ? (is_array($_GET['data_types']) ? $_GET['data_types'] : [$_GET['data_types']]) : ['price', 'volume', 'market_cap'];
            
            // Call the bridge function
            $result = collectMarketData($symbols, $dataTypes);
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'symbols' => $symbols,
                    'data' => $result['data'] ?? [],
                    'collection_date' => $result['collection_date'] ?? date('Y-m-d H:i:s')
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get market data');
            }
            break;
            
        case 'financial':
            // Get parameters from the request
            // Handle array parameters correctly
            $symbols = isset($_GET['symbols']) ? (is_array($_GET['symbols']) ? $_GET['symbols'] : [$_GET['symbols']]) : ['2222.SR', '1211.SR'];
            $statementTypes = isset($_GET['statement_types']) ? (is_array($_GET['statement_types']) ? $_GET['statement_types'] : [$_GET['statement_types']]) : ['income', 'balance', 'cash_flow'];
            $periods = isset($_GET['periods']) ? (is_array($_GET['periods']) ? $_GET['periods'] : [$_GET['periods']]) : ['annual', 'quarterly'];
            
            // Call the bridge function
            $result = collectFinancialData($symbols, $statementTypes, $periods);
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'symbols' => $symbols,
                    'data' => $result['data'] ?? [],
                    'collection_date' => $result['collection_date'] ?? date('Y-m-d H:i:s')
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get financial data');
            }
            break;
            
        case 'sentiment':
            // Get parameters from the request
            // Handle array parameters correctly
            $symbols = isset($_GET['symbols']) ? (is_array($_GET['symbols']) ? $_GET['symbols'] : [$_GET['symbols']]) : ['2222.SR', '1211.SR'];
            $sources = isset($_GET['sources']) ? (is_array($_GET['sources']) ? $_GET['sources'] : [$_GET['sources']]) : ['news', 'social_media', 'analyst_ratings'];
            $timeRange = $_GET['time_range'] ?? '1w';
            
            // Call the bridge function
            $result = analyzeSentiment($symbols, $sources, $timeRange);
            
            // Format the response
            if ($result['success']) {
                $response = [
                    'success' => true,
                    'symbols' => $symbols,
                    'sentiment' => $result['data'] ?? [],
                    'analysis_date' => $result['analysis_date'] ?? date('Y-m-d H:i:s')
                ];
            } else {
                throw new Exception($result['error'] ?? 'Failed to get sentiment analysis');
            }
            break;
            
        default:
            throw new Exception("Unknown action: {$action}");
    }
    
    // Output the response
    echo json_encode($response);
    
} catch (Exception $e) {
    // تسجيل الخطأ
    error_log("API Error: " . $e->getMessage());
    error_log("Stack trace: " . $e->getTraceAsString());
    
    // Handle errors
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'action' => $action ?? 'unknown',
        'request_uri' => $_SERVER['REQUEST_URI'],
        'timestamp' => date('Y-m-d H:i:s')
    ]);
}