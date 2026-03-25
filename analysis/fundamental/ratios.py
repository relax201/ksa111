"""
Financial Ratios Module for Saudi Stock Market (Tasi)

This module provides functions for calculating and analyzing
financial ratios for Saudi companies.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class FinancialRatios:
    """
    A class for calculating and analyzing financial ratios
    for Saudi companies based on financial statements.
    """
    
    def __init__(self, financial_data=None):
        """
        Initialize the financial ratios calculator.
        
        Args:
            financial_data (dict): Financial statements data
        """
        self.financial_data = financial_data or {}
    
    def set_financial_data(self, financial_data):
        """
        Set or update financial data.
        
        Args:
            financial_data (dict): Financial statements data
        """
        self.financial_data = financial_data
    
    def profitability_ratios(self):
        """
        Calculate profitability ratios.
        
        Returns:
            dict: Profitability ratios
        """
        income_stmt = self.financial_data.get('income_statement')
        balance_sheet = self.financial_data.get('balance_sheet')
        
        if income_stmt is None or balance_sheet is None:
            return {
                'gross_margin': None,
                'operating_margin': None,
                'net_profit_margin': None,
                'return_on_assets': None,
                'return_on_equity': None,
                'return_on_invested_capital': None
            }
        
        # Extract required values
        revenue = income_stmt.get('revenue', 0)
        gross_profit = income_stmt.get('gross_profit', 0)
        operating_income = income_stmt.get('operating_income', 0)
        net_income = income_stmt.get('net_income', 0)
        
        total_assets = balance_sheet.get('total_assets', 0)
        total_equity = balance_sheet.get('total_equity', 0)
        total_debt = balance_sheet.get('total_debt', 0)
        
        # Calculate ratios
        gross_margin = gross_profit / revenue if revenue else None
        operating_margin = operating_income / revenue if revenue else None
        net_profit_margin = net_income / revenue if revenue else None
        
        return_on_assets = net_income / total_assets if total_assets else None
        return_on_equity = net_income / total_equity if total_equity else None
        
        invested_capital = total_equity + total_debt
        return_on_invested_capital = operating_income / invested_capital if invested_capital else None
        
        return {
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'net_profit_margin': net_profit_margin,
            'return_on_assets': return_on_assets,
            'return_on_equity': return_on_equity,
            'return_on_invested_capital': return_on_invested_capital
        }
    
    def liquidity_ratios(self):
        """
        Calculate liquidity ratios.
        
        Returns:
            dict: Liquidity ratios
        """
        balance_sheet = self.financial_data.get('balance_sheet')
        
        if balance_sheet is None:
            return {
                'current_ratio': None,
                'quick_ratio': None,
                'cash_ratio': None,
                'operating_cash_flow_ratio': None
            }
        
        # Extract required values
        current_assets = balance_sheet.get('current_assets', 0)
        current_liabilities = balance_sheet.get('current_liabilities', 0)
        cash_and_equivalents = balance_sheet.get('cash_and_equivalents', 0)
        short_term_investments = balance_sheet.get('short_term_investments', 0)
        inventory = balance_sheet.get('inventory', 0)
        
        cash_flow = self.financial_data.get('cash_flow', {})
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)
        
        # Calculate ratios
        current_ratio = current_assets / current_liabilities if current_liabilities else None
        
        quick_assets = current_assets - inventory
        quick_ratio = quick_assets / current_liabilities if current_liabilities else None
        
        cash_and_investments = cash_and_equivalents + short_term_investments
        cash_ratio = cash_and_investments / current_liabilities if current_liabilities else None
        
        operating_cash_flow_ratio = operating_cash_flow / current_liabilities if current_liabilities else None
        
        return {
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'cash_ratio': cash_ratio,
            'operating_cash_flow_ratio': operating_cash_flow_ratio
        }
    
    def solvency_ratios(self):
        """
        Calculate solvency ratios.
        
        Returns:
            dict: Solvency ratios
        """
        balance_sheet = self.financial_data.get('balance_sheet')
        income_stmt = self.financial_data.get('income_statement')
        
        if balance_sheet is None or income_stmt is None:
            return {
                'debt_to_equity': None,
                'debt_to_assets': None,
                'interest_coverage': None,
                'debt_service_coverage': None
            }
        
        # Extract required values
        total_debt = balance_sheet.get('total_debt', 0)
        total_equity = balance_sheet.get('total_equity', 0)
        total_assets = balance_sheet.get('total_assets', 0)
        
        operating_income = income_stmt.get('operating_income', 0)
        interest_expense = income_stmt.get('interest_expense', 0)
        
        cash_flow = self.financial_data.get('cash_flow', {})
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)
        
        # Calculate ratios
        debt_to_equity = total_debt / total_equity if total_equity else None
        debt_to_assets = total_debt / total_assets if total_assets else None
        
        interest_coverage = operating_income / interest_expense if interest_expense else None
        
        debt_service = interest_expense + (total_debt * 0.1)  # Assuming 10% principal repayment
        debt_service_coverage = operating_cash_flow / debt_service if debt_service else None
        
        return {
            'debt_to_equity': debt_to_equity,
            'debt_to_assets': debt_to_assets,
            'interest_coverage': interest_coverage,
            'debt_service_coverage': debt_service_coverage
        }
    
    def efficiency_ratios(self):
        """
        Calculate efficiency ratios.
        
        Returns:
            dict: Efficiency ratios
        """
        income_stmt = self.financial_data.get('income_statement')
        balance_sheet = self.financial_data.get('balance_sheet')
        
        if income_stmt is None or balance_sheet is None:
            return {
                'asset_turnover': None,
                'inventory_turnover': None,
                'receivables_turnover': None,
                'days_sales_outstanding': None,
                'days_inventory_outstanding': None,
                'days_payables_outstanding': None,
                'cash_conversion_cycle': None
            }
        
        # Extract required values
        revenue = income_stmt.get('revenue', 0)
        cost_of_goods_sold = income_stmt.get('cost_of_goods_sold', 0)
        
        total_assets = balance_sheet.get('total_assets', 0)
        inventory = balance_sheet.get('inventory', 0)
        accounts_receivable = balance_sheet.get('accounts_receivable', 0)
        accounts_payable = balance_sheet.get('accounts_payable', 0)
        
        # Calculate ratios
        asset_turnover = revenue / total_assets if total_assets else None
        
        inventory_turnover = cost_of_goods_sold / inventory if inventory else None
        days_inventory_outstanding = 365 / inventory_turnover if inventory_turnover else None
        
        receivables_turnover = revenue / accounts_receivable if accounts_receivable else None
        days_sales_outstanding = 365 / receivables_turnover if receivables_turnover else None
        
        payables_turnover = cost_of_goods_sold / accounts_payable if accounts_payable else None
        days_payables_outstanding = 365 / payables_turnover if payables_turnover else None
        
        cash_conversion_cycle = (days_inventory_outstanding or 0) + (days_sales_outstanding or 0) - (days_payables_outstanding or 0)
        
        return {
            'asset_turnover': asset_turnover,
            'inventory_turnover': inventory_turnover,
            'receivables_turnover': receivables_turnover,
            'days_sales_outstanding': days_sales_outstanding,
            'days_inventory_outstanding': days_inventory_outstanding,
            'days_payables_outstanding': days_payables_outstanding,
            'cash_conversion_cycle': cash_conversion_cycle
        }
    
    def valuation_ratios(self, market_data):
        """
        Calculate valuation ratios.
        
        Args:
            market_data (dict): Market data including price, shares outstanding, etc.
            
        Returns:
            dict: Valuation ratios
        """
        income_stmt = self.financial_data.get('income_statement')
        balance_sheet = self.financial_data.get('balance_sheet')
        cash_flow = self.financial_data.get('cash_flow', {})
        
        if income_stmt is None or balance_sheet is None or not market_data:
            return {
                'price_to_earnings': None,
                'price_to_book': None,
                'price_to_sales': None,
                'price_to_cash_flow': None,
                'enterprise_value_to_ebitda': None,
                'dividend_yield': None,
                'payout_ratio': None
            }
        
        # Extract required values
        net_income = income_stmt.get('net_income', 0)
        revenue = income_stmt.get('revenue', 0)
        ebitda = income_stmt.get('ebitda', 0)
        dividends_paid = cash_flow.get('dividends_paid', 0)
        
        total_equity = balance_sheet.get('total_equity', 0)
        total_debt = balance_sheet.get('total_debt', 0)
        cash_and_equivalents = balance_sheet.get('cash_and_equivalents', 0)
        
        price = market_data.get('price', 0)
        shares_outstanding = market_data.get('shares_outstanding', 0)
        
        # Calculate market values
        market_cap = price * shares_outstanding
        enterprise_value = market_cap + total_debt - cash_and_equivalents
        
        # Calculate ratios
        price_to_earnings = price / (net_income / shares_outstanding) if net_income else None
        price_to_book = price / (total_equity / shares_outstanding) if total_equity else None
        price_to_sales = price / (revenue / shares_outstanding) if revenue else None
        
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)
        price_to_cash_flow = price / (operating_cash_flow / shares_outstanding) if operating_cash_flow else None
        
        enterprise_value_to_ebitda = enterprise_value / ebitda if ebitda else None
        
        dividend_per_share = abs(dividends_paid) / shares_outstanding if shares_outstanding else 0
        dividend_yield = dividend_per_share / price if price else None
        
        payout_ratio = abs(dividends_paid) / net_income if net_income else None
        
        return {
            'price_to_earnings': price_to_earnings,
            'price_to_book': price_to_book,
            'price_to_sales': price_to_sales,
            'price_to_cash_flow': price_to_cash_flow,
            'enterprise_value_to_ebitda': enterprise_value_to_ebitda,
            'dividend_yield': dividend_yield,
            'payout_ratio': payout_ratio
        }
    
    def growth_ratios(self, historical_data, periods=5):
        """
        Calculate growth ratios.
        
        Args:
            historical_data (dict): Historical financial data
            periods (int): Number of periods to analyze
            
        Returns:
            dict: Growth ratios
        """
        if not historical_data:
            return {
                'revenue_growth': None,
                'earnings_growth': None,
                'dividend_growth': None,
                'book_value_growth': None,
                'free_cash_flow_growth': None
            }
        
        # Extract time series data
        revenue_series = historical_data.get('revenue', [])
        earnings_series = historical_data.get('net_income', [])
        dividend_series = historical_data.get('dividends', [])
        book_value_series = historical_data.get('book_value', [])
        fcf_series = historical_data.get('free_cash_flow', [])
        
        # Calculate compound annual growth rates
        def calculate_cagr(series, periods):
            if len(series) < periods or series[0] <= 0 or series[-1] <= 0:
                return None
            return (series[-1] / series[0]) ** (1 / periods) - 1
        
        revenue_growth = calculate_cagr(revenue_series[-periods:], periods)
        earnings_growth = calculate_cagr(earnings_series[-periods:], periods)
        dividend_growth = calculate_cagr(dividend_series[-periods:], periods)
        book_value_growth = calculate_cagr(book_value_series[-periods:], periods)
        fcf_growth = calculate_cagr(fcf_series[-periods:], periods)
        
        return {
            'revenue_growth': revenue_growth,
            'earnings_growth': earnings_growth,
            'dividend_growth': dividend_growth,
            'book_value_growth': book_value_growth,
            'free_cash_flow_growth': fcf_growth
        }
    
    def dividend_analysis(self, historical_data, market_data):
        """
        Analyze dividend history and sustainability.
        
        Args:
            historical_data (dict): Historical financial data
            market_data (dict): Current market data
            
        Returns:
            dict: Dividend analysis
        """
        if not historical_data or not market_data:
            return {
                'current_dividend_yield': None,
                'dividend_growth_rate': None,
                'payout_ratio': None,
                'dividend_coverage': None,
                'years_of_dividend_growth': None,
                'dividend_consistency': None,
                'dividend_sustainability_score': None
            }
        
        # Extract data
        dividend_series = historical_data.get('dividends', [])
        earnings_series = historical_data.get('net_income', [])
        fcf_series = historical_data.get('free_cash_flow', [])
        
        current_dividend = dividend_series[-1] if dividend_series else 0
        current_earnings = earnings_series[-1] if earnings_series else 0
        current_fcf = fcf_series[-1] if fcf_series else 0
        
        price = market_data.get('price', 0)
        shares_outstanding = market_data.get('shares_outstanding', 0)
        
        # Calculate metrics
        dividend_per_share = current_dividend / shares_outstanding if shares_outstanding else 0
        current_dividend_yield = dividend_per_share / price if price else None
        
        # Calculate dividend growth rate (5-year CAGR)
        periods = min(5, len(dividend_series))
        if periods >= 2 and dividend_series[-periods] > 0:
            dividend_growth_rate = (dividend_series[-1] / dividend_series[-periods]) ** (1 / periods) - 1
        else:
            dividend_growth_rate = None
        
        # Calculate payout ratios
        payout_ratio = current_dividend / current_earnings if current_earnings else None
        fcf_payout_ratio = current_dividend / current_fcf if current_fcf else None
        
        # Dividend coverage
        dividend_coverage = current_earnings / current_dividend if current_dividend else None
        
        # Years of dividend growth
        years_of_growth = 0
        for i in range(1, len(dividend_series)):
            if dividend_series[i] > dividend_series[i-1]:
                years_of_growth += 1
            else:
                break
        
        # Dividend consistency (percentage of years with increasing dividends)
        if len(dividend_series) > 1:
            increases = sum(1 for i in range(1, len(dividend_series)) if dividend_series[i] > dividend_series[i-1])
            dividend_consistency = increases / (len(dividend_series) - 1)
        else:
            dividend_consistency = None
        
        # Dividend sustainability score (0-100)
        sustainability_score = None
        if payout_ratio is not None and dividend_growth_rate is not None and dividend_consistency is not None:
            # Lower payout ratio is better (max 40 points)
            payout_score = max(0, 40 - (payout_ratio * 100) * 0.4) if payout_ratio <= 1 else 0
            
            # Higher growth rate is better (max 30 points)
            growth_score = min(30, dividend_growth_rate * 100 * 3) if dividend_growth_rate > 0 else 0
            
            # Higher consistency is better (max 30 points)
            consistency_score = dividend_consistency * 30 if dividend_consistency is not None else 0
            
            sustainability_score = payout_score + growth_score + consistency_score
        
        return {
            'current_dividend_yield': current_dividend_yield,
            'dividend_growth_rate': dividend_growth_rate,
            'payout_ratio': payout_ratio,
            'fcf_payout_ratio': fcf_payout_ratio,
            'dividend_coverage': dividend_coverage,
            'years_of_dividend_growth': years_of_growth,
            'dividend_consistency': dividend_consistency,
            'dividend_sustainability_score': sustainability_score
        }
    
    def calculate_all_ratios(self, market_data=None, historical_data=None):
        """
        Calculate all financial ratios.
        
        Args:
            market_data (dict): Current market data
            historical_data (dict): Historical financial data
            
        Returns:
            dict: All financial ratios
        """
        ratios = {
            'profitability': self.profitability_ratios(),
            'liquidity': self.liquidity_ratios(),
            'solvency': self.solvency_ratios(),
            'efficiency': self.efficiency_ratios()
        }
        
        if market_data:
            ratios['valuation'] = self.valuation_ratios(market_data)
        
        if historical_data:
            ratios['growth'] = self.growth_ratios(historical_data)
            
            if market_data:
                ratios['dividend'] = self.dividend_analysis(historical_data, market_data)
        
        return ratios
    
    def interpret_ratios(self, ratios, sector_averages=None):
        """
        Interpret financial ratios and provide insights.
        
        Args:
            ratios (dict): Financial ratios
            sector_averages (dict): Sector average ratios for comparison
            
        Returns:
            dict: Interpretation and insights
        """
        insights = {}
        
        # Profitability insights
        if 'profitability' in ratios:
            prof = ratios['profitability']
            prof_insights = []
            
            if prof['return_on_equity'] is not None:
                if prof['return_on_equity'] > 0.15:
                    prof_insights.append("Strong return on equity indicates efficient use of shareholder capital.")
                elif prof['return_on_equity'] < 0.05:
                    prof_insights.append("Low return on equity may indicate inefficient use of capital.")
            
            if prof['net_profit_margin'] is not None:
                if prof['net_profit_margin'] > 0.2:
                    prof_insights.append("High profit margin indicates strong pricing power and cost control.")
                elif prof['net_profit_margin'] < 0.05:
                    prof_insights.append("Low profit margin may indicate competitive pressures or cost issues.")
            
            insights['profitability'] = prof_insights
        
        # Liquidity insights
        if 'liquidity' in ratios:
            liq = ratios['liquidity']
            liq_insights = []
            
            if liq['current_ratio'] is not None:
                if liq['current_ratio'] < 1:
                    liq_insights.append("Current ratio below 1 indicates potential short-term liquidity issues.")
                elif liq['current_ratio'] > 3:
                    liq_insights.append("High current ratio may indicate inefficient use of assets.")
            
            insights['liquidity'] = liq_insights
        
        # Solvency insights
        if 'solvency' in ratios:
            solv = ratios['solvency']
            solv_insights = []
            
            if solv['debt_to_equity'] is not None:
                if solv['debt_to_equity'] > 2:
                    solv_insights.append("High debt-to-equity ratio indicates significant financial leverage.")
                elif solv['debt_to_equity'] < 0.3:
                    solv_insights.append("Low debt-to-equity ratio indicates conservative financial structure.")
            
            insights['solvency'] = solv_insights
        
        # Valuation insights
        if 'valuation' in ratios:
            val = ratios['valuation']
            val_insights = []
            
            if val['price_to_earnings'] is not None:
                if val['price_to_earnings'] > 25:
                    val_insights.append("High P/E ratio indicates market expects strong future growth.")
                elif val['price_to_earnings'] < 10:
                    val_insights.append("Low P/E ratio may indicate undervaluation or market concerns.")
            
            insights['valuation'] = val_insights
        
        # Compare with sector averages if available
        if sector_averages:
            comparison = {}
            
            for category, metrics in ratios.items():
                if category in sector_averages:
                    category_comparison = {}
                    
                    for metric, value in metrics.items():
                        if metric in sector_averages[category] and value is not None:
                            sector_value = sector_averages[category][metric]
                            if sector_value is not None:
                                difference = value - sector_value
                                percent_diff = difference / sector_value if sector_value != 0 else None
                                
                                category_comparison[metric] = {
                                    'company': value,
                                    'sector': sector_value,
                                    'difference': difference,
                                    'percent_difference': percent_diff
                                }
                    
                    comparison[category] = category_comparison
            
            insights['sector_comparison'] = comparison
        
        return insights