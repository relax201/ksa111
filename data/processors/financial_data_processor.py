"""
Financial Data Processor for Saudi Stock Market (Tadawul)

This module provides functionality to process and normalize financial data
for Saudi companies, preparing it for analysis.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    """
    A class for processing and normalizing financial data for Saudi companies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the financial data processor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict: Configuration dictionary
        """
        default_config = {
            'output_dir': './processed_data',
            'normalization': {
                'income_statement': {
                    'normalize_by': 'revenue',
                    'exclude': ['eps', 'shares_outstanding']
                },
                'balance_sheet': {
                    'normalize_by': 'total_assets',
                    'exclude': ['shares_outstanding']
                }
            },
            'standardization': {
                'method': 'z-score',  # 'z-score', 'min-max', or 'robust'
                'sector_based': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge user config with default config
                    for key, value in user_config.items():
                        if key in default_config and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        return default_config
    
    def normalize_financial_statements(self, financial_data: Dict) -> Dict:
        """
        Normalize financial statements by converting to common size statements.
        
        Args:
            financial_data: Financial statements data
            
        Returns:
            Dict: Normalized financial statements
        """
        logger.info("Normalizing financial statements")
        
        normalized_data = {}
        
        # Process income statement
        if 'income_statement' in financial_data:
            income_stmt = financial_data['income_statement']
            normalized_income = self._normalize_statement(
                income_stmt, 
                self.config['normalization']['income_statement']['normalize_by'],
                self.config['normalization']['income_statement']['exclude']
            )
            normalized_data['income_statement'] = normalized_income
        
        # Process balance sheet
        if 'balance_sheet' in financial_data:
            balance_sheet = financial_data['balance_sheet']
            normalized_balance = self._normalize_statement(
                balance_sheet, 
                self.config['normalization']['balance_sheet']['normalize_by'],
                self.config['normalization']['balance_sheet']['exclude']
            )
            normalized_data['balance_sheet'] = normalized_balance
        
        # Copy other data as is
        for key, value in financial_data.items():
            if key not in normalized_data:
                normalized_data[key] = value
        
        return normalized_data
    
    def _normalize_statement(self, statement: Dict, normalize_by: str, exclude: List[str]) -> Dict:
        """
        Normalize a financial statement by a specific field.
        
        Args:
            statement: Financial statement data
            normalize_by: Field to normalize by
            exclude: Fields to exclude from normalization
            
        Returns:
            Dict: Normalized statement
        """
        normalized = statement.copy()
        
        # Extract data
        data = statement.get('data', [])
        normalized_data = []
        
        for period in data:
            normalized_period = period.copy()
            
            # Get normalization base value
            base_value = period.get(normalize_by, 1)
            
            if base_value != 0:
                # Normalize each field
                for field, value in period.items():
                    if field not in exclude and field != normalize_by and isinstance(value, (int, float)):
                        normalized_period[f"{field}_normalized"] = value / base_value
            
            normalized_data.append(normalized_period)
        
        normalized['data'] = normalized_data
        normalized['normalization_base'] = normalize_by
        
        return normalized
    
    def calculate_growth_rates(self, financial_data: Dict) -> Dict:
        """
        Calculate year-over-year growth rates for financial data.
        
        Args:
            financial_data: Financial statements data
            
        Returns:
            Dict: Financial data with growth rates
        """
        logger.info("Calculating growth rates")
        
        data_with_growth = financial_data.copy()
        
        # Process income statement
        if 'income_statement' in financial_data:
            income_stmt = financial_data['income_statement']
            data_with_growth['income_statement'] = self._calculate_statement_growth(income_stmt)
        
        # Process balance sheet
        if 'balance_sheet' in financial_data:
            balance_sheet = financial_data['balance_sheet']
            data_with_growth['balance_sheet'] = self._calculate_statement_growth(balance_sheet)
        
        # Process cash flow
        if 'cash_flow' in financial_data:
            cash_flow = financial_data['cash_flow']
            data_with_growth['cash_flow'] = self._calculate_statement_growth(cash_flow)
        
        return data_with_growth
    
    def _calculate_statement_growth(self, statement: Dict) -> Dict:
        """
        Calculate growth rates for a financial statement.
        
        Args:
            statement: Financial statement data
            
        Returns:
            Dict: Statement with growth rates
        """
        statement_with_growth = statement.copy()
        
        # Extract data
        data = statement.get('data', [])
        
        if len(data) < 2:
            # Not enough data to calculate growth
            statement_with_growth['data'] = data
            return statement_with_growth
        
        # Sort data by date if available
        if 'date' in data[0]:
            data = sorted(data, key=lambda x: x['date'])
        
        data_with_growth = []
        
        for i in range(len(data)):
            period = data[i].copy()
            
            if i > 0:
                prev_period = data[i-1]
                
                # Calculate growth for each field
                for field, value in period.items():
                    if isinstance(value, (int, float)) and field in prev_period:
                        prev_value = prev_period[field]
                        
                        if prev_value != 0:
                            growth = (value - prev_value) / abs(prev_value)
                            period[f"{field}_growth"] = growth
                        else:
                            # Can't calculate growth if previous value is zero
                            period[f"{field}_growth"] = None
            
            data_with_growth.append(period)
        
        statement_with_growth['data'] = data_with_growth
        
        return statement_with_growth
    
    def calculate_ttm_values(self, financial_data: Dict) -> Dict:
        """
        Calculate trailing twelve months (TTM) values from quarterly data.
        
        Args:
            financial_data: Financial statements data
            
        Returns:
            Dict: Financial data with TTM values
        """
        logger.info("Calculating TTM values")
        
        data_with_ttm = financial_data.copy()
        
        # Process quarterly income statement
        if 'quarterly_income' in financial_data:
            quarterly_income = financial_data['quarterly_income']
            ttm_income = self._calculate_ttm(quarterly_income)
            data_with_ttm['ttm_income'] = ttm_income
        
        return data_with_ttm
    
    def _calculate_ttm(self, quarterly_data: Dict) -> Dict:
        """
        Calculate TTM values from quarterly data.
        
        Args:
            quarterly_data: Quarterly financial data
            
        Returns:
            Dict: TTM data
        """
        ttm_data = quarterly_data.copy()
        
        # Extract data
        data = quarterly_data.get('data', [])
        
        if len(data) < 4:
            # Not enough data to calculate TTM
            ttm_data['data'] = []
            ttm_data['note'] = "Insufficient data for TTM calculation (need at least 4 quarters)"
            return ttm_data
        
        # Sort data by date if available
        if 'date' in data[0]:
            data = sorted(data, key=lambda x: x['date'])
        
        ttm_periods = []
        
        # Calculate TTM for each set of 4 consecutive quarters
        for i in range(len(data) - 3):
            ttm_period = {
                'end_date': data[i+3].get('date', f"Q{i+4}"),
                'period': 'TTM'
            }
            
            # Sum values for the last 4 quarters
            for field in data[i]:
                if isinstance(data[i][field], (int, float)):
                    ttm_period[field] = sum(data[j].get(field, 0) for j in range(i, i+4))
            
            ttm_periods.append(ttm_period)
        
        ttm_data['data'] = ttm_periods
        
        return ttm_data
    
    def standardize_data(self, financial_data: Dict, sector_data: Optional[Dict] = None) -> Dict:
        """
        Standardize financial data for comparison.
        
        Args:
            financial_data: Financial statements data
            sector_data: Sector data for sector-based standardization
            
        Returns:
            Dict: Standardized financial data
        """
        logger.info("Standardizing financial data")
        
        standardized_data = financial_data.copy()
        
        # Determine standardization method
        method = self.config['standardization']['method']
        sector_based = self.config['standardization']['sector_based']
        
        if sector_based and not sector_data:
            logger.warning("Sector-based standardization requested but no sector data provided")
            sector_based = False
        
        # Process ratios
        if 'ratios' in financial_data:
            ratios = financial_data['ratios']
            
            if sector_based:
                sector_ratios = sector_data.get('ratios', {})
                standardized_ratios = self._standardize_with_sector(ratios, sector_ratios, method)
            else:
                standardized_ratios = self._standardize_data(ratios, method)
            
            standardized_data['standardized_ratios'] = standardized_ratios
        
        return standardized_data
    
    def _standardize_with_sector(self, data: Dict, sector_data: Dict, method: str) -> Dict:
        """
        Standardize data using sector averages.
        
        Args:
            data: Data to standardize
            sector_data: Sector data for comparison
            method: Standardization method
            
        Returns:
            Dict: Standardized data
        """
        standardized = {}
        
        for key, value in data.items():
            if key in sector_data and isinstance(value, (int, float)) and isinstance(sector_data[key], (int, float)):
                sector_value = sector_data[key]
                
                if method == 'z-score' and sector_data.get(f"{key}_std", 0) > 0:
                    # Z-score standardization
                    std_dev = sector_data.get(f"{key}_std", 1)
                    standardized[key] = (value - sector_value) / std_dev
                else:
                    # Simple ratio to sector average
                    if sector_value != 0:
                        standardized[key] = value / sector_value
                    else:
                        standardized[key] = None
            else:
                standardized[key] = value
        
        return standardized
    
    def _standardize_data(self, data: Dict, method: str) -> Dict:
        """
        Standardize data using statistical methods.
        
        Args:
            data: Data to standardize
            method: Standardization method
            
        Returns:
            Dict: Standardized data
        """
        standardized = {}
        
        # Calculate statistics for numeric fields
        numeric_values = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                numeric_values[key] = value
        
        if method == 'z-score':
            # Calculate mean and standard deviation
            mean = np.mean(list(numeric_values.values()))
            std_dev = np.std(list(numeric_values.values()))
            
            # Standardize using z-score
            for key, value in data.items():
                if key in numeric_values:
                    if std_dev > 0:
                        standardized[key] = (value - mean) / std_dev
                    else:
                        standardized[key] = 0
                else:
                    standardized[key] = value
        
        elif method == 'min-max':
            # Calculate min and max
            min_val = np.min(list(numeric_values.values()))
            max_val = np.max(list(numeric_values.values()))
            
            # Standardize using min-max scaling
            for key, value in data.items():
                if key in numeric_values:
                    if max_val > min_val:
                        standardized[key] = (value - min_val) / (max_val - min_val)
                    else:
                        standardized[key] = 0.5
                else:
                    standardized[key] = value
        
        elif method == 'robust':
            # Calculate median and IQR
            median = np.median(list(numeric_values.values()))
            q1 = np.percentile(list(numeric_values.values()), 25)
            q3 = np.percentile(list(numeric_values.values()), 75)
            iqr = q3 - q1
            
            # Standardize using robust scaling
            for key, value in data.items():
                if key in numeric_values:
                    if iqr > 0:
                        standardized[key] = (value - median) / iqr
                    else:
                        standardized[key] = 0
                else:
                    standardized[key] = value
        
        else:
            # No standardization
            standardized = data
        
        return standardized
    
    def process_financial_data(self, financial_data: Dict, sector_data: Optional[Dict] = None) -> Dict:
        """
        Process financial data by applying all processing steps.
        
        Args:
            financial_data: Financial statements data
            sector_data: Sector data for sector-based standardization
            
        Returns:
            Dict: Processed financial data
        """
        logger.info("Processing financial data")
        
        # Apply processing steps
        normalized_data = self.normalize_financial_statements(financial_data)
        data_with_growth = self.calculate_growth_rates(normalized_data)
        data_with_ttm = self.calculate_ttm_values(data_with_growth)
        standardized_data = self.standardize_data(data_with_ttm, sector_data)
        
        # Add processing metadata
        standardized_data['processing_metadata'] = {
            'processed_at': datetime.now().isoformat(),
            'normalization_method': self.config['normalization'],
            'standardization_method': self.config['standardization']['method'],
            'sector_based_standardization': self.config['standardization']['sector_based'] and sector_data is not None
        }
        
        return standardized_data
    
    def save_processed_data(self, processed_data: Dict, symbol: str) -> str:
        """
        Save processed financial data to file.
        
        Args:
            processed_data: Processed financial data
            symbol: Company symbol
            
        Returns:
            str: Path to saved file
        """
        logger.info(f"Saving processed data for {symbol}")
        
        # Create output directory
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        # Save to file
        file_path = os.path.join(self.config['output_dir'], f"{symbol}_processed.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            return file_path
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            return f"Error: {str(e)}"
    
    def load_processed_data(self, symbol: str) -> Optional[Dict]:
        """
        Load processed financial data from file.
        
        Args:
            symbol: Company symbol
            
        Returns:
            Optional[Dict]: Processed financial data or None if file doesn't exist
        """
        logger.info(f"Loading processed data for {symbol}")
        
        file_path = os.path.join(self.config['output_dir'], f"{symbol}_processed.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Processed data file not found for {symbol}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return None
    
    def compare_companies(self, symbols: List[str], metrics: List[str]) -> pd.DataFrame:
        """
        Compare multiple companies based on specified metrics.
        
        Args:
            symbols: List of company symbols
            metrics: List of metrics to compare
            
        Returns:
            pd.DataFrame: Comparison table
        """
        logger.info(f"Comparing companies: {', '.join(symbols)}")
        
        # Load processed data for each company
        company_data = {}
        for symbol in symbols:
            data = self.load_processed_data(symbol)
            if data:
                company_data[symbol] = data
        
        if not company_data:
            logger.warning("No processed data found for any company")
            return pd.DataFrame()
        
        # Extract metrics
        comparison_data = {}
        
        for symbol, data in company_data.items():
            company_metrics = {}
            
            # Extract profile data
            if 'profile' in data:
                profile = data['profile']
                for metric in metrics:
                    if metric in profile:
                        company_metrics[metric] = profile[metric]
            
            # Extract ratio data
            if 'ratios' in data:
                ratios = data['ratios']
                for metric in metrics:
                    if metric in ratios:
                        company_metrics[metric] = ratios[metric]
            
            # Extract standardized ratio data
            if 'standardized_ratios' in data:
                std_ratios = data['standardized_ratios']
                for metric in metrics:
                    std_metric = f"{metric}_standardized"
                    if metric in std_ratios:
                        company_metrics[std_metric] = std_ratios[metric]
            
            comparison_data[symbol] = company_metrics
        
        # Create DataFrame
        df = pd.DataFrame.from_dict(comparison_data, orient='index')
        
        return df