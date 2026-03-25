"""
Script to train and evaluate machine learning models for stock recommendations.

This script trains machine learning models on historical data and evaluates their performance.
It also compares the performance of the enhanced recommendation engine with the base engine.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import internal modules
from data.storage.database_manager import DatabaseManager
from recommendation.engine import RecommendationEngine
from recommendation.enhanced_engine import EnhancedRecommendationEngine
from analysis.models.ml_recommendation_model import MLRecommendationModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_models(symbols, start_date, end_date, output_dir='results'):
    """
    Train machine learning models and save results.
    
    Args:
        symbols: List of stock symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_dir: Directory to save results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize enhanced recommendation engine
    enhanced_engine = EnhancedRecommendationEngine()
    
    # Train models
    logger.info(f"Training models for {len(symbols)} symbols from {start_date} to {end_date}")
    results = enhanced_engine.train_models(symbols, start_date, end_date)
    
    # Save results
    result_path = os.path.join(output_dir, f"training_results_{datetime.now().strftime('%Y%m%d')}.json")
    with open(result_path, 'w') as f:
        import json
        json.dump(results, f, indent=2)
    
    logger.info(f"Training results saved to {result_path}")
    
    # Plot feature importance
    if enhanced_engine.feature_importance:
        for model_type, importance in enhanced_engine.feature_importance.items():
            if importance:
                # Convert to DataFrame
                importance_df = pd.DataFrame(list(importance.items()), columns=['Feature', 'Importance'])
                importance_df = importance_df.sort_values('Importance', ascending=False).head(20)
                
                # Plot
                plt.figure(figsize=(12, 8))
                sns.barplot(x='Importance', y='Feature', data=importance_df)
                plt.title(f'Feature Importance - {model_type.replace("_", " ").title()}')
                plt.tight_layout()
                
                # Save plot
                plot_path = os.path.join(output_dir, f"feature_importance_{model_type}_{datetime.now().strftime('%Y%m%d')}.png")
                plt.savefig(plot_path)
                plt.close()
                
                logger.info(f"Feature importance plot saved to {plot_path}")

