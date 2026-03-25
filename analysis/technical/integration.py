#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration Module for Technical Analysis

This module provides integration functions for the technical analysis components,
allowing them to be called from external systems like the PHP backend.
"""

import json
import sys
import logging
from typing import Dict, List, Any, Union

# Import technical analysis components
from analysis.technical.analyzer import TechnicalAnalyzer
from analysis.technical.indicators import calculate_indicators

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('technical_integration')

def parse_input() -> Dict[str, Any]:
    """
    Parse input parameters from command line arguments.
    
    Returns:
        Dict[str, Any]: Dictionary containing parsed parameters
    """
    try:
        if len(sys.argv) < 2:
            logger.error("No input parameters provided")
            return {}
        
        # Parse JSON input from command line
        params_json = sys.argv[1]
        params = json.loads(params_json)
        
        logger.info(f"Received parameters: {params}")
        return params
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON input: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error parsing input: {e}")
        return {}

def perform_technical_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform technical analysis based on provided parameters.
    
    Args:
        params (Dict[str, Any]): Parameters for technical analysis
            - symbol: str - Stock symbol
            - indicators: List[str] - List of indicators to calculate
            - timeframe: str (optional) - Timeframe for analysis ('daily', 'weekly', 'monthly')
    
    Returns:
        Dict[str, Any]: Technical analysis results
    """
    try:
        # Validate required parameters
        if 'symbol' not in params or 'indicators' not in params:
            return {
                'success': False,
                'error': 'Missing required parameters: symbol and indicators'
            }
        
        symbol = params['symbol']
        indicators = params['indicators']
        timeframe = params.get('timeframe', 'daily')
        
        # Initialize technical analyzer
        analyzer = TechnicalAnalyzer()
        
        # Get historical data for the symbol
        historical_data = analyzer.get_historical_data(symbol, timeframe)
        
        if not historical_data:
            return {
                'success': False,
                'error': f'No historical data found for symbol: {symbol}'
            }
        
        # Calculate requested indicators
        results = {}
        for indicator in indicators:
            indicator_result = analyzer.calculate_indicator(
                data=historical_data,
                indicator=indicator
            )
            if indicator_result:
                results[indicator] = indicator_result
        
        # Add trend analysis
        trend_analysis = analyzer.analyze_trends(historical_data)
        
        return {
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'indicators': results,
            'trend_analysis': trend_analysis,
            'last_updated': analyzer.get_last_update_time(symbol)
        }
    except Exception as e:
        logger.error(f"Error performing technical analysis: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_available_indicators() -> Dict[str, Any]:
    """
    Get list of available technical indicators.
    
    Returns:
        Dict[str, Any]: List of available indicators with descriptions
    """
    try:
        # This would typically come from a configuration or the indicators module
        available_indicators = {
            'SMA': 'Simple Moving Average',
            'EMA': 'Exponential Moving Average',
            'RSI': 'Relative Strength Index',
            'MACD': 'Moving Average Convergence Divergence',
            'BB': 'Bollinger Bands',
            'ATR': 'Average True Range',
            'OBV': 'On-Balance Volume',
            'ADX': 'Average Directional Index',
            'Stochastic': 'Stochastic Oscillator',
            'CCI': 'Commodity Channel Index'
        }
        
        return {
            'success': True,
            'indicators': available_indicators
        }
    except Exception as e:
        logger.error(f"Error getting available indicators: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    Main function to handle integration requests.
    """
    try:
        # Parse input parameters
        params = parse_input()
        if not params:
            result = {
                'success': False,
                'error': 'Invalid or missing input parameters'
            }
        else:
            # Determine which function to call based on action parameter
            action = params.get('action', 'analyze')
            
            if action == 'analyze':
                result = perform_technical_analysis(params)
            elif action == 'get_indicators':
                result = get_available_indicators()
            else:
                result = {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
        
        # Output result as JSON
        print(json.dumps(result))
    except Exception as e:
        logger.error(f"Unexpected error in integration: {e}")
        print(json.dumps({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }))

if __name__ == "__main__":
    main()