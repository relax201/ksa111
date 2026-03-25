"""
Enhanced Recommendation Engine for Saudi Stock Market (Tadawul)

This module integrates machine learning models with enhanced data sources
to generate more accurate stock recommendations.
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

# Import internal modules
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.storage.database_manager import DatabaseManager
from data.collectors.enhanced_data_collector import EnhancedDataCollector
from analysis.models.ml_recommendation_model import MLRecommendationModel
from analysis.technical.indicators import calculate_indicators
from analysis.fundamental.ratios import calculate_ratios
from recommendation.engine import RecommendationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedRecommendationEngine:
    """
    Enhanced recommendation engine that integrates machine learning models
    with multiple data sources to generate more accurate stock recommendations.
    """
    
    def __init__(self, db_path: str = 'tasi_data.db', model_dir: str = 'models', cache_dir: str = 'cache'):
        """
        Initialize the enhanced recommendation engine.
        
        Args:
            db_path: Path to the SQLite database
            model_dir: Directory to save/load ML models
            cache_dir: Directory to cache data
        """
        self.db_manager = DatabaseManager(db_path)
        self.data_collector = EnhancedDataCollector(cache_dir)
        self.ml_model = MLRecommendationModel(model_dir)
        self.base_engine = RecommendationEngine()
        
        # Create directories if they don't exist
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        # Model weights for ensemble
        self.model_weights = {
            'random_forest': 0.4,
            'gradient_boosting': 0.4,
            'neural_network': 0.2
        }
        
        # Feature importance (will be updated during training)
        self.feature_importance = {}
    
    def prepare_training_data(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Prepare training data for the ML model.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with training data
        """
        logger.info(f"Preparing training data for {len(symbols)} symbols from {start_date} to {end_date}")
        
        all_data = []
        
        for symbol in symbols:
            try:
                # Get market data
                market_data = self.db_manager.get_market_data(symbol, start_date, end_date)
                
                if market_data.empty:
                    logger.warning(f"No market data found for {symbol}")
                    continue
                
                # Calculate technical indicators
                market_data_with_indicators = calculate_indicators(market_data)
                
                # Get fundamental data
                income_stmt = self.db_manager.get_financial_statement(symbol, 'income', 'annual')
                balance_sheet = self.db_manager.get_financial_statement(symbol, 'balance', 'annual')
                cash_flow = self.db_manager.get_financial_statement(symbol, 'cash_flow', 'annual')
                
                # Calculate fundamental ratios
                ratios = calculate_ratios(income_stmt, balance_sheet, cash_flow)
                
                # Convert ratios to DataFrame
                if ratios:
                    ratios_df = pd.DataFrame([ratios])
                    ratios_df.index = [market_data.index[-1]]  # Use the last date
                    
                    # Join market data with ratios
                    # We'll forward fill the ratios for all dates
                    for col in ratios_df.columns:
                        market_data_with_indicators[col] = ratios_df[col].iloc[0]
                
                # Get enhanced data
                enhanced_data = self.data_collector.collect_enhanced_data(symbol)
                
                # Add enhanced data features
                if enhanced_data:
                    # News sentiment
                    market_data_with_indicators['news_sentiment'] = enhanced_data.get('news', {}).get('sentiment', 0)
                    
                    # Social sentiment
                    market_data_with_indicators['social_sentiment'] = enhanced_data.get('social', {}).get('sentiment', 0)
                    
                    # Analyst consensus
                    consensus = enhanced_data.get('analyst', {}).get('consensus', 'N/A')
                    if consensus != 'N/A':
                        consensus_map = {
                            'Strong Buy': 2,
                            'Buy': 1,
                            'Hold': 0,
                            'Sell': -1,
                            'Strong Sell': -2
                        }
                        market_data_with_indicators['analyst_rating'] = consensus_map.get(consensus, 0)
                    else:
                        market_data_with_indicators['analyst_rating'] = 0
                    
                    # Target price
                    target_price = enhanced_data.get('analyst', {}).get('target_price', 0)
                    if target_price > 0:
                        market_data_with_indicators['target_price'] = target_price
                        market_data_with_indicators['target_price_ratio'] = target_price / market_data_with_indicators['close']
                    
                    # Institutional ownership
                    market_data_with_indicators['institutional_ownership'] = enhanced_data.get('institutional', {}).get('ownership', 0)
                
                # Create target variable
                # Example: 1 if price increases by 5% or more in the next 20 days, 0 otherwise
                market_data_with_indicators['future_price'] = market_data_with_indicators['close'].shift(-20)
                market_data_with_indicators['future_return'] = market_data_with_indicators['future_price'] / market_data_with_indicators['close'] - 1
                market_data_with_indicators['target'] = (market_data_with_indicators['future_return'] > 0.05).astype(int)
                
                # Add symbol column
                market_data_with_indicators['symbol'] = symbol
                
                # Add to all data
                all_data.append(market_data_with_indicators)
                
                logger.info(f"Prepared training data for {symbol} with {len(market_data_with_indicators)} rows")
                
            except Exception as e:
                logger.error(f"Error preparing training data for {symbol}: {e}")
        
        # Combine all data
        if all_data:
            combined_data = pd.concat(all_data)
            logger.info(f"Combined training data with {len(combined_data)} rows")
            return combined_data
        else:
            logger.warning("No training data prepared")
            return pd.DataFrame()
    
    def train_models(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """
        Train machine learning models for stock recommendations.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with training results
        """
        # Prepare training data
        training_data = self.prepare_training_data(symbols, start_date, end_date)
        
        if training_data.empty:
            logger.error("No training data available")
            return {'error': 'No training data available'}
        
        # Train models
        logger.info("Training machine learning models")
        
        results = {}
        
        # Train random forest model
        try:
            rf_result = self.ml_model.train(
                training_data, 
                model_type='random_forest',
                feature_selection=True,
                optimize_hyperparams=True
            )
            results['random_forest'] = rf_result
            
            # Update feature importance
            self.feature_importance['random_forest'] = rf_result.get('feature_importance', {})
            
            logger.info(f"Random Forest model trained with F1 score: {rf_result.get('f1', 0):.4f}")
        except Exception as e:
            logger.error(f"Error training Random Forest model: {e}")
            results['random_forest'] = {'error': str(e)}
        
        # Train gradient boosting model
        try:
            gb_result = self.ml_model.train(
                training_data, 
                model_type='gradient_boosting',
                feature_selection=True,
                optimize_hyperparams=True
            )
            results['gradient_boosting'] = gb_result
            
            # Update feature importance
            self.feature_importance['gradient_boosting'] = gb_result.get('feature_importance', {})
            
            logger.info(f"Gradient Boosting model trained with F1 score: {gb_result.get('f1', 0):.4f}")
        except Exception as e:
            logger.error(f"Error training Gradient Boosting model: {e}")
            results['gradient_boosting'] = {'error': str(e)}
        
        # Train neural network model
        try:
            nn_result = self.ml_model.train(
                training_data, 
                model_type='neural_network',
                feature_selection=True,
                optimize_hyperparams=True
            )
            results['neural_network'] = nn_result
            
            logger.info(f"Neural Network model trained with F1 score: {nn_result.get('f1', 0):.4f}")
        except Exception as e:
            logger.error(f"Error training Neural Network model: {e}")
            results['neural_network'] = {'error': str(e)}
        
        # Save performance metrics
        self.ml_model.save_performance_metrics()
        
        return {
            'results': results,
            'training_date': datetime.now().isoformat(),
            'symbols_count': len(symbols),
            'data_points': len(training_data)
        }
    
    def prepare_prediction_data(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """
        Prepare data for prediction.
        
        Args:
            symbol: Stock symbol
            days: Number of days of historical data to use
            
        Returns:
            DataFrame with prediction data
        """
        logger.info(f"Preparing prediction data for {symbol}")
        
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            # Get market data
            market_data = self.db_manager.get_market_data(symbol, start_date, end_date)
            
            if market_data.empty:
                logger.warning(f"No market data found for {symbol}")
                return pd.DataFrame()
            
            # Calculate technical indicators
            market_data_with_indicators = calculate_indicators(market_data)
            
            # Get fundamental data
            income_stmt = self.db_manager.get_financial_statement(symbol, 'income', 'annual')
            balance_sheet = self.db_manager.get_financial_statement(symbol, 'balance', 'annual')
            cash_flow = self.db_manager.get_financial_statement(symbol, 'cash_flow', 'annual')
            
            # Calculate fundamental ratios
            ratios = calculate_ratios(income_stmt, balance_sheet, cash_flow)
            
            # Convert ratios to DataFrame
            if ratios:
                ratios_df = pd.DataFrame([ratios])
                ratios_df.index = [market_data.index[-1]]  # Use the last date
                
                # Join market data with ratios
                # We'll forward fill the ratios for all dates
                for col in ratios_df.columns:
                    market_data_with_indicators[col] = ratios_df[col].iloc[0]
            
            # Get enhanced data
            enhanced_data = self.data_collector.collect_enhanced_data(symbol)
            
            # Add enhanced data features
            if enhanced_data:
                # News sentiment
                market_data_with_indicators['news_sentiment'] = enhanced_data.get('news', {}).get('sentiment', 0)
                
                # Social sentiment
                market_data_with_indicators['social_sentiment'] = enhanced_data.get('social', {}).get('sentiment', 0)
                
                # Analyst consensus
                consensus = enhanced_data.get('analyst', {}).get('consensus', 'N/A')
                if consensus != 'N/A':
                    consensus_map = {
                        'Strong Buy': 2,
                        'Buy': 1,
                        'Hold': 0,
                        'Sell': -1,
                        'Strong Sell': -2
                    }
                    market_data_with_indicators['analyst_rating'] = consensus_map.get(consensus, 0)
                else:
                    market_data_with_indicators['analyst_rating'] = 0
                
                # Target price
                target_price = enhanced_data.get('analyst', {}).get('target_price', 0)
                if target_price > 0:
                    market_data_with_indicators['target_price'] = target_price
                    market_data_with_indicators['target_price_ratio'] = target_price / market_data_with_indicators['close']
                
                # Institutional ownership
                market_data_with_indicators['institutional_ownership'] = enhanced_data.get('institutional', {}).get('ownership', 0)
            
            # Add symbol column
            market_data_with_indicators['symbol'] = symbol
            
            logger.info(f"Prepared prediction data for {symbol} with {len(market_data_with_indicators)} rows")
            
            return market_data_with_indicators
            
        except Exception as e:
            logger.error(f"Error preparing prediction data for {symbol}: {e}")
            return pd.DataFrame()
    
    def generate_recommendation(self, symbol: str) -> Dict:
        """
        Generate enhanced recommendation for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with recommendation
        """
        logger.info(f"Generating enhanced recommendation for {symbol}")
        
        try:
            # Get company information
            company = self.db_manager.get_company(symbol)
            
            if not company:
                logger.warning(f"Company {symbol} not found")
                return {'error': f"Company {symbol} not found"}
            
            # Prepare prediction data
            prediction_data = self.prepare_prediction_data(symbol)
            
            if prediction_data.empty:
                logger.warning(f"No prediction data available for {symbol}")
                return {'error': f"No prediction data available for {symbol}"}
            
            # Get base recommendation
            base_recommendation = self.base_engine.generate_recommendation(symbol)
            
            # Generate ML recommendation
            ml_recommendation = self.ml_model.ensemble_predict(
                prediction_data,
                model_types=['random_forest', 'gradient_boosting', 'neural_network'],
                weights=self.model_weights
            )
            
            # Extract the latest ML recommendation
            if ml_recommendation.get('recommendations'):
                latest_ml_rec = ml_recommendation['recommendations'][-1]
            else:
                latest_ml_rec = {}
            
            # Combine recommendations
            # We'll use the ML recommendation as the base and enhance it with the rule-based recommendation
            
            # Determine action
            if latest_ml_rec.get('action') and base_recommendation.get('action'):
                # If both agree, use that action
                if latest_ml_rec['action'] == base_recommendation['action']:
                    action = latest_ml_rec['action']
                # If ML confidence is high, prefer ML
                elif latest_ml_rec.get('confidence', 0) > 75:
                    action = latest_ml_rec['action']
                # If base confidence is high, prefer base
                elif base_recommendation.get('confidence', 0) > 75:
                    action = base_recommendation['action']
                # Otherwise, use ML
                else:
                    action = latest_ml_rec['action']
            elif latest_ml_rec.get('action'):
                action = latest_ml_rec['action']
            elif base_recommendation.get('action'):
                action = base_recommendation['action']
            else:
                action = 'hold'
            
            # Determine confidence
            if latest_ml_rec.get('confidence') and base_recommendation.get('confidence'):
                # If both agree, use the higher confidence
                if latest_ml_rec['action'] == base_recommendation['action']:
                    confidence = max(latest_ml_rec['confidence'], base_recommendation['confidence'])
                # If they disagree, use a weighted average
                else:
                    confidence = (latest_ml_rec['confidence'] * 0.7 + base_recommendation['confidence'] * 0.3)
            elif latest_ml_rec.get('confidence'):
                confidence = latest_ml_rec['confidence']
            elif base_recommendation.get('confidence'):
                confidence = base_recommendation['confidence']
            else:
                confidence = 50
            
            # Determine target price
            if latest_ml_rec.get('target_price') and base_recommendation.get('target_price'):
                # Use weighted average
                target_price = (latest_ml_rec['target_price'] * 0.7 + base_recommendation['target_price'] * 0.3)
            elif latest_ml_rec.get('target_price'):
                target_price = latest_ml_rec['target_price']
            elif base_recommendation.get('target_price'):
                target_price = base_recommendation['target_price']
            else:
                # Use current price as fallback
                target_price = prediction_data['close'].iloc[-1] if not prediction_data.empty else 0
            
            # Determine stop loss
            if latest_ml_rec.get('stop_loss') and base_recommendation.get('stop_loss'):
                # Use weighted average
                stop_loss = (latest_ml_rec['stop_loss'] * 0.7 + base_recommendation['stop_loss'] * 0.3)
            elif latest_ml_rec.get('stop_loss'):
                stop_loss = latest_ml_rec['stop_loss']
            elif base_recommendation.get('stop_loss'):
                stop_loss = base_recommendation['stop_loss']
            else:
                # Use current price as fallback
                current_price = prediction_data['close'].iloc[-1] if not prediction_data.empty else 0
                stop_loss = current_price * 0.95 if action == 'buy' else current_price * 1.05
            
            # Get enhanced data
            enhanced_data = self.data_collector.collect_enhanced_data(symbol)
            
            # Prepare technical signals
            technical_signals = base_recommendation.get('technical_signals', [])
            
            # Add ML-based signals
            if self.feature_importance.get('random_forest'):
                # Get top 5 features
                top_features = list(self.feature_importance['random_forest'].items())[:5]
                for feature, importance in top_features:
                    if feature in prediction_data.columns:
                        value = prediction_data[feature].iloc[-1]
                        if not pd.isna(value):
                            signal = f"{feature.replace('_', ' ').title()}: {value:.2f}"
                            technical_signals.append(signal)
            
            # Prepare fundamental signals
            fundamental_signals = base_recommendation.get('fundamental_signals', [])
            
            # Add enhanced data signals
            if enhanced_data:
                # News sentiment
                news_sentiment = enhanced_data.get('news', {}).get('sentiment', 0)
                if news_sentiment != 0:
                    sentiment_text = "Positive" if news_sentiment > 0 else "Negative"
                    fundamental_signals.append(f"News Sentiment: {sentiment_text} ({news_sentiment:.2f})")
                
                # Social sentiment
                social_sentiment = enhanced_data.get('social', {}).get('sentiment', 0)
                if social_sentiment != 0:
                    sentiment_text = "Positive" if social_sentiment > 0 else "Negative"
                    fundamental_signals.append(f"Social Media Sentiment: {sentiment_text} ({social_sentiment:.2f})")
                
                # Analyst consensus
                consensus = enhanced_data.get('analyst', {}).get('consensus', 'N/A')
                if consensus != 'N/A':
                    fundamental_signals.append(f"Analyst Consensus: {consensus}")
                
                # Target price
                target_price_analyst = enhanced_data.get('analyst', {}).get('target_price', 0)
                if target_price_analyst > 0:
                    current_price = prediction_data['close'].iloc[-1] if not prediction_data.empty else 0
                    if current_price > 0:
                        potential_return = (target_price_analyst / current_price - 1) * 100
                        fundamental_signals.append(f"Analyst Target Price: {target_price_analyst:.2f} ({potential_return:.1f}%)")
            
            # Create enhanced recommendation
            enhanced_recommendation = {
                'symbol': symbol,
                'stock': {
                    'symbol': symbol,
                    'name': company.get('name', ''),
                    'sector': company.get('sector', ''),
                    'industry': company.get('industry', '')
                },
                'action': action,
                'confidence': round(confidence, 2),
                'price': prediction_data['close'].iloc[-1] if not prediction_data.empty else 0,
                'target_price': round(target_price, 2),
                'stop_loss': round(stop_loss, 2),
                'time_frame': base_recommendation.get('time_frame', 'medium'),
                'type': 'enhanced',
                'technical_signals': technical_signals[:5],  # Limit to top 5
                'fundamental_signals': fundamental_signals[:5],  # Limit to top 5
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'expiry_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'notes': "This recommendation is generated using an enhanced algorithm that combines traditional technical and fundamental analysis with machine learning and alternative data sources."
            }
            
            logger.info(f"Generated enhanced recommendation for {symbol}: {action} with {confidence:.2f}% confidence")
            
            return enhanced_recommendation
            
        except Exception as e:
            logger.error(f"Error generating enhanced recommendation for {symbol}: {e}")
            return {'error': str(e)}
    
    def generate_recommendations_batch(self, symbols: List[str]) -> List[Dict]:
        """
        Generate enhanced recommendations for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of recommendations
        """
        logger.info(f"Generating enhanced recommendations for {len(symbols)} symbols")
        
        recommendations = []
        
        for symbol in symbols:
            try:
                recommendation = self.generate_recommendation(symbol)
                if 'error' not in recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Error generating recommendation for {symbol}: {e}")
        
        # Sort recommendations by confidence (highest first)
        recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        logger.info(f"Generated {len(recommendations)} enhanced recommendations")
        
        return recommendations