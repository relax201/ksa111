"""
Recommendation Models for Saudi Stock Market (Tasi)

This module provides machine learning models for generating
stock recommendations based on historical data and patterns.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
import joblib
import os
from datetime import datetime

class RecommendationModel:
    """
    Base class for recommendation models using machine learning.
    """
    
    def __init__(self, model_type='random_forest', model_params=None):
        """
        Initialize the recommendation model.
        
        Args:
            model_type (str): Type of model to use ('random_forest', 'gradient_boosting', 
                             'logistic_regression', 'svm')
            model_params (dict): Parameters for the model
        """
        self.model_type = model_type
        self.model_params = model_params or {}
        self.model = self._create_model()
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.trained = False
        
    def _create_model(self):
        """
        Create the machine learning model based on the specified type.
        
        Returns:
            object: Scikit-learn model instance
        """
        if self.model_type == 'random_forest':
            params = {
                'n_estimators': self.model_params.get('n_estimators', 100),
                'max_depth': self.model_params.get('max_depth', None),
                'min_samples_split': self.model_params.get('min_samples_split', 2),
                'random_state': self.model_params.get('random_state', 42)
            }
            return RandomForestClassifier(**params)
            
        elif self.model_type == 'gradient_boosting':
            params = {
                'n_estimators': self.model_params.get('n_estimators', 100),
                'learning_rate': self.model_params.get('learning_rate', 0.1),
                'max_depth': self.model_params.get('max_depth', 3),
                'random_state': self.model_params.get('random_state', 42)
            }
            return GradientBoostingClassifier(**params)
            
        elif self.model_type == 'logistic_regression':
            params = {
                'C': self.model_params.get('C', 1.0),
                'penalty': self.model_params.get('penalty', 'l2'),
                'solver': self.model_params.get('solver', 'lbfgs'),
                'random_state': self.model_params.get('random_state', 42)
            }
            return LogisticRegression(**params)
            
        elif self.model_type == 'svm':
            params = {
                'C': self.model_params.get('C', 1.0),
                'kernel': self.model_params.get('kernel', 'rbf'),
                'gamma': self.model_params.get('gamma', 'scale'),
                'probability': True,
                'random_state': self.model_params.get('random_state', 42)
            }
            return SVC(**params)
            
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def prepare_data(self, X, y, test_size=0.2):
        """
        Prepare data for training and testing.
        
        Args:
            X (DataFrame): Features
            y (Series): Target variable
            test_size (float): Proportion of data to use for testing
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X, y, optimize=False):
        """
        Train the model on the provided data.
        
        Args:
            X (DataFrame): Features
            y (Series): Target variable (1 for buy, 0 for hold, -1 for sell)
            optimize (bool): Whether to perform hyperparameter optimization
            
        Returns:
            dict: Training results and metrics
        """
        X_train, X_test, y_train, y_test = self.prepare_data(X, y)
        
        if optimize:
            self.model = self._optimize_hyperparameters(X_train, y_train)
        
        # Train the model
        self.model.fit(X_train, y_train)
        self.trained = True
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted')
        }
        
        # Store feature importance if available
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = dict(zip(X.columns, self.model.feature_importances_))
        
        return {
            'model_type': self.model_type,
            'training_date': datetime.now().strftime('%Y-%m-%d'),
            'metrics': metrics,
            'feature_importance': self.feature_importance
        }
    
    def _optimize_hyperparameters(self, X_train, y_train):
        """
        Optimize model hyperparameters using grid search.
        
        Args:
            X_train (array): Training features
            y_train (array): Training targets
            
        Returns:
            object: Optimized model
        """
        if self.model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10]
            }
        elif self.model_type == 'gradient_boosting':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        elif self.model_type == 'logistic_regression':
            param_grid = {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        elif self.model_type == 'svm':
            param_grid = {
                'C': [0.1, 1.0, 10.0],
                'kernel': ['linear', 'rbf', 'poly'],
                'gamma': ['scale', 'auto', 0.1, 1.0]
            }
        else:
            return self.model
        
        grid_search = GridSearchCV(
            self._create_model(), 
            param_grid, 
            cv=5, 
            scoring='f1_weighted',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        return grid_search.best_estimator_
    
    def predict(self, X):
        """
        Generate predictions for new data.
        
        Args:
            X (DataFrame): Features for prediction
            
        Returns:
            array: Predicted classes
        """
        if not self.trained:
            raise ValueError("Model has not been trained yet")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X):
        """
        Generate probability predictions for new data.
        
        Args:
            X (DataFrame): Features for prediction
            
        Returns:
            array: Predicted probabilities for each class
        """
        if not self.trained:
            raise ValueError("Model has not been trained yet")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get probability predictions
        return self.model.predict_proba(X_scaled)
    
    def save_model(self, path):
        """
        Save the trained model to disk.
        
        Args:
            path (str): Path to save the model
            
        Returns:
            str: Path where model was saved
        """
        if not self.trained:
            raise ValueError("Cannot save untrained model")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and scaler
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_importance': self.feature_importance,
            'trained_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        joblib.dump(model_data, path)
        return path
    
    @classmethod
    def load_model(cls, path):
        """
        Load a trained model from disk.
        
        Args:
            path (str): Path to the saved model
            
        Returns:
            RecommendationModel: Loaded model instance
        """
        model_data = joblib.load(path)
        
        # Create instance
        instance = cls(model_type=model_data['model_type'])
        
        # Load model components
        instance.model = model_data['model']
        instance.scaler = model_data['scaler']
        instance.feature_importance = model_data['feature_importance']
        instance.trained = True
        
        return instance


class EnsembleRecommendationModel:
    """
    Ensemble model that combines multiple recommendation models.
    """
    
    def __init__(self, models=None, weights=None):
        """
        Initialize the ensemble model.
        
        Args:
            models (list): List of RecommendationModel instances
            weights (list): Weights for each model in the ensemble
        """
        self.models = models or []
        self.weights = weights or [1.0] * len(self.models)
        
        # Normalize weights
        if sum(self.weights) != 1.0:
            self.weights = [w / sum(self.weights) for w in self.weights]
    
    def add_model(self, model, weight=1.0):
        """
        Add a model to the ensemble.
        
        Args:
            model (RecommendationModel): Model to add
            weight (float): Weight for the model
        """
        self.models.append(model)
        self.weights.append(weight)
        
        # Normalize weights
        self.weights = [w / sum(self.weights) for w in self.weights]
    
    def predict(self, X):
        """
        Generate predictions using the ensemble.
        
        Args:
            X (DataFrame): Features for prediction
            
        Returns:
            array: Predicted classes
        """
        if not self.models:
            raise ValueError("No models in the ensemble")
        
        # Get probability predictions from each model
        probas = [model.predict_proba(X) for model in self.models]
        
        # Weight and combine probabilities
        weighted_probas = np.zeros_like(probas[0])
        for i, proba in enumerate(probas):
            weighted_probas += proba * self.weights[i]
        
        # Get class with highest probability
        return np.argmax(weighted_probas, axis=1) - 1  # Convert to -1, 0, 1
    
    def predict_proba(self, X):
        """
        Generate probability predictions using the ensemble.
        
        Args:
            X (DataFrame): Features for prediction
            
        Returns:
            array: Predicted probabilities for each class
        """
        if not self.models:
            raise ValueError("No models in the ensemble")
        
        # Get probability predictions from each model
        probas = [model.predict_proba(X) for model in self.models]
        
        # Weight and combine probabilities
        weighted_probas = np.zeros_like(probas[0])
        for i, proba in enumerate(probas):
            weighted_probas += proba * self.weights[i]
        
        return weighted_probas
    
    def save_ensemble(self, directory):
        """
        Save all models in the ensemble.
        
        Args:
            directory (str): Directory to save models
            
        Returns:
            str: Path where ensemble configuration was saved
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save each model
        model_paths = []
        for i, model in enumerate(self.models):
            model_path = os.path.join(directory, f"model_{i}.joblib")
            model.save_model(model_path)
            model_paths.append(model_path)
        
        # Save ensemble configuration
        config = {
            'model_paths': model_paths,
            'weights': self.weights,
            'saved_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        config_path = os.path.join(directory, "ensemble_config.joblib")
        joblib.dump(config, config_path)
        
        return config_path
    
    @classmethod
    def load_ensemble(cls, config_path):
        """
        Load an ensemble from a saved configuration.
        
        Args:
            config_path (str): Path to the ensemble configuration
            
        Returns:
            EnsembleRecommendationModel: Loaded ensemble instance
        """
        config = joblib.load(config_path)
        
        # Load each model
        models = []
        for model_path in config['model_paths']:
            model = RecommendationModel.load_model(model_path)
            models.append(model)
        
        # Create ensemble
        return cls(models=models, weights=config['weights'])