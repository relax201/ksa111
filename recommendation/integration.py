#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration Module for Recommendation Engine

This module provides integration functions for the recommendation engine,
allowing it to be called from external systems like the PHP backend.
"""

import json
import sys
import logging
from typing import Dict, List, Any, Union

# Import recommendation engine components
from recommendation.engine import RecommendationEngine
from recommendation.portfolio import PortfolioOptimizer
from recommendation.screener import StockScreener
from recommendation.models import load_model
from recommendation.utils import setup_logging

# Setup logging
logger = setup_logging('integration')

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

def get_recommendations(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get investment recommendations based on provided parameters.
    
    Args:
        params (Dict[str, Any]): Parameters for recommendation generation
            - risk_profile: str - 'conservative', 'moderate', or 'aggressive'
            - investment_horizon: str - 'short', 'medium', or 'long'
            - sectors: List[str] (optional) - List of sectors to include
            - exclude_symbols: List[str] (optional) - Symbols to exclude
            - max_results: int (optional) - Maximum number of recommendations
    
    Returns:
        Dict[str, Any]: Recommendation results
    """
    try:
        # Validate required parameters
        if 'risk_profile' not in params or 'investment_horizon' not in params:
            return {
                'success': False,
                'error': 'Missing required parameters: risk_profile and investment_horizon'
            }
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        # Get recommendations
        recommendations = engine.get_recommendations(
            risk_profile=params['risk_profile'],
            investment_horizon=params['investment_horizon'],
            sectors=params.get('sectors', []),
            exclude_symbols=params.get('exclude_symbols', []),
            max_results=params.get('max_results', 10)
        )
        
        return {
            'success': True,
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def optimize_portfolio(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize a portfolio based on provided parameters.
    
    Args:
        params (Dict[str, Any]): Parameters for portfolio optimization
            - holdings: List[Dict] - Current portfolio holdings
            - risk_tolerance: float - Risk tolerance level (0-1)
            - target_return: float (optional) - Target return
    
    Returns:
        Dict[str, Any]: Portfolio optimization results
    """
    try:
        # Validate required parameters
        if 'holdings' not in params or 'risk_tolerance' not in params:
            return {
                'success': False,
                'error': 'Missing required parameters: holdings and risk_tolerance'
            }
        
        # Initialize portfolio optimizer
        optimizer = PortfolioOptimizer()
        
        # Optimize portfolio
        optimization_result = optimizer.optimize(
            holdings=params['holdings'],
            risk_tolerance=params['risk_tolerance'],
            target_return=params.get('target_return')
        )
        
        return {
            'success': True,
            'optimization': optimization_result
        }
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def screen_stocks(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Screen stocks based on provided criteria.
    
    Args:
        params (Dict[str, Any]): Parameters for stock screening
            - criteria: Dict[str, Any] - Screening criteria
            - max_results: int (optional) - Maximum number of results
    
    Returns:
        Dict[str, Any]: Stock screening results
    """
    try:
        # Validate required parameters
        if 'criteria' not in params:
            return {
                'success': False,
                'error': 'Missing required parameter: criteria'
            }
        
        # Initialize stock screener
        screener = StockScreener()
        
        # Screen stocks
        screening_result = screener.screen(
            criteria=params['criteria'],
            max_results=params.get('max_results', 50)
        )
        
        return {
            'success': True,
            'results': screening_result
        }
    except Exception as e:
        logger.error(f"Error screening stocks: {e}")
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
            action = params.get('action', 'recommend')
            
            if action == 'recommend':
                result = get_recommendations(params)
            elif action == 'optimize':
                result = optimize_portfolio(params)
            elif action == 'screen':
                result = screen_stocks(params)
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