#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TASI3 Mock Integration System

This script provides mock implementations of the integration system for testing purposes.
It returns simulated data for each action to verify that the integration works correctly.
"""

import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mock_integration")

def generate_mock_data(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate mock data for testing purposes.
    
    Args:
        action: The requested action
        params: The parameters for the action
        
    Returns:
        Dictionary containing mock data for the action
    """
    mock_data = {'success': True, 'mock': True, 'timestamp': datetime.now().isoformat()}
    
    if action == 'recommend':
        risk_profile = params.get('risk_profile', 'moderate')
        investment_horizon = params.get('investment_horizon', 'medium')
        max_results = params.get('max_results', 5)
        
        recommendations = []
        for i in range(max_results):
            recommendations.append({
                'symbol': f"{2000 + i}.SR",
                'name': f"شركة {i}",
                'sector': 'تقنية المعلومات' if i % 2 == 0 else 'الرعاية الصحية',
                'recommendation': 'شراء' if i % 3 == 0 else ('احتفاظ' if i % 3 == 1 else 'بيع'),
                'target_price': round(100 + i * 10 + (0.1 * i), 2),
                'current_price': round(100 + i * 5, 2),
                'potential': f"{round(i * 5, 1)}%",
                'risk_score': round(0.3 + (0.1 * i), 2),
                'confidence': round(0.7 - (0.05 * i), 2)
            })
            
        mock_data['data'] = {
            'recommendations': recommendations,
            'risk_profile': risk_profile,
            'investment_horizon': investment_horizon,
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
    elif action == 'technical':
        symbol = params.get('symbol', '2222.SR')
        indicators = params.get('indicators', ['SMA', 'RSI', 'MACD'])
        timeframe = params.get('timeframe', 'daily')
        
        indicator_results = {}
        if 'SMA' in indicators:
            indicator_results['SMA'] = {
                '20': 105.75,
                '50': 98.32,
                '200': 92.15
            }
        if 'RSI' in indicators:
            indicator_results['RSI'] = {
                '14': 65.42
            }
        if 'MACD' in indicators:
            indicator_results['MACD'] = {
                'line': 2.35,
                'signal': 1.89,
                'histogram': 0.46
            }
            
        mock_data['data'] = {
            'symbol': symbol,
            'name': 'أرامكو',
            'timeframe': timeframe,
            'indicators': indicator_results,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'trend': 'صاعد' if len(indicator_results.keys()) % 2 == 0 else 'هابط',
            'support_levels': [95.20, 92.50, 90.00],
            'resistance_levels': [105.00, 108.75, 110.50]
        }
        
    elif action == 'fundamental':
        symbol = params.get('symbol', '2222.SR')
        metrics = params.get('metrics', ['PE', 'PB', 'ROE', 'EPS'])
        
        metric_results = {}
        if 'PE' in metrics:
            metric_results['PE'] = 15.75
        if 'PB' in metrics:
            metric_results['PB'] = 2.32
        if 'ROE' in metrics:
            metric_results['ROE'] = 0.1842
        if 'EPS' in metrics:
            metric_results['EPS'] = 6.35
            
        mock_data['data'] = {
            'symbol': symbol,
            'name': 'أرامكو',
            'metrics': metric_results,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'valuation': 'مقيمة بأقل من قيمتها' if sum(metric_results.values()) % 2 == 0 else 'مقيمة بأعلى من قيمتها',
            'sector_comparison': {
                'PE': {
                    'value': 15.75,
                    'sector_avg': 18.20,
                    'market_avg': 20.15
                },
                'PB': {
                    'value': 2.32,
                    'sector_avg': 2.50,
                    'market_avg': 2.75
                }
            }
        }
        
    elif action in ['market', 'financial']:
        symbols = params.get('symbols', ['2222.SR', '1211.SR'])
        
        data_results = {}
        for symbol in symbols:
            if action == 'market':
                data_results[symbol] = {
                    'price': round(100 + (ord(symbol[0]) % 10) * 10, 2),
                    'volume': int(1000000 + (ord(symbol[0]) % 10) * 100000),
                    'market_cap': int(1000000000 + (ord(symbol[0]) % 10) * 100000000),
                    'change': round((ord(symbol[0]) % 10 - 5) / 100, 4),
                    'change_percent': f"{round((ord(symbol[0]) % 10 - 5), 2)}%"
                }
            else:  # collect_financial_data
                data_results[symbol] = {
                    'income': {
                        'revenue': [100000000, 120000000, 150000000],
                        'net_income': [10000000, 15000000, 20000000],
                        'eps': [5.0, 7.5, 10.0]
                    },
                    'balance': {
                        'total_assets': [500000000, 550000000, 600000000],
                        'total_liabilities': [300000000, 320000000, 350000000],
                        'equity': [200000000, 230000000, 250000000]
                    },
                    'cash_flow': {
                        'operating': [30000000, 35000000, 40000000],
                        'investing': [-20000000, -25000000, -30000000],
                        'financing': [-5000000, -10000000, -15000000]
                    }
                }
                
        mock_data['data'] = {
            'symbols': symbols,
            'data': data_results,
            'collection_date': datetime.now().strftime('%Y-%m-%d')
        }
        
    elif action == 'sentiment':
        symbols = params.get('symbols', ['2222.SR', '1211.SR'])
        sources = params.get('sources', ['news', 'social_media', 'analyst_ratings'])
        
        sentiment_results = {}
        for symbol in symbols:
            sentiment_results[symbol] = {
                'overall_score': round(0.5 + (ord(symbol[0]) % 10 - 5) / 20, 2),
                'sources': {}
            }
            
            if 'news' in sources:
                sentiment_results[symbol]['sources']['news'] = {
                    'score': round(0.5 + (ord(symbol[0]) % 10 - 5) / 15, 2),
                    'articles_count': 10 + (ord(symbol[0]) % 10),
                    'positive_count': 6 + (ord(symbol[0]) % 5),
                    'negative_count': 4 - (ord(symbol[0]) % 3)
                }
                
            if 'social_media' in sources:
                sentiment_results[symbol]['sources']['social_media'] = {
                    'score': round(0.5 + (ord(symbol[0]) % 10 - 5) / 25, 2),
                    'mentions_count': 100 + (ord(symbol[0]) % 10) * 10,
                    'positive_count': 60 + (ord(symbol[0]) % 10) * 5,
                    'negative_count': 40 - (ord(symbol[0]) % 10) * 3
                }
                
            if 'analyst_ratings' in sources:
                sentiment_results[symbol]['sources']['analyst_ratings'] = {
                    'score': round(0.5 + (ord(symbol[0]) % 10 - 5) / 10, 2),
                    'buy_count': 3 + (ord(symbol[0]) % 3),
                    'hold_count': 2,
                    'sell_count': 1 - (ord(symbol[0]) % 2)
                }
                
        mock_data['data'] = {
            'symbols': symbols,
            'sentiment': sentiment_results,
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
    elif action == 'process_financial_data':
        data = params.get('data', {})
        processing_type = params.get('processing_type', 'normalization')
        
        # Just return the same data with a processing flag for mock purposes
        mock_data['data'] = {
            'processed_data': data,
            'processing_type': processing_type,
            'processing_date': datetime.now().strftime('%Y-%m-%d'),
            'processing_status': 'completed'
        }
        
    return mock_data

def main():
    """
    Main function to handle integration requests.
    """
    try:
        # Check if parameters are provided
        if len(sys.argv) < 2:
            result = {'success': False, 'error': 'No parameters provided'}
            print(json.dumps(result))
            return
            
        # Parse the JSON parameters
        params_json = sys.argv[1]
        try:
            params = json.loads(params_json)
            logger.info(f"Received parameters: {params}")
        except json.JSONDecodeError as e:
            result = {'success': False, 'error': f'Invalid JSON parameters: {str(e)}'}
            print(json.dumps(result))
            return
            
        # Get the action from parameters
        action = params.get('action')
        if not action:
            result = {'success': False, 'error': 'No action specified'}
            print(json.dumps(result))
            return
            
        # Generate mock data for the action
        result = generate_mock_data(action, params)
        
        # Output result as JSON
        print(json.dumps(result))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        print(json.dumps({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }))

if __name__ == "__main__":
    main()