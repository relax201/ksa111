"""
Market Data Collector for Saudi Stock Market (Tasi)

This module provides tools for collecting market data from various sources.
"""

import requests
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    """
    A class for collecting market data from various sources.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the market data collector.
        
        Args:
            api_key: API key for data sources
            config_path: Path to configuration file
        """
        self.api_key = api_key
        self.config = self._load_config(config_path) if config_path else {}
        self.base_url = self.config.get('base_url', 'https://app.sahmk.sa/api/v1')
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key if self.api_key else ''
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict: Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def get_market_summary(self) -> Dict:
        """
        Get market summary data.
        
        Returns:
            Dict: Market summary data
        """
        try:
            endpoint = f"{self.base_url}/market/summary/"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")
            return {}
    
    def get_stock_list(self) -> List[Dict]:
        """
        Get list of all stocks.
        
        Returns:
            List[Dict]: List of stocks
        """
        try:
            endpoint = f"{self.base_url}/stocks"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching stock list: {e}")
            return []
    
    def get_stock_price(self, symbol: str) -> Dict:
        """
        Get current price for a specific stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict: Stock price data
        """
        try:
            endpoint = f"{self.base_url}/quote/{symbol}/"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return {}
    
    def get_historical_prices(self, symbol: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, period: str = 'daily') -> pd.DataFrame:
        """
        Get historical prices for a specific stock.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Data period ('daily', 'weekly', 'monthly')
            
        Returns:
            pd.DataFrame: Historical price data
        """
        try:
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if not start_date:
                # Default to 1 year of data
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            endpoint = f"{self.base_url}/historical/{symbol}/"
            params = {
                'from': start_date,
                'to': end_date,
                'interval': '1d' if period == 'daily' else ('1w' if period == 'weekly' else '1m')
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json().get('data', [])
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Convert date column to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_market_indices(self) -> List[Dict]:
        """
        Get market indices data.
        
        Returns:
            List[Dict]: Market indices data
        """
        try:
            endpoint = f"{self.base_url}/market/indices"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return []
    
    def get_sector_performance(self) -> List[Dict]:
        """
        Get sector performance data.
        
        Returns:
            List[Dict]: Sector performance data
        """
        try:
            endpoint = f"{self.base_url}/market/sectors/"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json().get('sectors', [])
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return []
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """
        Get top gaining stocks.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List[Dict]: Top gaining stocks
        """
        try:
            endpoint = f"{self.base_url}/market/gainers/"
            params = {'limit': limit}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('gainers', [])
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """
        Get top losing stocks.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List[Dict]: Top losing stocks
        """
        try:
            endpoint = f"{self.base_url}/market/losers/"
            params = {'limit': limit}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('losers', [])
        except Exception as e:
            logger.error(f"Error fetching top losers: {e}")
            return []
    
    def get_most_active(self, limit: int = 10, by: str = 'volume') -> List[Dict]:
        """
        Get most active stocks.
        
        Args:
            limit: Number of stocks to return
            by: Metric to sort by ('volume', 'value')
            
        Returns:
            List[Dict]: Most active stocks
        """
        try:
            endpoint = f"{self.base_url}/market/volume/" if by == 'volume' else f"{self.base_url}/market/value/"
            params = {'limit': limit}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('stocks', [])
        except Exception as e:
            logger.error(f"Error fetching most active stocks: {e}")
            return []
    
    def get_company_profile(self, symbol: str) -> Dict:
        """
        Get company profile data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict: Company profile data
        """
        try:
            endpoint = f"{self.base_url}/company/{symbol}/"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return {}
    
    def get_company_financials(self, symbol: str, period: str = 'annual') -> Dict:
        """
        Get company financial data.
        
        Args:
            symbol: Stock symbol
            period: Financial period ('annual', 'quarterly')
            
        Returns:
            Dict: Company financial data
        """
        try:
            endpoint = f"{self.base_url}/financials/{symbol}/"
            params = {'period': period}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching company financials for {symbol}: {e}")
            return {}
    
    def get_market_news(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Get market news.
        
        Args:
            limit: Number of news items to return
            offset: Offset for pagination
            
        Returns:
            List[Dict]: Market news
        """
        try:
            endpoint = f"{self.base_url}/market/news"
            params = {'limit': limit, 'offset': offset}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []
    
    def get_company_news(self, symbol: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Get company-specific news.
        
        Args:
            symbol: Stock symbol
            limit: Number of news items to return
            offset: Offset for pagination
            
        Returns:
            List[Dict]: Company news
        """
        try:
            endpoint = f"{self.base_url}/stocks/{symbol}/news"
            params = {'limit': limit, 'offset': offset}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching company news for {symbol}: {e}")
            return []
    
    def save_data_to_csv(self, data: Union[pd.DataFrame, List, Dict], 
                        filename: str, index: bool = True) -> bool:
        """
        Save data to CSV file.
        
        Args:
            data: Data to save
            filename: Output filename
            index: Whether to include index in output
            
        Returns:
            bool: Success status
        """
        try:
            # Convert to DataFrame if not already
            if not isinstance(data, pd.DataFrame):
                df = pd.DataFrame(data)
            else:
                df = data
            
            df.to_csv(filename, index=index)
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {e}")
            return False
    
    def save_data_to_json(self, data: Any, filename: str) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            filename: Output filename
            
        Returns:
            bool: Success status
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {e}")
            return False

    # ---- واجهة التكامل مع system_integration.py ----

    def collect_data(self, symbols: List[str], data_types: Optional[List[str]] = None) -> Dict:
        """جمع بيانات السوق لمجموعة من الرموز."""
        if data_types is None:
            data_types = ['price', 'volume', 'market_cap']
        result = {}
        for symbol in symbols:
            try:
                stock_data = {}
                price_data = self.get_stock_price(symbol)
                if 'price' in data_types and price_data:
                    stock_data['price'] = price_data
                if 'volume' in data_types and price_data:
                    stock_data['volume'] = price_data.get('volume')
                if 'market_cap' in data_types:
                    profile = self.get_company_profile(symbol)
                    stock_data['market_cap'] = profile.get('market_cap')
                result[symbol] = stock_data
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {e}")
                result[symbol] = {}
        self._last_update_time = datetime.now().isoformat()
        return result

    def get_last_update_time(self) -> str:
        """إعادة وقت آخر تحديث."""
        if hasattr(self, '_last_update_time'):
            return self._last_update_time
        return datetime.now().isoformat()