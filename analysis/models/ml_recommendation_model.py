"""
Machine Learning Model for Stock Recommendations

This module implements machine learning models to improve the accuracy of stock recommendations
by analyzing historical patterns and combining multiple data sources.
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any

# ML libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# Feature engineering
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif

# For saving/loading models
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLRecommendationModel:
    """
    Machine Learning model for generating stock recommendations.
    
    This class implements various ML algorithms to predict stock price movements
    and generate buy/sell/hold recommendations with confidence scores.
    """
    
    def __init__(self, model_dir: str = 'models'):
        """
        Initialize the ML recommendation model.
        
        Args:
            model_dir: Directory to save/load trained models
        """
        self.model_dir = model_dir
        self.models = {}
        self.feature_importances = {}
        self.performance_metrics = {}
        self.scaler = None
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Default model parameters
        self.default_params = {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 10,
                'min_samples_leaf': 5,
                'random_state': 42
            },
            'gradient_boosting': {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 5,
                'random_state': 42
            },
            'logistic_regression': {
                'C': 1.0,
                'max_iter': 1000,
                'random_state': 42
            },
            'svm': {
                'C': 1.0,
                'kernel': 'rbf',
                'probability': True,
                'random_state': 42
            },
            'neural_network': {
                'hidden_layer_sizes': (100, 50),
                'activation': 'relu',
                'solver': 'adam',
                'alpha': 0.0001,
                'max_iter': 500,
                'random_state': 42
            }
        }
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for the ML model.
        
        Args:
            data: DataFrame containing raw data
            
        Returns:
            DataFrame with engineered features
        """
        # Make a copy to avoid modifying the original data
        df = data.copy()
        
        # Handle missing values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Basic feature engineering
        
        # 1. Technical indicators (assuming these columns exist)
        # If they don't exist, they will be created with NaN values
        technical_cols = [
            'rsi_14', 'macd', 'macd_signal', 'macd_hist', 
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
            'atr_14', 'adx_14', 'cci_14', 'stoch_k', 'stoch_d',
            'williams_r', 'obv'
        ]
        
        # 2. Price and volume features
        if 'close' in df.columns and 'open' in df.columns:
            # Daily returns
            df['daily_return'] = df['close'].pct_change()
            
            # Price change percentage
            df['price_change_pct'] = (df['close'] - df['open']) / df['open'] * 100
            
            # Volatility (rolling standard deviation of returns)
            df['volatility_5d'] = df['daily_return'].rolling(window=5).std()
            df['volatility_20d'] = df['daily_return'].rolling(window=20).std()
            
            # Momentum indicators
            df['momentum_5d'] = df['close'].pct_change(periods=5)
            df['momentum_20d'] = df['close'].pct_change(periods=20)
            
            # Price relative to moving averages
            if 'sma_20' in df.columns:
                df['price_to_sma20'] = df['close'] / df['sma_20']
            if 'sma_50' in df.columns:
                df['price_to_sma50'] = df['close'] / df['sma_50']
            if 'sma_200' in df.columns:
                df['price_to_sma200'] = df['close'] / df['sma_200']
        
        # 3. Volume features
        if 'volume' in df.columns:
            # Volume change
            df['volume_change'] = df['volume'].pct_change()
            
            # Relative volume (compared to moving average)
            df['relative_volume_5d'] = df['volume'] / df['volume'].rolling(window=5).mean()
            df['relative_volume_20d'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # 4. Fundamental features (if available)
        fundamental_cols = [
            'pe_ratio', 'pb_ratio', 'ps_ratio', 'dividend_yield',
            'roe', 'roa', 'debt_to_equity', 'current_ratio',
            'quick_ratio', 'profit_margin', 'operating_margin',
            'revenue_growth', 'earnings_growth'
        ]
        
        # 5. Market sentiment features (if available)
        sentiment_cols = [
            'news_sentiment', 'social_sentiment', 'analyst_rating',
            'institutional_ownership', 'short_interest'
        ]
        
        # 6. Sector and market features (if available)
        market_cols = [
            'sector_performance', 'market_return', 'market_volatility',
            'interest_rate', 'oil_price', 'market_pe'
        ]
        
        # Create target variable (if not already present)
        # This is just a placeholder - in a real implementation, you would define
        # your target variable based on your specific prediction goal
        if 'target' not in df.columns and 'close' in df.columns:
            # Example: Predict if price will increase by 2% or more in the next 5 days
            df['future_return_5d'] = df['close'].shift(-5) / df['close'] - 1
            df['target'] = (df['future_return_5d'] > 0.02).astype(int)
        
        # Drop rows with NaN in target
        df = df.dropna(subset=['target'])
        
        # Log feature creation
        logger.info(f"Created features dataframe with shape {df.shape}")
        
        return df
    
    def _get_model(self, model_type: str, params: Optional[Dict] = None) -> Any:
        """
        Get a model instance based on the specified type and parameters.
        
        Args:
            model_type: Type of model ('random_forest', 'gradient_boosting', etc.)
            params: Model parameters (if None, use default parameters)
            
        Returns:
            Model instance
        """
        if params is None:
            params = self.default_params.get(model_type, {})
        
        if model_type == 'random_forest':
            return RandomForestClassifier(**params)
        elif model_type == 'gradient_boosting':
            return GradientBoostingClassifier(**params)
        elif model_type == 'logistic_regression':
            return LogisticRegression(**params)
        elif model_type == 'svm':
            return SVC(**params)
        elif model_type == 'neural_network':
            return MLPClassifier(**params)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def train(self, data: pd.DataFrame, model_type: str = 'random_forest', 
             params: Optional[Dict] = None, feature_selection: bool = True,
             cv: int = 5, optimize_hyperparams: bool = False) -> Dict:
        """
        Train a machine learning model for stock recommendations.
        
        Args:
            data: DataFrame containing historical data
            model_type: Type of model to train
            params: Model parameters (if None, use default parameters)
            feature_selection: Whether to perform feature selection
            cv: Number of cross-validation folds
            optimize_hyperparams: Whether to optimize hyperparameters using GridSearchCV
            
        Returns:
            Dictionary with training results
        """
        # Prepare features
        df = self._prepare_features(data)
        
        # Split features and target
        X = df.drop(['target'], axis=1)
        y = df['target']
        
        # Remove non-numeric columns
        X = X.select_dtypes(include=['number'])
        
        # Fill missing values
        X = X.fillna(X.mean())
        
        # Get column names
        feature_names = X.columns.tolist()
        
        # Split data into training and testing sets
        # Use TimeSeriesSplit for time series data
        tscv = TimeSeriesSplit(n_splits=cv)
        
        # For simplicity, we'll use a single train-test split here
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save the scaler for future predictions
        self.scaler = scaler
        
        # Feature selection (optional)
        if feature_selection and X_train.shape[1] > 10:
            # Select top k features
            k = min(20, X_train.shape[1])
            selector = SelectKBest(f_classif, k=k)
            X_train_scaled = selector.fit_transform(X_train_scaled, y_train)
            X_test_scaled = selector.transform(X_test_scaled)
            
            # Get selected feature names
            selected_indices = selector.get_support(indices=True)
            selected_features = [feature_names[i] for i in selected_indices]
            logger.info(f"Selected {len(selected_features)} features: {selected_features}")
        else:
            selected_features = feature_names
        
        # Get model
        if optimize_hyperparams:
            # Define parameter grid for grid search
            param_grid = self._get_param_grid(model_type)
            
            # Create base model
            base_model = self._get_model(model_type)
            
            # Create grid search
            model = GridSearchCV(
                base_model, param_grid, cv=tscv, scoring='f1',
                n_jobs=-1, verbose=1
            )
            
            # Fit model
            model.fit(X_train_scaled, y_train)
            
            # Get best parameters
            best_params = model.best_params_
            logger.info(f"Best parameters: {best_params}")
            
            # Use best model
            best_model = model.best_estimator_
        else:
            # Use model with specified or default parameters
            best_model = self._get_model(model_type, params)
            
            # Fit model
            best_model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = best_model.predict(X_test_scaled)
        y_prob = best_model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate performance metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # Log performance metrics
        logger.info(f"Model: {model_type}")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1 Score: {f1:.4f}")
        logger.info(f"Confusion Matrix:\n{conf_matrix}")
        
        # Get feature importances (if available)
        if hasattr(best_model, 'feature_importances_'):
            importances = best_model.feature_importances_
            feature_importance = dict(zip(selected_features, importances))
            sorted_importance = {k: v for k, v in sorted(
                feature_importance.items(), key=lambda item: item[1], reverse=True
            )}
            logger.info(f"Feature Importances: {sorted_importance}")
            self.feature_importances[model_type] = sorted_importance
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
        joblib.dump(best_model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, f"{model_type}_scaler.joblib")
        joblib.dump(scaler, scaler_path)
        
        # Store model and performance metrics
        self.models[model_type] = best_model
        self.performance_metrics[model_type] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': conf_matrix.tolist(),
            'training_date': datetime.now().isoformat()
        }
        
        # Return results
        return {
            'model_type': model_type,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': conf_matrix.tolist(),
            'feature_importance': self.feature_importances.get(model_type, {}),
            'selected_features': selected_features
        }
    
    def _get_param_grid(self, model_type: str) -> Dict:
        """
        Get parameter grid for hyperparameter optimization.
        
        Args:
            model_type: Type of model
            
        Returns:
            Parameter grid for GridSearchCV
        """
        if model_type == 'random_forest':
            return {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif model_type == 'gradient_boosting':
            return {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        elif model_type == 'logistic_regression':
            return {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        elif model_type == 'svm':
            return {
                'C': [0.1, 1.0, 10.0],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto', 0.1, 0.01]
            }
        elif model_type == 'neural_network':
            return {
                'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
                'activation': ['relu', 'tanh'],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate': ['constant', 'adaptive']
            }
        else:
            return {}
    
    def predict(self, data: pd.DataFrame, model_type: str = 'random_forest') -> Dict:
        """
        Generate predictions using the trained model.
        
        Args:
            data: DataFrame containing features
            model_type: Type of model to use for prediction
            
        Returns:
            Dictionary with predictions
        """
        # Check if model exists
        if model_type not in self.models:
            # Try to load model
            model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
            scaler_path = os.path.join(self.model_dir, f"{model_type}_scaler.joblib")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[model_type] = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
            else:
                raise ValueError(f"Model {model_type} not found. Train the model first.")
        
        # Prepare features
        df = self._prepare_features(data)
        
        # Remove target column if it exists
        if 'target' in df.columns:
            df = df.drop(['target'], axis=1)
        
        # Select only numeric columns
        X = df.select_dtypes(include=['number'])
        
        # Fill missing values
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        model = self.models[model_type]
        y_pred = model.predict(X_scaled)
        y_prob = model.predict_proba(X_scaled)
        
        # Map predictions to recommendations
        recommendations = []
        for i, (pred, probs) in enumerate(zip(y_pred, y_prob)):
            # Get confidence score
            confidence = probs[1] if pred == 1 else probs[0]
            
            # Map to recommendation
            if pred == 1:
                action = 'buy'
            else:
                # If confidence is low, recommend hold
                if confidence < 0.6:
                    action = 'hold'
                else:
                    action = 'sell'
            
            # Calculate target price and stop loss (simplified example)
            current_price = df.iloc[i]['close'] if 'close' in df.columns else None
            
            if current_price is not None:
                if action == 'buy':
                    # Target price: current price + (confidence * 10%)
                    target_price = current_price * (1 + confidence * 0.1)
                    # Stop loss: current price - (5%)
                    stop_loss = current_price * 0.95
                elif action == 'sell':
                    # Target price: current price - (confidence * 10%)
                    target_price = current_price * (1 - confidence * 0.1)
                    # Stop loss: current price + (5%)
                    stop_loss = current_price * 1.05
                else:  # hold
                    target_price = current_price * 1.05
                    stop_loss = current_price * 0.95
            else:
                target_price = None
                stop_loss = None
            
            # Create recommendation
            recommendation = {
                'action': action,
                'confidence': round(confidence * 100, 2),
                'target_price': round(target_price, 2) if target_price is not None else None,
                'stop_loss': round(stop_loss, 2) if stop_loss is not None else None,
                'prediction_date': datetime.now().isoformat(),
                'model_type': model_type
            }
            
            recommendations.append(recommendation)
        
        return {
            'recommendations': recommendations,
            'model_type': model_type,
            'prediction_date': datetime.now().isoformat()
        }
    
    def evaluate_models(self, data: pd.DataFrame, model_types: List[str] = None) -> Dict:
        """
        Evaluate multiple models on the same dataset.
        
        Args:
            data: DataFrame containing historical data
            model_types: List of model types to evaluate (if None, evaluate all supported models)
            
        Returns:
            Dictionary with evaluation results
        """
        if model_types is None:
            model_types = ['random_forest', 'gradient_boosting', 'logistic_regression', 'svm', 'neural_network']
        
        results = {}
        
        for model_type in model_types:
            logger.info(f"Evaluating model: {model_type}")
            result = self.train(data, model_type=model_type)
            results[model_type] = result
        
        # Find best model
        best_model = max(results.items(), key=lambda x: x[1]['f1'])
        logger.info(f"Best model: {best_model[0]} with F1 score: {best_model[1]['f1']:.4f}")
        
        return {
            'model_results': results,
            'best_model': best_model[0],
            'evaluation_date': datetime.now().isoformat()
        }
    
    def ensemble_predict(self, data: pd.DataFrame, model_types: List[str] = None,
                       weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Generate predictions using an ensemble of models.
        
        Args:
            data: DataFrame containing features
            model_types: List of model types to use (if None, use all available models)
            weights: Dictionary mapping model types to weights (if None, use equal weights)
            
        Returns:
            Dictionary with ensemble predictions
        """
        if model_types is None:
            model_types = list(self.models.keys())
            
            # If no models are loaded, try to load default models
            if not model_types:
                model_types = ['random_forest', 'gradient_boosting']
                for model_type in model_types:
                    model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
                    scaler_path = os.path.join(self.model_dir, f"{model_type}_scaler.joblib")
                    
                    if os.path.exists(model_path) and os.path.exists(scaler_path):
                        self.models[model_type] = joblib.load(model_path)
                        self.scaler = joblib.load(scaler_path)
                    else:
                        logger.warning(f"Model {model_type} not found. Skipping.")
                        model_types.remove(model_type)
        
        # Check if any models are available
        if not model_types:
            raise ValueError("No models available for prediction. Train models first.")
        
        # Set default weights if not provided
        if weights is None:
            weights = {model_type: 1.0 / len(model_types) for model_type in model_types}
        
        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}
        
        # Get predictions from each model
        all_predictions = {}
        for model_type in model_types:
            try:
                predictions = self.predict(data, model_type=model_type)
                all_predictions[model_type] = predictions['recommendations']
            except Exception as e:
                logger.error(f"Error getting predictions from {model_type}: {e}")
        
        # Combine predictions
        ensemble_recommendations = []
        
        # Assuming each model makes predictions for the same data points in the same order
        if all_predictions:
            num_samples = len(next(iter(all_predictions.values())))
            
            for i in range(num_samples):
                # Collect predictions from all models for this sample
                actions = []
                confidences = []
                target_prices = []
                stop_losses = []
                
                for model_type, predictions in all_predictions.items():
                    if i < len(predictions):
                        pred = predictions[i]
                        actions.append(pred['action'])
                        confidences.append(pred['confidence'] * weights[model_type])
                        
                        if pred['target_price'] is not None:
                            target_prices.append(pred['target_price'])
                        
                        if pred['stop_loss'] is not None:
                            stop_losses.append(pred['stop_loss'])
                
                # Determine ensemble action (majority vote)
                action_counts = {}
                for action in actions:
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                ensemble_action = max(action_counts.items(), key=lambda x: x[1])[0]
                
                # Calculate ensemble confidence (weighted average)
                ensemble_confidence = sum(confidences)
                
                # Calculate ensemble target price and stop loss (average)
                ensemble_target_price = sum(target_prices) / len(target_prices) if target_prices else None
                ensemble_stop_loss = sum(stop_losses) / len(stop_losses) if stop_losses else None
                
                # Create ensemble recommendation
                ensemble_recommendation = {
                    'action': ensemble_action,
                    'confidence': round(ensemble_confidence, 2),
                    'target_price': round(ensemble_target_price, 2) if ensemble_target_price is not None else None,
                    'stop_loss': round(ensemble_stop_loss, 2) if ensemble_stop_loss is not None else None,
                    'prediction_date': datetime.now().isoformat(),
                    'model_type': 'ensemble',
                    'models_used': list(all_predictions.keys())
                }
                
                ensemble_recommendations.append(ensemble_recommendation)
        
        return {
            'recommendations': ensemble_recommendations,
            'model_type': 'ensemble',
            'models_used': list(all_predictions.keys()),
            'weights': weights,
            'prediction_date': datetime.now().isoformat()
        }
    
    def save_performance_metrics(self, file_path: str = None) -> None:
        """
        Save performance metrics to a file.
        
        Args:
            file_path: Path to save the metrics (if None, use default path)
        """
        if file_path is None:
            file_path = os.path.join(self.model_dir, 'performance_metrics.joblib')
        
        joblib.dump(self.performance_metrics, file_path)
        logger.info(f"Performance metrics saved to {file_path}")
    
    def load_performance_metrics(self, file_path: str = None) -> Dict:
        """
        Load performance metrics from a file.
        
        Args:
            file_path: Path to load the metrics from (if None, use default path)
            
        Returns:
            Dictionary with performance metrics
        """
        if file_path is None:
            file_path = os.path.join(self.model_dir, 'performance_metrics.joblib')
        
        if os.path.exists(file_path):
            self.performance_metrics = joblib.load(file_path)
            logger.info(f"Performance metrics loaded from {file_path}")
            return self.performance_metrics
        else:
            logger.warning(f"Performance metrics file not found: {file_path}")
            return {}