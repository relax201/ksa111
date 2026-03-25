#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration Module for Data Collection and Processing

This module provides integration functions for data collection and processing components,
allowing them to be called from external systems like the PHP backend.
"""

import json
import sys
import logging
from typing import Dict, List, Any, Union

# Import data collection and processing components
from data.collectors.market_data_collector import MarketDataCollector
from data.collectors.financial_data_collector import FinancialDataCollector
from data.collectors.sentiment_analyzer import SentimentAnalyzer
from data.processors.financial_data_processor import FinancialDataProcessor
from data.storage.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_integration')

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

def collect_market_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect market data for specified symbols.
    
    Args:
        params (Dict[str, Any]): Parameters for data collection
            - symbols: List[str] - List of stock symbols
            - data_types: List[str] (optional) - Types of market data to collect
    
    Returns:
        Dict[str, Any]: Collected market data
    """
    try:
        # Validate required parameters
        if 'symbols' not in params:
            return {
                'success': False,
                'error': 'Missing required parameter: symbols'
            }
        
        symbols = params['symbols']
        data_types = params.get('data_types', ['price', 'volume', 'market_cap'])
        
        # Initialize market data collector
        collector = MarketDataCollector()
        
        # Collect market data
        market_data = collector.collect_data(symbols, data_types)
        
        return {
            'success': True,
            'data': market_data,
            'last_updated': collector.get_last_update_time()
        }
    except Exception as e:
        logger.error(f"Error collecting market data: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def collect_financial_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect financial data for specified symbols.
    
    Args:
        params (Dict[str, Any]): Parameters for data collection
            - symbols: List[str] - List of stock symbols
            - statement_types: List[str] (optional) - Types of financial statements
            - periods: List[str] (optional) - Reporting periods
    
    Returns:
        Dict[str, Any]: Collected financial data
    """
    try:
        # Validate required parameters
        if 'symbols' not in params:
            return {
                'success': False,
                'error': 'Missing required parameter: symbols'
            }
        
        symbols = params['symbols']
        statement_types = params.get('statement_types', ['income', 'balance', 'cash_flow'])
        periods = params.get('periods', ['annual', 'quarterly'])
        
        # Initialize financial data collector
        collector = FinancialDataCollector()
        
        # Collect financial data
        financial_data = collector.collect_data(symbols, statement_types, periods)
        
        return {
            'success': True,
            'data': financial_data,
            'last_updated': collector.get_last_update_time()
        }
    except Exception as e:
        logger.error(f"Error collecting financial data: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def analyze_sentiment(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze sentiment for specified symbols.
    
    Args:
        params (Dict[str, Any]): Parameters for sentiment analysis
            - symbols: List[str] - List of stock symbols
            - sources: List[str] (optional) - Sources for sentiment data
            - time_range: str (optional) - Time range for sentiment data
    
    Returns:
        Dict[str, Any]: Sentiment analysis results
    """
    try:
        # Validate required parameters
        if 'symbols' not in params:
            return {
                'success': False,
                'error': 'Missing required parameter: symbols'
            }
        
        symbols = params['symbols']
        sources = params.get('sources', ['news', 'social_media', 'analyst_ratings'])
        time_range = params.get('time_range', '1w')  # Default to 1 week
        
        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer()
        
        # Analyze sentiment
        sentiment_data = analyzer.analyze(symbols, sources, time_range)
        
        return {
            'success': True,
            'data': sentiment_data,
            'last_updated': analyzer.get_last_update_time()
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def process_financial_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process financial data.
    
    Args:
        params (Dict[str, Any]): Parameters for data processing
            - data: Dict[str, Any] - Financial data to process
            - processing_type: str - Type of processing to apply
            - options: Dict[str, Any] (optional) - Processing options
    
    Returns:
        Dict[str, Any]: Processed data
    """
    try:
        # Validate required parameters
        if 'data' not in params or 'processing_type' not in params:
            return {
                'success': False,
                'error': 'Missing required parameters: data and processing_type'
            }
        
        data = params['data']
        processing_type = params['processing_type']
        options = params.get('options', {})
        
        # Initialize data processor
        processor = FinancialDataProcessor()
        
        # Process data
        processed_data = processor.process(data, processing_type, options)
        
        return {
            'success': True,
            'data': processed_data
        }
    except Exception as e:
        logger.error(f"Error processing financial data: {e}")
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
            action = params.get('action', 'collect_market')
            
            if action == 'collect_market':
                result = collect_market_data(params)
            elif action == 'collect_financial':
                result = collect_financial_data(params)
            elif action == 'analyze_sentiment':
                result = analyze_sentiment(params)
            elif action == 'process_data':
                result = process_financial_data(params)
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