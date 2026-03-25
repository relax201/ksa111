"""
Financial Statements Module for Saudi Stock Market (Tasi)

This module provides tools for retrieving, processing, and analyzing
financial statements for Saudi companies.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class FinancialStatements:
    """
    A class for handling financial statements data for Saudi companies.
    """
    
    def __init__(self, data_source=None):
        """
        Initialize the financial statements handler.
        
        Args:
            data_source: Source for financial data (API, database, etc.)
        """
        self.data_source = data_source
        self.statements = {}
    
    def load_statements(self, ticker, period_type='annual', years=5):
        """
        Load financial statements for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            period_type (str): 'annual' or 'quarterly'
            years (int): Number of years of data to retrieve
            
        Returns:
            dict: Financial statements
        """
        # This would connect to the data source and retrieve statements
        # For now, return a placeholder structure
        
        # Placeholder for actual implementation
        statements = {
            'income_statement': self._generate_placeholder_income_statement(years, period_type),
            'balance_sheet': self._generate_placeholder_balance_sheet(years, period_type),
            'cash_flow': self._generate_placeholder_cash_flow(years, period_type),
            'metadata': {
                'ticker': ticker,
                'period_type': period_type,
                'years': years,
                'currency': 'SAR',
                'retrieved_at': datetime.now().strftime('%Y-%m-%d')
            }
        }
        
        self.statements = statements
        return statements
    
    def _generate_placeholder_income_statement(self, years, period_type):
        """
        Generate placeholder income statement data.
        
        Args:
            years (int): Number of years
            period_type (str): 'annual' or 'quarterly'
            
        Returns:
            DataFrame: Placeholder income statement
        """
        # Determine number of periods
        periods = years if period_type == 'annual' else years * 4
        
        # Generate dates
        if period_type == 'annual':
            end_year = datetime.now().year - 1  # Last complete year
            dates = [f"{year}-12-31" for year in range(end_year - years + 1, end_year + 1)]
        else:
            # Generate quarterly dates
            end_year = datetime.now().year
            end_quarter = (datetime.now().month - 1) // 3  # Current quarter (0-3)
            
            dates = []
            year = end_year
            quarter = end_quarter
            
            for _ in range(periods):
                month = quarter * 3 + 3
                dates.append(f"{year}-{month:02d}-{30 if month != 2 else 28}")
                
                quarter -= 1
                if quarter < 0:
                    quarter = 3
                    year -= 1
            
            dates.reverse()  # Chronological order
        
        # Create DataFrame
        df = pd.DataFrame(index=dates)
        
        # Add columns with placeholder data
        df['revenue'] = np.linspace(1000000, 2000000, periods)  # Growing revenue
        df['cost_of_goods_sold'] = df['revenue'] * np.random.uniform(0.6, 0.7, periods)
        df['gross_profit'] = df['revenue'] - df['cost_of_goods_sold']
        
        df['operating_expenses'] = df['revenue'] * np.random.uniform(0.2, 0.3, periods)
        df['operating_income'] = df['gross_profit'] - df['operating_expenses']
        
        df['interest_expense'] = np.random.uniform(10000, 50000, periods)
        df['other_income_expense'] = np.random.uniform(-20000, 20000, periods)
        
        df['income_before_tax'] = df['operating_income'] - df['interest_expense'] + df['other_income_expense']
        df['income_tax'] = df['income_before_tax'] * np.random.uniform(0.15, 0.25, periods)
        df['net_income'] = df['income_before_tax'] - df['income_tax']
        
        df['ebitda'] = df['operating_income'] + np.random.uniform(50000, 100000, periods)  # Depreciation & amortization
        df['eps_basic'] = df['net_income'] / np.random.uniform(10000000, 15000000, periods)  # Shares outstanding
        
        return df
    
    def _generate_placeholder_balance_sheet(self, years, period_type):
        """
        Generate placeholder balance sheet data.
        
        Args:
            years (int): Number of years
            period_type (str): 'annual' or 'quarterly'
            
        Returns:
            DataFrame: Placeholder balance sheet
        """
        # Determine number of periods
        periods = years if period_type == 'annual' else years * 4
        
        # Generate dates (same as income statement)
        if period_type == 'annual':
            end_year = datetime.now().year - 1
            dates = [f"{year}-12-31" for year in range(end_year - years + 1, end_year + 1)]
        else:
            end_year = datetime.now().year
            end_quarter = (datetime.now().month - 1) // 3
            
            dates = []
            year = end_year
            quarter = end_quarter
            
            for _ in range(periods):
                month = quarter * 3 + 3
                dates.append(f"{year}-{month:02d}-{30 if month != 2 else 28}")
                
                quarter -= 1
                if quarter < 0:
                    quarter = 3
                    year -= 1
            
            dates.reverse()
        
        # Create DataFrame
        df = pd.DataFrame(index=dates)
        
        # Add columns with placeholder data
        # Assets
        df['cash_and_equivalents'] = np.random.uniform(100000, 300000, periods)
        df['short_term_investments'] = np.random.uniform(50000, 150000, periods)
        df['accounts_receivable'] = np.random.uniform(200000, 400000, periods)
        df['inventory'] = np.random.uniform(300000, 500000, periods)
        df['other_current_assets'] = np.random.uniform(50000, 100000, periods)
        df['current_assets'] = df['cash_and_equivalents'] + df['short_term_investments'] + \
                              df['accounts_receivable'] + df['inventory'] + df['other_current_assets']
        
        df['property_plant_equipment'] = np.linspace(1000000, 1500000, periods)  # Growing PPE
        df['intangible_assets'] = np.random.uniform(200000, 300000, periods)
        df['long_term_investments'] = np.random.uniform(300000, 500000, periods)
        df['other_non_current_assets'] = np.random.uniform(100000, 200000, periods)
        df['non_current_assets'] = df['property_plant_equipment'] + df['intangible_assets'] + \
                                  df['long_term_investments'] + df['other_non_current_assets']
        
        df['total_assets'] = df['current_assets'] + df['non_current_assets']
        
        # Liabilities
        df['accounts_payable'] = np.random.uniform(150000, 250000, periods)
        df['short_term_debt'] = np.random.uniform(100000, 200000, periods)
        df['other_current_liabilities'] = np.random.uniform(100000, 150000, periods)
        df['current_liabilities'] = df['accounts_payable'] + df['short_term_debt'] + df['other_current_liabilities']
        
        df['long_term_debt'] = np.random.uniform(500000, 700000, periods)
        df['other_non_current_liabilities'] = np.random.uniform(200000, 300000, periods)
        df['non_current_liabilities'] = df['long_term_debt'] + df['other_non_current_liabilities']
        
        df['total_liabilities'] = df['current_liabilities'] + df['non_current_liabilities']
        
        # Equity
        df['common_stock'] = np.random.uniform(500000, 600000, periods)
        df['retained_earnings'] = np.linspace(500000, 1000000, periods)  # Growing retained earnings
        df['other_equity'] = np.random.uniform(-50000, 50000, periods)
        df['total_equity'] = df['common_stock'] + df['retained_earnings'] + df['other_equity']
        
        # Ensure balance sheet balances
        df['total_liabilities_and_equity'] = df['total_liabilities'] + df['total_equity']
        
        # Additional metrics
        df['total_debt'] = df['short_term_debt'] + df['long_term_debt']
        df['net_debt'] = df['total_debt'] - df['cash_and_equivalents']
        df['working_capital'] = df['current_assets'] - df['current_liabilities']
        
        return df
    
    def _generate_placeholder_cash_flow(self, years, period_type):
        """
        Generate placeholder cash flow statement data.
        
        Args:
            years (int): Number of years
            period_type (str): 'annual' or 'quarterly'
            
        Returns:
            DataFrame: Placeholder cash flow statement
        """
        # Determine number of periods
        periods = years if period_type == 'annual' else years * 4
        
        # Generate dates (same as other statements)
        if period_type == 'annual':
            end_year = datetime.now().year - 1
            dates = [f"{year}-12-31" for year in range(end_year - years + 1, end_year + 1)]
        else:
            end_year = datetime.now().year
            end_quarter = (datetime.now().month - 1) // 3
            
            dates = []
            year = end_year
            quarter = end_quarter
            
            for _ in range(periods):
                month = quarter * 3 + 3
                dates.append(f"{year}-{month:02d}-{30 if month != 2 else 28}")
                
                quarter -= 1
                if quarter < 0:
                    quarter = 3
                    year -= 1
            
            dates.reverse()
        
        # Create DataFrame
        df = pd.DataFrame(index=dates)
        
        # Add columns with placeholder data
        # Operating activities
        df['net_income'] = np.linspace(200000, 400000, periods)  # Growing net income
        df['depreciation_amortization'] = np.random.uniform(50000, 100000, periods)
        df['changes_in_working_capital'] = np.random.uniform(-50000, 50000, periods)
        df['other_operating_activities'] = np.random.uniform(-30000, 30000, periods)
        df['operating_cash_flow'] = df['net_income'] + df['depreciation_amortization'] + \
                                   df['changes_in_working_capital'] + df['other_operating_activities']
        
        # Investing activities
        df['capital_expenditures'] = -np.random.uniform(100000, 200000, periods)  # Negative for cash outflow
        df['acquisitions'] = -np.random.uniform(0, 100000, periods)
        df['other_investing_activities'] = np.random.uniform(-50000, 50000, periods)
        df['investing_cash_flow'] = df['capital_expenditures'] + df['acquisitions'] + df['other_investing_activities']
        
        # Financing activities
        df['debt_issuance_repayment'] = np.random.uniform(-100000, 100000, periods)
        df['dividends_paid'] = -np.random.uniform(50000, 100000, periods)  # Negative for cash outflow
        df['share_repurchases'] = -np.random.uniform(0, 50000, periods)
        df['other_financing_activities'] = np.random.uniform(-30000, 30000, periods)
        df['financing_cash_flow'] = df['debt_issuance_repayment'] + df['dividends_paid'] + \
                                   df['share_repurchases'] + df['other_financing_activities']
        
        # Net change in cash
        df['net_change_in_cash'] = df['operating_cash_flow'] + df['investing_cash_flow'] + df['financing_cash_flow']
        
        # Additional metrics
        df['free_cash_flow'] = df['operating_cash_flow'] + df['capital_expenditures']
        
        return df
    
    def get_latest_statements(self):
        """
        Get the most recent financial statements.
        
        Returns:
            dict: Latest financial statements
        """
        if not self.statements:
            return None
        
        # Extract the most recent data from each statement
        income_stmt = self.statements['income_statement']
        balance_sheet = self.statements['balance_sheet']
        cash_flow = self.statements['cash_flow']
        
        latest = {
            'income_statement': income_stmt.iloc[-1].to_dict(),
            'balance_sheet': balance_sheet.iloc[-1].to_dict(),
            'cash_flow': cash_flow.iloc[-1].to_dict(),
            'metadata': self.statements['metadata']
        }
        
        return latest
    
    def get_historical_data(self, metrics=None):
        """
        Get historical data for specific metrics.
        
        Args:
            metrics (list): List of metrics to retrieve
            
        Returns:
            dict: Historical data for specified metrics
        """
        if not self.statements:
            return None
        
        if metrics is None:
            metrics = [
                'revenue', 'net_income', 'ebitda', 'eps_basic',
                'total_assets', 'total_equity', 'total_debt',
                'operating_cash_flow', 'free_cash_flow'
            ]
        
        historical_data = {}
        
        for metric in metrics:
            # Find which statement contains this metric
            for stmt_name, stmt_df in [
                ('income_statement', self.statements['income_statement']),
                ('balance_sheet', self.statements['balance_sheet']),
                ('cash_flow', self.statements['cash_flow'])
            ]:
                if metric in stmt_df.columns:
                    historical_data[metric] = stmt_df[metric].tolist()
                    break
        
        return historical_data
    
    def calculate_growth_rates(self, metrics=None, periods=None):
        """
        Calculate growth rates for specified metrics.
        
        Args:
            metrics (list): List of metrics to analyze
            periods (list): List of periods to calculate (e.g., [1, 3, 5] for 1-year, 3-year, 5-year)
            
        Returns:
            dict: Growth rates for each metric and period
        """
        if not self.statements:
            return None
        
        if metrics is None:
            metrics = ['revenue', 'net_income', 'ebitda', 'eps_basic']
        
        if periods is None:
            periods = [1, 3, 5]
        
        growth_rates = {}
        
        for metric in metrics:
            metric_rates = {}
            
            # Find which statement contains this metric
            for stmt_name, stmt_df in [
                ('income_statement', self.statements['income_statement']),
                ('balance_sheet', self.statements['balance_sheet']),
                ('cash_flow', self.statements['cash_flow'])
            ]:
                if metric in stmt_df.columns:
                    series = stmt_df[metric]
                    
                    for period in periods:
                        if len(series) > period:
                            # Calculate compound annual growth rate
                            start_value = series.iloc[-period-1]
                            end_value = series.iloc[-1]
                            
                            if start_value > 0 and end_value > 0:
                                cagr = (end_value / start_value) ** (1 / period) - 1
                                metric_rates[f"{period}_year"] = cagr
                            else:
                                metric_rates[f"{period}_year"] = None
                        else:
                            metric_rates[f"{period}_year"] = None
                    
                    break
            
            growth_rates[metric] = metric_rates
        
        return growth_rates
    
    def save_statements(self, directory, ticker=None):
        """
        Save financial statements to files.
        
        Args:
            directory (str): Directory to save files
            ticker (str): Stock ticker symbol (defaults to metadata ticker)
            
        Returns:
            dict: Paths to saved files
        """
        if not self.statements:
            return None
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Get ticker from metadata if not provided
        if ticker is None:
            ticker = self.statements['metadata']['ticker']
        
        # Save each statement to a CSV file
        paths = {}
        
        for stmt_name, stmt_df in [
            ('income_statement', self.statements['income_statement']),
            ('balance_sheet', self.statements['balance_sheet']),
            ('cash_flow', self.statements['cash_flow'])
        ]:
            file_path = os.path.join(directory, f"{ticker}_{stmt_name}.csv")
            stmt_df.to_csv(file_path)
            paths[stmt_name] = file_path
        
        # Save metadata to JSON
        metadata_path = os.path.join(directory, f"{ticker}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(self.statements['metadata'], f, indent=2)
        
        paths['metadata'] = metadata_path
        
        return paths
    
    @classmethod
    def load_statements_from_files(cls, directory, ticker):
        """
        Load financial statements from files.
        
        Args:
            directory (str): Directory containing the files
            ticker (str): Stock ticker symbol
            
        Returns:
            FinancialStatements: Instance with loaded statements
        """
        instance = cls()
        
        # Load metadata
        metadata_path = os.path.join(directory, f"{ticker}_metadata.json")
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        except FileNotFoundError:
            return None
        
        # Load each statement
        statements = {'metadata': metadata}
        
        for stmt_name in ['income_statement', 'balance_sheet', 'cash_flow']:
            file_path = os.path.join(directory, f"{ticker}_{stmt_name}.csv")
            try:
                stmt_df = pd.read_csv(file_path, index_col=0)
                statements[stmt_name] = stmt_df
            except FileNotFoundError:
                return None
        
        instance.statements = statements
        return instance