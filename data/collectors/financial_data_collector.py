"""
Financial Data Collector for Saudi Stock Market (Tadawul)

This module provides functionality to collect financial data for Saudi companies
from various sources including Tadawul, Argaam, and company websites.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialDataCollector:
    """
    A class for collecting financial data for Saudi companies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the financial data collector.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept': 'application/json, text/plain, */*',
        }
        
        # Add API keys if available
        if 'api_keys' in self.config:
            self.api_keys = self.config['api_keys']
        else:
            self.api_keys = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict: Configuration dictionary
        """
        default_config = {
            'sources': {
                'tadawul': {
                    'base_url': 'https://www.saudiexchange.sa/wps/portal/tadawul/market-participants/issuers/issuers-directory/',
                    'financial_url': 'https://www.saudiexchange.sa/wps/portal/tadawul/market-participants/issuers/issuers-reports-and-announcements/'
                },
                'argaam': {
                    'base_url': 'https://www.argaam.com/ar/company/',
                    'financial_url': 'https://www.argaam.com/ar/company/financial-statements/'
                }
            },
            'cache_dir': './cache',
            'cache_expiry': 86400  # 24 hours in seconds
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
    
    def get_company_list(self, market: str = 'all') -> List[Dict]:
        """
        Get list of companies in the Saudi market.
        
        Args:
            market: Market segment ('main', 'nomu', 'all')
            
        Returns:
            List[Dict]: List of companies with basic information
        """
        logger.info(f"Fetching company list for market: {market}")
        
        # Check cache first
        cache_file = os.path.join(self.config['cache_dir'], f'companies_{market}.json')
        if os.path.exists(cache_file):
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if file_age < self.config['cache_expiry']:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
        
        # If cache doesn't exist or is expired, fetch from source
        companies = []
        
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['tadawul']['base_url']}companies"
            
            if 'tadawul' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['tadawul']}"
            
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on the actual API structure
            # This is a placeholder for the actual implementation
            for item in data.get('companies', []):
                if market == 'all' or item.get('market') == market:
                    companies.append({
                        'symbol': item.get('symbol'),
                        'name': item.get('name'),
                        'name_ar': item.get('name_ar'),
                        'sector': item.get('sector'),
                        'market': item.get('market'),
                        'isin': item.get('isin')
                    })
            
            # Save to cache
            os.makedirs(self.config['cache_dir'], exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(companies, f, ensure_ascii=False, indent=2)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error fetching company list: {e}")
            
            # If there's an error but we have a cache file, use it even if expired
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as cache_e:
                    logger.error(f"Error reading cache file: {cache_e}")
            
            return []
    
    def get_financial_statements(self, symbol: str, 
                               statement_type: str = 'income', 
                               period: str = 'annual',
                               years: int = 5) -> Dict:
        """
        Get financial statements for a company.
        
        Args:
            symbol: Company symbol
            statement_type: Type of statement ('income', 'balance', 'cash_flow')
            period: Period ('annual', 'quarterly')
            years: Number of years to retrieve
            
        Returns:
            Dict: Financial statement data
        """
        logger.info(f"Fetching {statement_type} statement for {symbol} ({period}, {years} years)")
        
        # Check cache first
        cache_file = os.path.join(self.config['cache_dir'], f'{symbol}_{statement_type}_{period}.json')
        if os.path.exists(cache_file):
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if file_age < self.config['cache_expiry']:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
        
        # If cache doesn't exist or is expired, fetch from source
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['argaam']['financial_url']}{symbol}"
            
            if 'argaam' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['argaam']}"
            
            params = {
                'type': statement_type,
                'period': period,
                'years': years
            }
            
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on the actual API structure
            # This is a placeholder for the actual implementation
            statements = {
                'symbol': symbol,
                'statement_type': statement_type,
                'period': period,
                'currency': data.get('currency', 'SAR'),
                'unit': data.get('unit', 'million'),
                'data': data.get('statements', [])
            }
            
            # Save to cache
            os.makedirs(self.config['cache_dir'], exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(statements, f, ensure_ascii=False, indent=2)
            
            return statements
            
        except Exception as e:
            logger.error(f"Error fetching financial statements: {e}")
            
            # If there's an error but we have a cache file, use it even if expired
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as cache_e:
                    logger.error(f"Error reading cache file: {cache_e}")
            
            return {
                'symbol': symbol,
                'statement_type': statement_type,
                'period': period,
                'currency': 'SAR',
                'unit': 'million',
                'data': []
            }
    
    def get_company_profile(self, symbol: str) -> Dict:
        """
        Get company profile information.
        
        Args:
            symbol: Company symbol
            
        Returns:
            Dict: Company profile data
        """
        logger.info(f"Fetching company profile for {symbol}")
        
        # Check cache first
        cache_file = os.path.join(self.config['cache_dir'], f'{symbol}_profile.json')
        if os.path.exists(cache_file):
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if file_age < self.config['cache_expiry']:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
        
        # If cache doesn't exist or is expired, fetch from source
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['tadawul']['base_url']}{symbol}"
            
            if 'tadawul' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['tadawul']}"
            
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on the actual API structure
            # This is a placeholder for the actual implementation
            profile = {
                'symbol': symbol,
                'name': data.get('name'),
                'name_ar': data.get('name_ar'),
                'sector': data.get('sector'),
                'industry': data.get('industry'),
                'description': data.get('description'),
                'website': data.get('website'),
                'address': data.get('address'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'ceo': data.get('ceo'),
                'established_date': data.get('established_date'),
                'listing_date': data.get('listing_date'),
                'fiscal_year_end': data.get('fiscal_year_end'),
                'auditor': data.get('auditor'),
                'shares_outstanding': data.get('shares_outstanding'),
                'free_float': data.get('free_float'),
                'market_cap': data.get('market_cap')
            }
            
            # Save to cache
            os.makedirs(self.config['cache_dir'], exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error fetching company profile: {e}")
            
            # If there's an error but we have a cache file, use it even if expired
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as cache_e:
                    logger.error(f"Error reading cache file: {cache_e}")
            
            return {
                'symbol': symbol,
                'name': '',
                'name_ar': '',
                'sector': '',
                'industry': '',
                'description': '',
                'website': '',
                'address': '',
                'phone': '',
                'email': '',
                'ceo': '',
                'established_date': '',
                'listing_date': '',
                'fiscal_year_end': '',
                'auditor': '',
                'shares_outstanding': 0,
                'free_float': 0,
                'market_cap': 0
            }
    
    def get_market_data(self, symbol: str, 
                      start_date: Optional[str] = None, 
                      end_date: Optional[str] = None,
                      interval: str = 'daily') -> pd.DataFrame:
        """
        Get market data (OHLCV) for a company.
        
        Args:
            symbol: Company symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')
            
        Returns:
            pd.DataFrame: Market data
        """
        logger.info(f"Fetching market data for {symbol} ({interval})")
        
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if start_date is None:
            if interval == 'daily':
                # Default to 1 year for daily data
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            elif interval == 'weekly':
                # Default to 3 years for weekly data
                start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
            else:
                # Default to 5 years for monthly data
                start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        
        # Check cache first
        cache_file = os.path.join(self.config['cache_dir'], f'{symbol}_market_{interval}_{start_date}_{end_date}.csv')
        if os.path.exists(cache_file):
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if file_age < self.config['cache_expiry']:
                try:
                    return pd.read_csv(cache_file, parse_dates=['date'], index_col='date')
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
        
        # If cache doesn't exist or is expired, fetch from source
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['tadawul']['base_url']}historical/{symbol}"
            
            if 'tadawul' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['tadawul']}"
            
            params = {
                'from': start_date,
                'to': end_date,
                'interval': interval
            }
            
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on the actual API structure
            # This is a placeholder for the actual implementation
            market_data = pd.DataFrame(data.get('data', []))
            
            if not market_data.empty:
                # Convert date column to datetime
                market_data['date'] = pd.to_datetime(market_data['date'])
                
                # Set date as index
                market_data.set_index('date', inplace=True)
                
                # Sort by date
                market_data.sort_index(inplace=True)
                
                # Save to cache
                os.makedirs(self.config['cache_dir'], exist_ok=True)
                market_data.to_csv(cache_file)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            
            # If there's an error but we have a cache file, use it even if expired
            if os.path.exists(cache_file):
                try:
                    return pd.read_csv(cache_file, parse_dates=['date'], index_col='date')
                except Exception as cache_e:
                    logger.error(f"Error reading cache file: {cache_e}")
            
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    
    def get_sector_data(self, sector: str) -> Dict:
        """
        Get sector data.
        
        Args:
            sector: Sector name
            
        Returns:
            Dict: Sector data
        """
        logger.info(f"Fetching sector data for {sector}")
        
        # Check cache first
        cache_file = os.path.join(self.config['cache_dir'], f'sector_{sector}.json')
        if os.path.exists(cache_file):
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if file_age < self.config['cache_expiry']:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
        
        # If cache doesn't exist or is expired, fetch from source
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['tadawul']['base_url']}sectors/{sector}"
            
            if 'tadawul' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['tadawul']}"
            
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on the actual API structure
            # This is a placeholder for the actual implementation
            sector_data = {
                'name': data.get('name'),
                'name_ar': data.get('name_ar'),
                'companies_count': data.get('companies_count'),
                'market_cap': data.get('market_cap'),
                'pe_ratio': data.get('pe_ratio'),
                'pb_ratio': data.get('pb_ratio'),
                'dividend_yield': data.get('dividend_yield'),
                'ytd_return': data.get('ytd_return'),
                'companies': data.get('companies', [])
            }
            
            # Save to cache
            os.makedirs(self.config['cache_dir'], exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(sector_data, f, ensure_ascii=False, indent=2)
            
            return sector_data
            
        except Exception as e:
            logger.error(f"Error fetching sector data: {e}")
            
            # If there's an error but we have a cache file, use it even if expired
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as cache_e:
                    logger.error(f"Error reading cache file: {cache_e}")
            
            return {
                'name': sector,
                'name_ar': '',
                'companies_count': 0,
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0,
                'dividend_yield': 0,
                'ytd_return': 0,
                'companies': []
            }
    
    def get_all_financial_data(self, symbol: str) -> Dict:
        """
        Get all financial data for a company.
        
        Args:
            symbol: Company symbol
            
        Returns:
            Dict: All financial data
        """
        logger.info(f"Fetching all financial data for {symbol}")
        
        # Get company profile
        profile = self.get_company_profile(symbol)
        
        # Get financial statements
        income_statement = self.get_financial_statements(symbol, 'income', 'annual')
        balance_sheet = self.get_financial_statements(symbol, 'balance', 'annual')
        cash_flow = self.get_financial_statements(symbol, 'cash_flow', 'annual')
        
        # Get quarterly statements
        quarterly_income = self.get_financial_statements(symbol, 'income', 'quarterly')
        
        # Get market data
        market_data = self.get_market_data(symbol)
        
        # Combine all data
        all_data = {
            'profile': profile,
            'financial_statements': {
                'income_statement': income_statement,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'quarterly_income': quarterly_income
            },
            'market_data': market_data.to_dict(orient='records') if not market_data.empty else []
        }
        
        return all_data
    
    def download_financial_reports(self, symbol: str, year: int, quarter: Optional[int] = None, 
                                 report_type: str = 'financial') -> str:
        """
        Download financial reports for a company.
        
        Args:
            symbol: Company symbol
            year: Report year
            quarter: Report quarter (1-4, None for annual)
            report_type: Report type ('financial', 'board', 'presentation')
            
        Returns:
            str: Path to downloaded file or error message
        """
        logger.info(f"Downloading {report_type} report for {symbol} ({year} Q{quarter if quarter else 'Annual'})")
        
        # Create directory for reports
        reports_dir = os.path.join(self.config['cache_dir'], 'reports', symbol)
        os.makedirs(reports_dir, exist_ok=True)
        
        # Determine file name
        period = f"Q{quarter}" if quarter else "Annual"
        file_name = f"{symbol}_{year}_{period}_{report_type}.pdf"
        file_path = os.path.join(reports_dir, file_name)
        
        # Check if file already exists
        if os.path.exists(file_path):
            return file_path
        
        try:
            # Implementation depends on the actual API structure
            # This is a placeholder for the actual implementation
            url = f"{self.config['sources']['tadawul']['financial_url']}{symbol}/reports"
            
            if 'tadawul' in self.api_keys:
                self.headers['Authorization'] = f"Bearer {self.api_keys['tadawul']}"
            
            params = {
                'year': year,
                'quarter': quarter,
                'type': report_type
            }
            
            response = self.session.get(url, headers=self.headers, params=params, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            return f"Error: {str(e)}"

    # ---- واجهة التكامل مع system_integration.py ----

    def collect_data(self, symbols: List[str],
                     statement_types: Optional[List[str]] = None,
                     periods: Optional[List[str]] = None) -> Dict:
        """جمع البيانات المالية لمجموعة من الرموز."""
        if statement_types is None:
            statement_types = ['income', 'balance', 'cash_flow']
        if periods is None:
            periods = ['annual']
        result = {}
        for symbol in symbols:
            try:
                symbol_data = {}
                for period in periods:
                    period_data = {}
                    for stype in statement_types:
                        period_data[stype] = self.get_financial_statements(symbol, stype, period)
                    symbol_data[period] = period_data
                result[symbol] = symbol_data
            except Exception as e:
                logger.error(f"Error collecting financial data for {symbol}: {e}")
                result[symbol] = {}
        self._last_update_time = datetime.now().isoformat()
        return result

    def get_last_update_time(self) -> str:
        """إعادة وقت آخر تحديث."""
        if hasattr(self, '_last_update_time'):
            return self._last_update_time
        return datetime.now().isoformat()