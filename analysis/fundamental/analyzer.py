"""
Fundamental Analysis Module for Saudi Stock Market (Tasi)

This module provides tools for fundamental analysis of Saudi stocks,
including financial ratios, company performance metrics, and sector analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

class FundamentalAnalyzer:
    """
    A class for performing fundamental analysis on Saudi stocks.
    
    This analyzer evaluates companies based on financial statements,
    key performance indicators, and sector benchmarks.
    """
    
    def __init__(self, data_source=None):
        """
        Initialize the fundamental analyzer.

        Args:
            data_source: Source for financial data (API, database, etc.)
        """
        self.data_source = data_source
        self.financial_data = {}
        self._cache: Dict[str, Any] = {}

    def _get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """جلب بيانات السهم من yfinance مع تخزين مؤقت."""
        if ticker in self._cache:
            return self._cache[ticker]
        if not YFINANCE_AVAILABLE:
            return {}
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            self._cache[ticker] = {'info': info, 'ticker': t}
            return self._cache[ticker]
        except Exception:
            return {}

    def load_financial_statements(self, ticker: str, period: str = 'annual') -> Dict:
        """
        جلب القوائم المالية للشركة عبر yfinance.
        """
        cached = self._get_ticker_info(ticker)
        t = cached.get('ticker')
        result = {'income_statement': None, 'balance_sheet': None, 'cash_flow': None}
        if t is None:
            return result
        try:
            if period == 'annual':
                income = t.financials
                balance = t.balance_sheet
                cashflow = t.cashflow
            else:
                income = t.quarterly_financials
                balance = t.quarterly_balance_sheet
                cashflow = t.quarterly_cashflow

            def df_to_dict(df):
                if df is None or (hasattr(df, 'empty') and df.empty):
                    return {}
                return {str(col.date()): df[col].dropna().to_dict() for col in df.columns}

            result['income_statement'] = df_to_dict(income)
            result['balance_sheet'] = df_to_dict(balance)
            result['cash_flow'] = df_to_dict(cashflow)
        except Exception:
            pass
        return result

    def calculate_financial_ratios(self, ticker: str) -> Dict:
        """
        حساب النسب المالية الرئيسية عبر yfinance.
        """
        info = self._get_ticker_info(ticker).get('info', {})

        def safe(key):
            v = info.get(key)
            return round(float(v), 4) if v is not None else None

        # حساب نمو الإيرادات من القوائم المالية
        revenue_growth = safe('revenueGrowth')
        earnings_growth = safe('earningsGrowth')

        return {
            'profitability': {
                'roe': safe('returnOnEquity'),
                'roa': safe('returnOnAssets'),
                'profit_margin': safe('profitMargins'),
                'operating_margin': safe('operatingMargins'),
            },
            'valuation': {
                'pe_ratio': safe('trailingPE'),
                'pb_ratio': safe('priceToBook'),
                'dividend_yield': safe('dividendYield'),
                'peg_ratio': safe('pegRatio'),
            },
            'liquidity': {
                'current_ratio': safe('currentRatio'),
                'quick_ratio': safe('quickRatio'),
                'debt_to_equity': safe('debtToEquity'),
            },
            'growth': {
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'dividend_growth': safe('fiveYearAvgDividendYield'),
            }
        }
    
    def sector_comparison(self, ticker, metrics=None):
        """
        Compare company metrics against sector averages.
        
        Args:
            ticker (str): Stock ticker symbol
            metrics (list): Specific metrics to compare
            
        Returns:
            dict: Comparison results
        """
        if metrics is None:
            metrics = ['pe_ratio', 'roe', 'profit_margin']

        info = self._get_ticker_info(ticker).get('info', {})
        mapping = {
            'pe_ratio': 'trailingPE', 'roe': 'returnOnEquity',
            'profit_margin': 'profitMargins', 'pb_ratio': 'priceToBook',
        }
        company_values = {}
        for m in metrics:
            key = mapping.get(m, m)
            v = info.get(key)
            company_values[m] = round(float(v), 4) if v is not None else None

        return {
            'company_values': company_values,
            'sector_averages': {},   # يحتاج إلى مصدر بيانات القطاع
            'percentile_ranks': {}
        }

    def dividend_analysis(self, ticker: str, years: int = 5) -> Dict:
        """تحليل توزيعات الأرباح عبر yfinance."""
        info = self._get_ticker_info(ticker).get('info', {})
        t = self._get_ticker_info(ticker).get('ticker')

        dividend_history = []
        if t is not None and YFINANCE_AVAILABLE:
            try:
                divs = t.dividends
                if not divs.empty:
                    dividend_history = [
                        {'date': str(d.date()), 'amount': float(v)}
                        for d, v in divs.items()
                    ][-years * 4:]  # آخر years سنوات تقريباً
            except Exception:
                pass

        payout = info.get('payoutRatio')
        return {
            'dividend_history': dividend_history,
            'payout_ratio': round(float(payout), 4) if payout else None,
            'dividend_yield': round(float(info.get('dividendYield', 0)), 4),
            'dividend_growth_rate': None,
            'sustainability_score': None
        }

    def management_efficiency(self, ticker: str) -> Dict:
        """قياس كفاءة الإدارة عبر yfinance."""
        info = self._get_ticker_info(ticker).get('info', {})

        def safe(key):
            v = info.get(key)
            return round(float(v), 4) if v is not None else None

        return {
            'asset_turnover': safe('assetTurnover') if 'assetTurnover' in info else None,
            'inventory_turnover': None,
            'receivables_turnover': None,
            'capital_efficiency': safe('returnOnEquity'),
            'revenue_per_employee': safe('revenuePerShare'),
        }

    def intrinsic_value(self, ticker: str, model: str = 'pe') -> Dict:
        """
        تقدير القيمة الذاتية للسهم.
        يستخدم نموذج PE البسيط عند غياب بيانات DCF.
        """
        info = self._get_ticker_info(ticker).get('info', {})

        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        eps = info.get('trailingEps')
        pe = info.get('trailingPE')
        growth = info.get('earningsGrowth', 0.1) or 0.1

        estimated_value = None
        margin_of_safety = None

        if eps and pe:
            # Graham Number تقديري
            try:
                import math
                estimated_value = round(math.sqrt(22.5 * abs(eps) * abs(info.get('bookValue', eps))), 2)
                if current_price and estimated_value:
                    margin_of_safety = round((estimated_value - current_price) / estimated_value * 100, 2)
            except Exception:
                pass

        return {
            'estimated_value': estimated_value,
            'current_price': current_price,
            'margin_of_safety': margin_of_safety,
            'assumptions': {
                'growth_rate': round(float(growth), 4) if growth else None,
                'discount_rate': 0.10,
                'terminal_value': None
            }
        }
    
    def generate_report(self, ticker):
        """
        Generate a comprehensive fundamental analysis report.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Complete analysis report
        """
        # Collect all analysis components
        report = {
            'ticker': ticker,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'financial_ratios': self.calculate_financial_ratios(ticker),
            'sector_comparison': self.sector_comparison(ticker),
            'dividend_analysis': self.dividend_analysis(ticker),
            'management_efficiency': self.management_efficiency(ticker),
            'valuation': self.intrinsic_value(ticker)
        }
        
        # Add recommendation based on analysis
        report['recommendation'] = self._generate_recommendation(report)
        
        return report
    
    def _generate_recommendation(self, report):
        """
        Generate investment recommendation based on analysis.
        
        Args:
            report (dict): Analysis report
            
        Returns:
            dict: Recommendation details
        """
        # Placeholder for actual implementation
        score = 0
        factors = []
        ratios = report.get('financial_ratios', {})
        valuation = report.get('valuation', {})

        prof = ratios.get('profitability', {})
        val = ratios.get('valuation', {})
        liq = ratios.get('liquidity', {})

        # نقاط الربحية
        roe = prof.get('roe')
        if roe is not None:
            if roe > 0.15:
                score += 2; factors.append(f'ROE مرتفع ({roe:.1%})')
            elif roe < 0:
                score -= 2; factors.append(f'ROE سلبي ({roe:.1%})')

        # نقاط التقييم
        pe = val.get('pe_ratio')
        if pe is not None and pe > 0:
            if pe < 15:
                score += 2; factors.append(f'PE منخفض ({pe:.1f}x)')
            elif pe > 30:
                score -= 1; factors.append(f'PE مرتفع ({pe:.1f}x)')

        # نقاط هامش الأمان
        mos = valuation.get('margin_of_safety')
        if mos is not None:
            if mos > 20:
                score += 2; factors.append(f'هامش أمان إيجابي ({mos:.1f}%)')
            elif mos < -20:
                score -= 2; factors.append(f'السهم مبالغ في تقييمه ({mos:.1f}%)')

        # نقاط السيولة
        cr = liq.get('current_ratio')
        if cr is not None:
            if cr >= 1.5:
                score += 1; factors.append(f'نسبة سيولة جيدة ({cr:.1f})')
            elif cr < 1:
                score -= 1; factors.append(f'نسبة سيولة منخفضة ({cr:.1f})')

        # تحديد التوصية
        if score >= 4:
            action, confidence = 'buy', min(85, 50 + score * 5)
        elif score <= -2:
            action, confidence = 'sell', min(80, 50 + abs(score) * 5)
        else:
            action, confidence = 'hold', 50

        return {
            'action': action,
            'confidence': confidence,
            'key_factors': factors,
            'risk_assessment': 'low' if liq.get('debt_to_equity', 1) < 0.5 else 'medium',
            'time_horizon': 'medium_term'
        }

    # ---- واجهة التكامل مع system_integration.py ----

    # المقاييس المتاحة
    _AVAILABLE_RATIOS = ['PE', 'PB', 'ROE', 'ROA', 'profit_margin', 'operating_margin',
                         'current_ratio', 'quick_ratio', 'debt_to_equity']
    _AVAILABLE_VALUATIONS = ['pe_ratio', 'pb_ratio', 'dividend_yield', 'peg_ratio', 'market_cap']
    _AVAILABLE_STATEMENTS = ['revenue', 'net_income', 'total_assets', 'total_liabilities',
                              'equity', 'operating_cash_flow', 'free_cash_flow', 'EPS']

    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """جلب البيانات المالية للشركة عبر yfinance."""
        if not YFINANCE_AVAILABLE:
            return {'symbol': symbol, 'info': {}, 'financials': {}}
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            self._last_update = {symbol: datetime.now().isoformat()}
            return {'symbol': symbol, 'info': info, 'ticker': ticker}
        except Exception:
            return {'symbol': symbol, 'info': {}, 'ticker': None}

    def get_available_ratios(self) -> List[str]:
        return self._AVAILABLE_RATIOS

    def get_available_valuations(self) -> List[str]:
        return self._AVAILABLE_VALUATIONS

    def get_available_statement_items(self) -> List[str]:
        return self._AVAILABLE_STATEMENTS

    def calculate_ratios(self, financial_data: Dict, metrics: List[str]) -> Dict[str, Any]:
        """حساب النسب المالية من بيانات yfinance."""
        info = financial_data.get('info', {})
        result = {}
        mapping = {
            'PE': 'trailingPE', 'PB': 'priceToBook', 'ROE': 'returnOnEquity',
            'ROA': 'returnOnAssets', 'profit_margin': 'profitMargins',
            'operating_margin': 'operatingMargins', 'current_ratio': 'currentRatio',
            'quick_ratio': 'quickRatio', 'debt_to_equity': 'debtToEquity'
        }
        for m in metrics:
            key = mapping.get(m, m)
            val = info.get(key)
            result[m] = round(float(val), 4) if val is not None else None
        return result

    def calculate_valuations(self, financial_data: Dict, metrics: List[str]) -> Dict[str, Any]:
        """حساب مقاييس التقييم من بيانات yfinance."""
        info = financial_data.get('info', {})
        result = {}
        mapping = {
            'pe_ratio': 'trailingPE', 'pb_ratio': 'priceToBook',
            'dividend_yield': 'dividendYield', 'peg_ratio': 'pegRatio',
            'market_cap': 'marketCap'
        }
        for m in metrics:
            key = mapping.get(m, m)
            val = info.get(key)
            result[m] = round(float(val), 4) if val is not None else None
        return result

    def get_statement_items(self, financial_data: Dict, metrics: List[str]) -> Dict[str, Any]:
        """استخراج بنود القوائم المالية من yfinance."""
        info = financial_data.get('info', {})
        result = {}
        mapping = {
            'revenue': 'totalRevenue', 'net_income': 'netIncomeToCommon',
            'total_assets': 'totalAssets', 'total_liabilities': 'totalDebt',
            'equity': 'bookValue', 'operating_cash_flow': 'operatingCashflow',
            'free_cash_flow': 'freeCashflow', 'EPS': 'trailingEps'
        }
        for m in metrics:
            key = mapping.get(m, m)
            val = info.get(key)
            result[m] = val
        return result

    def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """جلب ملف الشركة من yfinance."""
        if not YFINANCE_AVAILABLE:
            return {'symbol': symbol}
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'employees': info.get('fullTimeEmployees'),
                'country': info.get('country', '')
            }
        except Exception:
            return {'symbol': symbol}

    def get_last_update_time(self, symbol: str = '') -> str:
        """إعادة وقت آخر تحديث."""
        if hasattr(self, '_last_update') and symbol in self._last_update:
            return self._last_update[symbol]
        return datetime.now().isoformat()