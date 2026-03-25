<?php
/**
 * TASI3 Integration Runner
 * 
 * This script runs the integration system with the specified parameters.
 */

// Get the action from command line arguments
$action = isset($argv[1]) ? $argv[1] : 'recommend';

// Parameters to pass to the integration system based on the action
switch ($action) {
    case 'recommend':
        $params = [
            'action' => 'recommend',
            'risk_profile' => 'moderate',
            'investment_horizon' => 'medium',
            'sectors' => ['technology', 'healthcare'],
            'exclude_symbols' => ['AAPL', 'MSFT'],
            'max_results' => 5
        ];
        break;
    case 'technical':
        $params = [
            'action' => 'technical_analysis',
            'symbol' => '2222.SR',
            'indicators' => ['SMA', 'RSI', 'MACD'],
            'timeframe' => 'daily'
        ];
        break;
    case 'fundamental':
        $params = [
            'action' => 'fundamental_analysis',
            'symbol' => '2222.SR',
            'metrics' => ['PE', 'PB', 'ROE', 'EPS']
        ];
        break;
    case 'market':
        $params = [
            'action' => 'collect_market_data',
            'symbols' => ['2222.SR', '1211.SR'],
            'data_types' => ['price', 'volume', 'market_cap']
        ];
        break;
    case 'financial':
        $params = [
            'action' => 'collect_financial_data',
            'symbols' => ['2222.SR', '1211.SR'],
            'statement_types' => ['income', 'balance', 'cash_flow'],
            'periods' => ['annual', 'quarterly']
        ];
        break;
    case 'sentiment':
        $params = [
            'action' => 'analyze_sentiment',
            'symbols' => ['2222.SR', '1211.SR'],
            'sources' => ['news', 'social_media', 'analyst_ratings'],
            'time_range' => '1w'
        ];
        break;
    case 'process':
        $params = [
            'action' => 'process_financial_data',
            'data' => [
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
            ],
            'processing_type' => 'normalization',
            'options' => ['method' => 'min_max']
        ];
        break;
    default:
        echo "Unknown action: {$action}\n";
        echo "Available actions: recommend, technical, fundamental, market, financial, sentiment, process\n";
        exit(1);
}

// Convert parameters to JSON
$jsonParams = json_encode($params);

// Escape the JSON string for shell execution
// Use double quotes for Windows and make sure to properly escape the JSON string
$escapedParams = '"' . str_replace('"', '\"', $jsonParams) . '"';

// Path to the Python integration script
$scriptPath = __DIR__ . '/mock_integration.py';

// Execute the Python script
$pythonExecutable = 'python';
$command = "{$pythonExecutable} {$scriptPath} {$escapedParams}";

// Execute the command and capture output
$output = shell_exec($command);

// Display the output
echo $output;