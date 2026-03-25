<?php
/**
 * TASI3 Integration Bridge
 * 
 * This file serves as a bridge between the PHP backend and the Python integration system.
 * It provides functions to call the Python integration script with appropriate parameters.
 */

/**
 * Execute the Python integration script with the given parameters
 * 
 * @param array $params Parameters to pass to the integration script
 * @return array Result from the integration script
 */
function executeIntegration(array $params): array
{
    try {
        // تسجيل المعلمات للتصحيح
        error_log("Integration parameters: " . print_r($params, true));
        
        // Path to the Python integration script
        // Use actual system integration for live data
        $scriptPath = __DIR__ . '/system_integration.py';
        
        // Ensure the script exists
        if (!file_exists($scriptPath)) {
            throw new Exception("Integration script not found: {$scriptPath}");
        }
        
        // Convert parameters to JSON
        $jsonParams = json_encode($params, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Error encoding parameters: " . json_last_error_msg());
        }
        
        // تسجيل JSON للتصحيح
        error_log("JSON parameters: " . $jsonParams);
        
        // تأمين المعلمات باستخدام escapeshellarg بدلاً من str_replace اليدوي
        $escapedParams = escapeshellarg($jsonParams);
        $escapedScript = escapeshellarg($scriptPath);

        // Execute the Python script
        $pythonExecutable = 'python'; // or 'python3' depending on the environment
        $command = "{$pythonExecutable} {$escapedScript} {$escapedParams} 2>&1";

        // تسجيل الأمر للتصحيح
        error_log("Executing command: " . $command);

        // Execute the command with timeout via proc_open for safety
        $output = shell_exec($command);
        
        // تسجيل الإخراج للتصحيح
        error_log("Command output: " . ($output ?? 'NULL'));
        
        if ($output === null) {
            throw new Exception("Error executing integration script");
        }
        
        // Parse the JSON output
        $result = json_decode($output, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Error decoding script output: " . json_last_error_msg() . " - Output: " . substr($output, 0, 1000));
        }
        
        // تسجيل النتيجة للتصحيح
        error_log("Integration result: " . print_r($result, true));
        
        return $result;
    } catch (Exception $e) {
        // Log the error
        error_log("Integration error: " . $e->getMessage());
        error_log("Stack trace: " . $e->getTraceAsString());
        
        // Return error response
        return [
            'success' => false,
            'error' => $e->getMessage(),
            'params' => $params
        ];
    }
}

/**
 * Get investment recommendations
 * 
 * @param string $riskProfile Risk profile (conservative, moderate, aggressive)
 * @param string $investmentHorizon Investment horizon (short, medium, long)
 * @param array $sectors Optional list of sectors to include
 * @param array $excludeSymbols Optional list of symbols to exclude
 * @param int $maxResults Optional maximum number of recommendations
 * @return array Recommendation results
 */
function getRecommendations(
    string $riskProfile,
    string $investmentHorizon,
    array $sectors = [],
    array $excludeSymbols = [],
    int $maxResults = 10
): array {
    $params = [
        'action' => 'recommend',
        'risk_profile' => $riskProfile,
        'investment_horizon' => $investmentHorizon,
        'sectors' => $sectors,
        'exclude_symbols' => $excludeSymbols,
        'max_results' => $maxResults
    ];
    
    return executeIntegration($params);
}

/**
 * Get technical analysis for a symbol
 * 
 * @param string $symbol Stock symbol
 * @param array $indicators List of technical indicators to calculate
 * @param string $timeframe Timeframe for analysis (daily, weekly, monthly)
 * @return array Technical analysis results
 */
function getTechnicalAnalysis(
    string $symbol,
    array $indicators,
    string $timeframe = 'daily'
): array {
    $params = [
        'action' => 'technical',
        'symbol' => $symbol,
        'indicators' => $indicators,
        'timeframe' => $timeframe
    ];
    
    return executeIntegration($params);
}

/**
 * Get fundamental analysis for a symbol
 * 
 * @param string $symbol Stock symbol
 * @param array $metrics List of fundamental metrics to calculate
 * @return array Fundamental analysis results
 */
function getFundamentalAnalysis(
    string $symbol,
    array $metrics
): array {
    $params = [
        'action' => 'fundamental',
        'symbol' => $symbol,
        'metrics' => $metrics
    ];
    
    return executeIntegration($params);
}

/**
 * Collect market data for symbols
 * 
 * @param array $symbols List of stock symbols
 * @param array $dataTypes List of market data types to collect
 * @return array Collected market data
 */
function collectMarketData(
    array $symbols,
    array $dataTypes = ['price', 'volume', 'market_cap']
): array {
    $params = [
        'action' => 'market',
        'symbols' => $symbols,
        'data_types' => $dataTypes
    ];
    
    return executeIntegration($params);
}

/**
 * Collect financial data for symbols
 * 
 * @param array $symbols List of stock symbols
 * @param array $statementTypes List of financial statement types
 * @param array $periods List of reporting periods
 * @return array Collected financial data
 */
function collectFinancialData(
    array $symbols,
    array $statementTypes = ['income', 'balance', 'cash_flow'],
    array $periods = ['annual', 'quarterly']
): array {
    $params = [
        'action' => 'financial',
        'symbols' => $symbols,
        'statement_types' => $statementTypes,
        'periods' => $periods
    ];
    
    return executeIntegration($params);
}

/**
 * Analyze sentiment for symbols
 * 
 * @param array $symbols List of stock symbols
 * @param array $sources List of sources for sentiment data
 * @param string $timeRange Time range for sentiment data
 * @return array Sentiment analysis results
 */
function analyzeSentiment(
    array $symbols,
    array $sources = ['news', 'social_media', 'analyst_ratings'],
    string $timeRange = '1w'
): array {
    $params = [
        'action' => 'sentiment',
        'symbols' => $symbols,
        'sources' => $sources,
        'time_range' => $timeRange
    ];
    
    return executeIntegration($params);
}

/**
 * Process financial data
 * 
 * @param array $data Financial data to process
 * @param string $processingType Type of processing to apply
 * @param array $options Processing options
 * @return array Processed data
 */
function processFinancialData(
    array $data,
    string $processingType,
    array $options = []
): array {
    $params = [
        'action' => 'process_financial_data',
        'data' => $data,
        'processing_type' => $processingType,
        'options' => $options
    ];
    
    return executeIntegration($params);
}