def evaluate_recommendations(symbols, days=60, output_dir='results'):
    """
    Evaluate and compare recommendations from base and enhanced engines.
    
    Args:
        symbols: List of stock symbols
        days: Number of days to evaluate
        output_dir: Directory to save results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize engines
    base_engine = RecommendationEngine()
    enhanced_engine = EnhancedRecommendationEngine()
    
    # Generate recommendations
    logger.info(f"Generating recommendations for {len(symbols)} symbols")
    
    base_recommendations = []
    enhanced_recommendations = []
    
    for symbol in symbols:
        try:
            # Generate base recommendation
            base_rec = base_engine.generate_recommendation(symbol)
            if 'error' not in base_rec:
                base_recommendations.append(base_rec)
            
            # Generate enhanced recommendation
            enhanced_rec = enhanced_engine.generate_recommendation(symbol)
            if 'error' not in enhanced_rec:
                enhanced_recommendations.append(enhanced_rec)
        except Exception as e:
            logger.error(f"Error generating recommendations for {symbol}: {e}")
    
    # Compare recommendations
    comparison = []
    
    for base_rec in base_recommendations:
        symbol = base_rec['symbol']
        
        # Find matching enhanced recommendation
        enhanced_rec = next((rec for rec in enhanced_recommendations if rec['symbol'] == symbol), None)
        
        if enhanced_rec:
            comparison.append({
                'symbol': symbol,
                'base_action': base_rec['action'],
                'enhanced_action': enhanced_rec['action'],
                'base_confidence': base_rec['confidence'],
                'enhanced_confidence': enhanced_rec['confidence'],
                'base_target_price': base_rec['target_price'],
                'enhanced_target_price': enhanced_rec['target_price'],
                'base_stop_loss': base_rec['stop_loss'],
                'enhanced_stop_loss': enhanced_rec['stop_loss'],
                'agreement': base_rec['action'] == enhanced_rec['action']
            })
    
    # Convert to DataFrame
    comparison_df = pd.DataFrame(comparison)
    
    # Calculate agreement rate
    agreement_rate = comparison_df['agreement'].mean() * 100
    
    # Count actions
    base_actions = comparison_df['base_action'].value_counts()
    enhanced_actions = comparison_df['enhanced_action'].value_counts()
    
    # Calculate average confidence
    base_confidence = comparison_df['base_confidence'].mean()
    enhanced_confidence = comparison_df['enhanced_confidence'].mean()
    
    # Save comparison
    comparison_path = os.path.join(output_dir, f"recommendation_comparison_{datetime.now().strftime('%Y%m%d')}.csv")
    comparison_df.to_csv(comparison_path, index=False)
    
    logger.info(f"Recommendation comparison saved to {comparison_path}")
    
    # Print summary
    logger.info(f"Agreement rate: {agreement_rate:.2f}%")
    logger.info(f"Base actions: {dict(base_actions)}")
    logger.info(f"Enhanced actions: {dict(enhanced_actions)}")
    logger.info(f"Base average confidence: {base_confidence:.2f}%")
    logger.info(f"Enhanced average confidence: {enhanced_confidence:.2f}%")
    
    # Plot comparison
    plt.figure(figsize=(12, 8))
    
    # Plot action counts
    plt.subplot(2, 2, 1)
    base_actions.plot(kind='bar', color='blue', alpha=0.7, label='Base')
    enhanced_actions.plot(kind='bar', color='green', alpha=0.7, label='Enhanced')
    plt.title('Action Counts')
    plt.xlabel('Action')
    plt.ylabel('Count')
    plt.legend()
    
    # Plot confidence distribution
    plt.subplot(2, 2, 2)
    sns.kdeplot(comparison_df['base_confidence'], label='Base', color='blue')
    sns.kdeplot(comparison_df['enhanced_confidence'], label='Enhanced', color='green')
    plt.title('Confidence Distribution')
    plt.xlabel('Confidence (%)')
    plt.ylabel('Density')
    plt.legend()
    
    # Plot agreement
    plt.subplot(2, 2, 3)
    agreement_counts = comparison_df['agreement'].value_counts()
    agreement_counts.plot(kind='pie', autopct='%1.1f%%', colors=['green', 'red'])
    plt.title('Agreement Rate')
    plt.ylabel('')
    
    # Plot confidence difference
    plt.subplot(2, 2, 4)
    comparison_df['confidence_diff'] = comparison_df['enhanced_confidence'] - comparison_df['base_confidence']
    sns.histplot(comparison_df['confidence_diff'], kde=True)
    plt.title('Confidence Difference (Enhanced - Base)')
    plt.xlabel('Difference (%)')
    plt.ylabel('Count')
    
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(output_dir, f"recommendation_comparison_{datetime.now().strftime('%Y%m%d')}.png")
    plt.savefig(plot_path)
    plt.close()
    
    logger.info(f"Recommendation comparison plot saved to {plot_path}")

def backtest_recommendations(symbols, start_date, end_date, output_dir='results'):
    """
    Backtest recommendations on historical data.
    
    Args:
        symbols: List of stock symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_dir: Directory to save results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Initialize engines
    base_engine = RecommendationEngine()
    enhanced_engine = EnhancedRecommendationEngine()
    
    # Results
    base_results = []
    enhanced_results = []
    
    # Backtest period
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Backtest every 30 days
    while current_date <= end_date_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        
        logger.info(f"Backtesting for date: {date_str}")
        
        for symbol in symbols:
            try:
                # Get market data
                market_data = db_manager.get_market_data(
                    symbol, 
                    (current_date - timedelta(days=180)).strftime('%Y-%m-%d'),
                    (current_date + timedelta(days=30)).strftime('%Y-%m-%d')
                )
                
                if market_data.empty:
                    logger.warning(f"No market data found for {symbol} on {date_str}")
                    continue
                
                # Get data up to current date
                historical_data = market_data[market_data.index <= date_str]
                
                if historical_data.empty:
                    continue
                
                # Get future data for evaluation
                future_data = market_data[market_data.index > date_str]
                
                if future_data.empty:
                    continue
                
                # Current price
                current_price = historical_data['close'].iloc[-1]
                
                # Future price (30 days later or last available)
                future_price = future_data['close'].iloc[-1]
                
                # Calculate return
                actual_return = (future_price / current_price - 1) * 100
                
                # Generate base recommendation
                base_rec = base_engine.generate_recommendation(symbol, historical_data=historical_data)
                
                if 'error' not in base_rec:
                    # Calculate expected return
                    if base_rec['action'] == 'buy':
                        expected_return = (base_rec['target_price'] / current_price - 1) * 100
                    elif base_rec['action'] == 'sell':
                        expected_return = (current_price / base_rec['target_price'] - 1) * 100
                    else:  # hold
                        expected_return = 0
                    
                    # Determine if recommendation was correct
                    if base_rec['action'] == 'buy':
                        correct = actual_return > 0
                    elif base_rec['action'] == 'sell':
                        correct = actual_return < 0
                    else:  # hold
                        correct = abs(actual_return) < 5
                    
                    base_results.append({
                        'date': date_str,
                        'symbol': symbol,
                        'action': base_rec['action'],
                        'confidence': base_rec['confidence'],
                        'current_price': current_price,
                        'target_price': base_rec['target_price'],
                        'future_price': future_price,
                        'expected_return': expected_return,
                        'actual_return': actual_return,
                        'correct': correct
                    })
                
                # Generate enhanced recommendation
                enhanced_rec = enhanced_engine.generate_recommendation(symbol, historical_data=historical_data)
                
                if 'error' not in enhanced_rec:
                    # Calculate expected return
                    if enhanced_rec['action'] == 'buy':
                        expected_return = (enhanced_rec['target_price'] / current_price - 1) * 100
                    elif enhanced_rec['action'] == 'sell':
                        expected_return = (current_price / enhanced_rec['target_price'] - 1) * 100
                    else:  # hold
                        expected_return = 0
                    
                    # Determine if recommendation was correct
                    if enhanced_rec['action'] == 'buy':
                        correct = actual_return > 0
                    elif enhanced_rec['action'] == 'sell':
                        correct = actual_return < 0
                    else:  # hold
                        correct = abs(actual_return) < 5
                    
                    enhanced_results.append({
                        'date': date_str,
                        'symbol': symbol,
                        'action': enhanced_rec['action'],
                        'confidence': enhanced_rec['confidence'],
                        'current_price': current_price,
                        'target_price': enhanced_rec['target_price'],
                        'future_price': future_price,
                        'expected_return': expected_return,
                        'actual_return': actual_return,
                        'correct': correct
                    })
            
            except Exception as e:
                logger.error(f"Error backtesting for {symbol} on {date_str}: {e}")
        
        # Move to next date
        current_date += timedelta(days=30)
    
    # Convert to DataFrames
    base_df = pd.DataFrame(base_results)
    enhanced_df = pd.DataFrame(enhanced_results)
    
    # Save results
    base_path = os.path.join(output_dir, f"backtest_base_{start_date}_{end_date}.csv")
    enhanced_path = os.path.join(output_dir, f"backtest_enhanced_{start_date}_{end_date}.csv")
    
    base_df.to_csv(base_path, index=False)
    enhanced_df.to_csv(enhanced_path, index=False)
    
    logger.info(f"Base backtest results saved to {base_path}")
    logger.info(f"Enhanced backtest results saved to {enhanced_path}")
    
    # Calculate accuracy
    if not base_df.empty:
        base_accuracy = base_df['correct'].mean() * 100
        logger.info(f"Base recommendation accuracy: {base_accuracy:.2f}%")
    else:
        base_accuracy = 0
    
    if not enhanced_df.empty:
        enhanced_accuracy = enhanced_df['correct'].mean() * 100
        logger.info(f"Enhanced recommendation accuracy: {enhanced_accuracy:.2f}%")
    else:
        enhanced_accuracy = 0
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # Plot accuracy
    plt.subplot(2, 2, 1)
    accuracies = [base_accuracy, enhanced_accuracy]
    plt.bar(['Base', 'Enhanced'], accuracies, color=['blue', 'green'])
    plt.title('Recommendation Accuracy')
    plt.xlabel('Engine')
    plt.ylabel('Accuracy (%)')
    
    # Plot action distribution
    if not base_df.empty and not enhanced_df.empty:
        plt.subplot(2, 2, 2)
        base_actions = base_df['action'].value_counts(normalize=True) * 100
        enhanced_actions = enhanced_df['action'].value_counts(normalize=True) * 100
        
        width = 0.35
        x = np.arange(len(base_actions.index))
        
        plt.bar(x - width/2, base_actions, width, label='Base', color='blue')
        plt.bar(x + width/2, enhanced_actions, width, label='Enhanced', color='green')
        
        plt.title('Action Distribution')
        plt.xlabel('Action')
        plt.ylabel('Percentage (%)')
        plt.xticks(x, base_actions.index)
        plt.legend()
    
    # Plot average returns
    if not base_df.empty and not enhanced_df.empty:
        plt.subplot(2, 2, 3)
        
        base_returns = base_df.groupby('action')['actual_return'].mean()
        enhanced_returns = enhanced_df.groupby('action')['actual_return'].mean()
        
        width = 0.35
        x = np.arange(len(base_returns.index))
        
        plt.bar(x - width/2, base_returns, width, label='Base', color='blue')
        plt.bar(x + width/2, enhanced_returns, width, label='Enhanced', color='green')
        
        plt.title('Average Actual Returns by Action')
        plt.xlabel('Action')
        plt.ylabel('Return (%)')
        plt.xticks(x, base_returns.index)
        plt.legend()
    
    # Plot accuracy by confidence
    if not base_df.empty and not enhanced_df.empty:
        plt.subplot(2, 2, 4)
        
        # Create confidence bins
        bins = [0, 60, 70, 80, 90, 100]
        labels = ['0-60', '60-70', '70-80', '80-90', '90-100']
        
        base_df['confidence_bin'] = pd.cut(base_df['confidence'], bins=bins, labels=labels)
        enhanced_df['confidence_bin'] = pd.cut(enhanced_df['confidence'], bins=bins, labels=labels)
        
        base_accuracy_by_confidence = base_df.groupby('confidence_bin')['correct'].mean() * 100
        enhanced_accuracy_by_confidence = enhanced_df.groupby('confidence_bin')['correct'].mean() * 100
        
        width = 0.35
        x = np.arange(len(base_accuracy_by_confidence.index))
        
        plt.bar(x - width/2, base_accuracy_by_confidence, width, label='Base', color='blue')
        plt.bar(x + width/2, enhanced_accuracy_by_confidence, width, label='Enhanced', color='green')
        
        plt.title('Accuracy by Confidence')
        plt.xlabel('Confidence Range')
        plt.ylabel('Accuracy (%)')
        plt.xticks(x, base_accuracy_by_confidence.index)
        plt.legend()
    
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(output_dir, f"backtest_comparison_{start_date}_{end_date}.png")
    plt.savefig(plot_path)
    plt.close()
    
    logger.info(f"Backtest comparison plot saved to {plot_path}")
    
    # Return accuracy improvement
    return enhanced_accuracy - base_accuracy

def main():
    """
    Main function to run the script.
    """
    # Define symbols to use
    # In a real implementation, you would get this from the database
    symbols = [
        'TASI.2222',  # Aramco
        'TASI.1150',  # Alinma Bank
        'TASI.2350',  # Saudi Kayan
        'TASI.2310',  # SIPCHEM
        'TASI.2380',  # Petro Rabigh
        'TASI.1010',  # RIBL
        'TASI.1050',  # NCB
        'TASI.2001',  # SABIC
        'TASI.4240',  # FIPCO
        'TASI.4003'   # Ceramic
    ]
    
    # Define date ranges
    train_start_date = '2018-01-01'
    train_end_date = '2020-12-31'
    test_start_date = '2021-01-01'
    test_end_date = '2021-12-31'
    
    # Create output directory
    output_dir = 'ml_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Train models
    train_models(symbols, train_start_date, train_end_date, output_dir)
    
    # Evaluate recommendations
    evaluate_recommendations(symbols, 60, output_dir)
    
    # Backtest recommendations
    accuracy_improvement = backtest_recommendations(symbols, test_start_date, test_end_date, output_dir)
    
    logger.info(f"Accuracy improvement with enhanced engine: {accuracy_improvement:.2f}%")

if __name__ == '__main__':
    main()