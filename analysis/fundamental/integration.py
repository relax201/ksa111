#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration Module for Fundamental Analysis

This module provides integration functions for the fundamental analysis components,
allowing them to be called from external systems like the PHP backend.
"""

import json
import sys
import logging
from typing import Dict, List, Any, Union

# Import fundamental analysis components
from analysis.fundamental.analyzer import FundamentalAnalyzer
from analysis.fundamental.ratios import calculate_ratios
from analysis.fundamental.valuation import calculate_valuation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fundamental_integration')

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

def perform_fundamental_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform fundamental analysis based on provided parameters.
    
    Args:
        params (Dict[str, Any]): Parameters for fundamental analysis
            - symbol: str - Stock symbol
            - metrics: List[str] - List of metrics to calculate
    
    Returns:
        Dict[str, Any]: Fundamental analysis results
    """
    try:
        # Validate required parameters
        if 'symbol' not in params or 'metrics' not in params:
            return {
                'success': False,
                'error': 'Missing required parameters: symbol and metrics'
            }
        
        symbol = params['symbol']
        metrics = params['metrics']
        
        # Initialize fundamental analyzer
        analyzer = FundamentalAnalyzer()
        
        # Get financial data for the symbol
        financial_data = analyzer.get_financial_data(symbol)
        
        if not financial_data:
            return {
                'success': False,
                'error': f'No financial data found for symbol: {symbol}'
            }
        
        # Calculate requested metrics
        results = {}
        
        # Group metrics by category
        ratio_metrics = [m for m in metrics if m in analyzer.get_available_ratios()]
        valuation_metrics = [m for m in metrics if m in analyzer.get_available_valuations()]
        statement_metrics = [m for m in metrics if m in analyzer.get_available_statement_items()]
        
        # Calculate ratios
        if ratio_metrics:
            results['ratios'] = analyzer.calculate_ratios(financial_data, ratio_metrics)
        
        # Calculate valuations
        if valuation_metrics:
            results['valuations'] = analyzer.calculate_valuations(financial_data, valuation_metrics)
        
        # Get statement items
        if statement_metrics:
            results['statements'] = analyzer.get_statement_items(financial_data, statement_metrics)
        
        # Add company profile
        company_profile = analyzer.get_company_profile(symbol)
        
        return {
            'success': True,
            'symbol': symbol,
            'metrics': results,
            'company_profile': company_profile,
            'last_updated': analyzer.get_last_update_time(symbol)
        }
    except Exception as e:
        logger.error(f"Error performing fundamental analysis: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_available_metrics() -> Dict[str, Any]:
    """
    Get list of available fundamental metrics.
    
    Returns:
        Dict[str, Any]: List of available metrics with descriptions
    """
    try:
        # Initialize fundamental analyzer
        analyzer = FundamentalAnalyzer()
        
        # Get available metrics
        ratios = analyzer.get_available_ratios()
        valuations = analyzer.get_available_valuations()
        statement_items = analyzer.get_available_statement_items()
        
        return {
            'success': True,
            'metrics': {
                'ratios': ratios,
                'valuations': valuations,
                'statement_items': statement_items
            }
        }
    except Exception as e:
        logger.error(f"Error getting available metrics: {e}")
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
                result = perform_fundamental_analysis(params)
            elif action == 'get_metrics':
                result = get_available_metrics()
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