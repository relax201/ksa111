"""
Stock Recommendation Engine for Saudi Stock Market (Tasi)

This module combines technical and fundamental analysis to generate
comprehensive investment recommendations for Saudi stocks.
"""

import pandas as pd
import numpy as np
from datetime import datetime

from analysis.technical.analyzer import TechnicalAnalyzer
from analysis.fundamental.analyzer import FundamentalAnalyzer
from data.collectors.market_data_collector import MarketDataCollector

try:
    from integration.config import SAHMAK_API_KEY
except ImportError:
    SAHMAK_API_KEY = None

class RecommendationEngine:
    """
    A recommendation engine that combines multiple analysis methods
    to generate investment recommendations for Saudi stocks.
    """
    
    def __init__(self, config=None):
        """
        Initialize the recommendation engine.
        
        Args:
            config (dict): Configuration parameters for the engine
        """
        self.config = config or {}
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        
        # Default weights for different analysis components
        self.weights = self.config.get('weights', {
            'technical': 0.4,
            'fundamental': 0.4,
            'market_sentiment': 0.1,
            'economic_indicators': 0.1
        })
        self.market_data = MarketDataCollector(api_key=SAHMAK_API_KEY)
    
    def generate_recommendation(self, ticker, time_horizon='medium'):
        """
        Generate a comprehensive investment recommendation.
        
        Args:
            ticker (str): Stock ticker symbol
            time_horizon (str): 'short', 'medium', or 'long'
            
        Returns:
            dict: Recommendation details
        """
        # Fetch historical data for technical analysis
        historical_data = self.market_data.get_historical_prices(ticker, period='daily')
        if historical_data is None or historical_data.empty:
            raise ValueError(f"No historical data for {ticker}")
            
        technical_analysis = self.technical_analyzer.analyze(historical_data)
        fundamental_analysis = self.fundamental_analyzer.generate_report(ticker)
        market_sentiment = self._analyze_market_sentiment(ticker)
        economic_indicators = self._analyze_economic_indicators()
        
        # Calculate weighted score
        scores = {
            'technical': self._score_technical(technical_analysis, time_horizon),
            'fundamental': self._score_fundamental(fundamental_analysis, time_horizon),
            'market_sentiment': market_sentiment['score'],
            'economic_indicators': economic_indicators['score']
        }
        
        weighted_score = sum(scores[key] * self.weights[key] for key in scores)
        
        # Determine recommendation based on score
        recommendation = self._determine_recommendation(weighted_score)
        
        # Compile detailed report
        return {
            'ticker': ticker,
            'recommendation': recommendation,
            'score': weighted_score,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'time_horizon': time_horizon,
            'components': {
                'technical_analysis': technical_analysis,
                'fundamental_analysis': fundamental_analysis,
                'market_sentiment': market_sentiment,
                'economic_indicators': economic_indicators
            },
            'explanation': self._generate_explanation(ticker, scores, recommendation),
            'risk_assessment': self._assess_risk(ticker, scores)
        }
    
    def _score_technical(self, analysis, time_horizon):
        """
        تحويل نتائج التحليل الفني إلى نقاط موحدة (0-1).
        """
        if not analysis or analysis.get('status') == 'error':
            return 0.5

        assessment = analysis.get('assessment', {})
        recommendation = assessment.get('recommendation', 'hold')
        confidence = assessment.get('confidence', 50) / 100.0

        trend = analysis.get('trend', {})
        momentum = analysis.get('momentum', {})

        score = 0.5  # نقطة البداية المحايدة

        # التوصية الأساسية
        if recommendation == 'buy':
            score += 0.2 * confidence
        elif recommendation == 'sell':
            score -= 0.2 * confidence

        # تعديل حسب الاتجاه
        horizon_map = {'short': 'short_term', 'medium': 'medium_term', 'long': 'long_term'}
        horizon_key = horizon_map.get(time_horizon, 'medium_term')
        trend_val = trend.get(horizon_key, 'neutral')
        if trend_val == 'bullish':
            score += 0.1
        elif trend_val == 'bearish':
            score -= 0.1

        # تعديل حسب الزخم
        direction = momentum.get('direction', 'neutral')
        if direction == 'positive':
            score += 0.05
        elif direction == 'negative':
            score -= 0.05
        elif direction == 'overbought':
            score -= 0.05  # تحذير من التشبع
        elif direction == 'oversold':
            score += 0.05  # فرصة محتملة

        return max(0.0, min(1.0, score))

    def _score_fundamental(self, analysis, time_horizon):
        """
        تحويل نتائج التحليل الأساسي إلى نقاط موحدة (0-1).
        """
        if not analysis:
            return 0.5

        recommendation = analysis.get('recommendation', {})
        action = recommendation.get('action')
        confidence = (recommendation.get('confidence') or 50) / 100.0

        score = 0.5

        if action == 'buy':
            score += 0.3 * confidence
        elif action == 'sell':
            score -= 0.3 * confidence

        # تعديل حسب هامش الأمان
        valuation = analysis.get('valuation', {})
        mos = valuation.get('margin_of_safety')
        if mos is not None:
            score += min(0.15, max(-0.15, mos / 100))

        # تعديل حسب الربحية
        ratios = analysis.get('financial_ratios', {})
        roe = ratios.get('profitability', {}).get('roe')
        if roe is not None:
            if roe > 0.20:
                score += 0.05
            elif roe < 0:
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _analyze_market_sentiment(self, ticker):
        """تحليل مشاعر السوق من المصادر المتاحة."""
        # محاولة جلب أخبار من yfinance
        score = 0.5
        try:
            import yfinance as yf
            t = yf.Ticker(ticker)
            news = t.news or []
            if news:
                # تقدير المشاعر بناءً على عناوين الأخبار (مبسّط)
                positive_words = ['gain', 'rise', 'profit', 'growth', 'beat', 'ارتفع', 'نمو', 'ربح']
                negative_words = ['loss', 'fall', 'decline', 'miss', 'انخفض', 'خسارة', 'تراجع']
                pos = sum(1 for n in news if any(w in n.get('title', '').lower() for w in positive_words))
                neg = sum(1 for n in news if any(w in n.get('title', '').lower() for w in negative_words))
                total = pos + neg
                if total > 0:
                    score = 0.3 + 0.4 * (pos / total)
        except Exception:
            pass

        return {
            'score': score,
            'news_sentiment': score,
            'social_media_sentiment': None,
            'institutional_activity': None
        }

    def _analyze_economic_indicators(self):
        """تحليل المؤشرات الاقتصادية المتاحة."""
        # قيم افتراضية محايدة - يمكن ربطها بـ API اقتصادي لاحقاً
        return {
            'score': 0.5,
            'interest_rates': None,
            'gdp_growth': None,
            'inflation': None,
            'sector_performance': None
        }
    
    def _determine_recommendation(self, score):
        """
        Determine recommendation based on overall score.
        
        Args:
            score (float): Overall weighted score
            
        Returns:
            str: Recommendation ('strong_buy', 'buy', 'hold', 'sell', 'strong_sell')
        """
        if score >= 0.8:
            return 'strong_buy'
        elif score >= 0.6:
            return 'buy'
        elif score >= 0.4:
            return 'hold'
        elif score >= 0.2:
            return 'sell'
        else:
            return 'strong_sell'
    
    def _generate_explanation(self, ticker, scores, recommendation):
        """
        Generate human-readable explanation for the recommendation.
        
        Args:
            ticker (str): Stock ticker symbol
            scores (dict): Component scores
            recommendation (str): Final recommendation
            
        Returns:
            str: Explanation text
        """
        rec_map = {
            'strong_buy': 'شراء قوي', 'buy': 'شراء',
            'hold': 'انتظار', 'sell': 'بيع', 'strong_sell': 'بيع قوي'
        }
        parts = []
        tech_score = scores.get('technical', 0.5)
        fund_score = scores.get('fundamental', 0.5)

        if tech_score > 0.6:
            parts.append('إشارات فنية إيجابية')
        elif tech_score < 0.4:
            parts.append('إشارات فنية سلبية')
        else:
            parts.append('إشارات فنية محايدة')

        if fund_score > 0.6:
            parts.append('أساسيات قوية')
        elif fund_score < 0.4:
            parts.append('أساسيات ضعيفة')
        else:
            parts.append('أساسيات معتدلة')

        rec_ar = rec_map.get(recommendation, recommendation)
        return f"توصية {rec_ar} للسهم {ticker} بناءً على: {' و'.join(parts)}."

    def _assess_risk(self, ticker, scores):
        """تقييم مستوى المخاطرة بناءً على التقلب والمؤشرات."""
        risks = []
        risk_score = 0

        tech = scores.get('technical', 0.5)
        fund = scores.get('fundamental', 0.5)

        # تقلب عالٍ إذا كانت الإشارات متضاربة
        if abs(tech - fund) > 0.3:
            risk_score += 1
            risks.append('تضارب بين الإشارات الفنية والأساسية')

        if tech < 0.3 or fund < 0.3:
            risk_score += 1
            risks.append('مؤشرات ضعيفة')

        # محاولة جلب تقلب السهم
        try:
            import yfinance as yf
            t = yf.Ticker(ticker)
            info = t.info or {}
            beta = info.get('beta')
            if beta is not None:
                if beta > 1.5:
                    risk_score += 2
                    risks.append(f'Beta مرتفع ({beta:.2f})')
                elif beta > 1.0:
                    risk_score += 1
        except Exception:
            pass

        if risk_score >= 3:
            risk_level = 'high'
        elif risk_score >= 1:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'volatility': None,
            'liquidity': None,
            'specific_risks': risks
        }
    
    def batch_recommendations(self, tickers, time_horizon='medium'):
        """
        Generate recommendations for multiple stocks.
        
        Args:
            tickers (list): List of stock ticker symbols
            time_horizon (str): Time horizon for recommendations
            
        Returns:
            dict: Recommendations for each ticker
        """
        recommendations = {}
        for ticker in tickers:
            recommendations[ticker] = self.generate_recommendation(ticker, time_horizon)
        return recommendations
    
    def get_recommendations(self, risk_profile='moderate', investment_horizon='medium', 
                           sectors=None, exclude_symbols=None, max_results=10):
        """
        Generate a list of top stock recommendations based on live market data.
        """
        # Fetch active stocks using market volume as a proxy for tradable universe
        stocks_data = self.market_data.get_most_active(limit=max_results * 2, by='volume')
        
        universe = []
        for s in stocks_data:
            symbol = s.get('symbol')
            if symbol and (not exclude_symbols or symbol not in exclude_symbols):
                universe.append(symbol)
                
        if not universe:
            # Fallback list if API limits/fails
            universe = ["2222", "1120", "2010", "1180", "2350"]
            
        results = []
        for ticker in universe:
            try:
                rec = self.generate_recommendation(ticker, investment_horizon)
                # Filter by risk profile loosely via score threshold mapping
                if risk_profile == 'conservative' and rec['score'] < 0.6:
                    continue
                results.append(rec)
            except Exception as e:
                continue
                
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def portfolio_recommendations(self, holdings, time_horizon='medium'):
        """
        Generate recommendations for a portfolio.
        
        Args:
            holdings (dict): Current portfolio holdings {ticker: shares}
            time_horizon (str): Time horizon for recommendations
            
        Returns:
            dict: Portfolio analysis and recommendations
        """
        # Get recommendations for each holding
        stock_recommendations = {ticker: self.generate_recommendation(ticker, time_horizon) 
                               for ticker in holdings}
        
        # Analyze portfolio composition and suggest adjustments
        # Placeholder for actual implementation
        return {
            'holdings_analysis': stock_recommendations,
            'portfolio_score': None,
            'suggested_actions': [],
            'rebalancing_recommendations': None,
            'risk_assessment': None
        }