"""
Stock Screener Module for Saudi Stock Market (Tasi)

This module provides tools for screening Saudi stocks based on
technical, fundamental, and other criteria.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class StockScreener:
    """
    A class for screening Saudi stocks based on various criteria.
    """
    
    def __init__(self, data_source=None):
        """
        Initialize the stock screener.
        
        Args:
            data_source: Source for stock data
        """
        self.data_source = data_source
        self.stock_data = {}
    
    def load_stock_data(self, tickers=None):
        """
        Load stock data for screening.
        
        Args:
            tickers (list): List of stock tickers to load
            
        Returns:
            dict: Loaded stock data
        """
        # This would connect to the data source and retrieve data
        # For now, return a placeholder
        self.stock_data = {}
        return self.stock_data
    
    def screen_by_price(self, min_price=None, max_price=None):
        """
        Screen stocks by price range.
        
        Args:
            min_price (float): Minimum price
            max_price (float): Maximum price
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            price = data.get('price')
            
            if price is None:
                continue
            
            if min_price is not None and price < min_price:
                continue
            
            if max_price is not None and price > max_price:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_market_cap(self, min_cap=None, max_cap=None):
        """
        Screen stocks by market capitalization.
        
        Args:
            min_cap (float): Minimum market cap
            max_cap (float): Maximum market cap
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            market_cap = data.get('market_cap')
            
            if market_cap is None:
                continue
            
            if min_cap is not None and market_cap < min_cap:
                continue
            
            if max_cap is not None and market_cap > max_cap:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_sector(self, sectors):
        """
        Screen stocks by sector.
        
        Args:
            sectors (list): List of sectors to include
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            sector = data.get('sector')
            
            if sector is None:
                continue
            
            if sector in sectors:
                results.append(ticker)
        
        return results
    
    def screen_by_pe_ratio(self, min_pe=None, max_pe=None):
        """
        Screen stocks by P/E ratio.
        
        Args:
            min_pe (float): Minimum P/E ratio
            max_pe (float): Maximum P/E ratio
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            pe_ratio = data.get('pe_ratio')
            
            if pe_ratio is None or pe_ratio <= 0:
                continue
            
            if min_pe is not None and pe_ratio < min_pe:
                continue
            
            if max_pe is not None and pe_ratio > max_pe:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_pb_ratio(self, min_pb=None, max_pb=None):
        """
        Screen stocks by P/B ratio.
        
        Args:
            min_pb (float): Minimum P/B ratio
            max_pb (float): Maximum P/B ratio
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            pb_ratio = data.get('pb_ratio')
            
            if pb_ratio is None or pb_ratio <= 0:
                continue
            
            if min_pb is not None and pb_ratio < min_pb:
                continue
            
            if max_pb is not None and pb_ratio > max_pb:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_dividend_yield(self, min_yield=None, max_yield=None):
        """
        Screen stocks by dividend yield.
        
        Args:
            min_yield (float): Minimum dividend yield
            max_yield (float): Maximum dividend yield
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            dividend_yield = data.get('dividend_yield')
            
            if dividend_yield is None:
                continue
            
            if min_yield is not None and dividend_yield < min_yield:
                continue
            
            if max_yield is not None and dividend_yield > max_yield:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_roe(self, min_roe=None):
        """
        Screen stocks by Return on Equity.
        
        Args:
            min_roe (float): Minimum ROE
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            roe = data.get('roe')
            
            if roe is None:
                continue
            
            if min_roe is not None and roe < min_roe:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_debt_to_equity(self, max_ratio=None):
        """
        Screen stocks by Debt to Equity ratio.
        
        Args:
            max_ratio (float): Maximum Debt to Equity ratio
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            debt_to_equity = data.get('debt_to_equity')
            
            if debt_to_equity is None:
                continue
            
            if max_ratio is not None and debt_to_equity > max_ratio:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_revenue_growth(self, min_growth=None):
        """
        Screen stocks by revenue growth rate.
        
        Args:
            min_growth (float): Minimum revenue growth rate
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            revenue_growth = data.get('revenue_growth')
            
            if revenue_growth is None:
                continue
            
            if min_growth is not None and revenue_growth < min_growth:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_earnings_growth(self, min_growth=None):
        """
        Screen stocks by earnings growth rate.
        
        Args:
            min_growth (float): Minimum earnings growth rate
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            earnings_growth = data.get('earnings_growth')
            
            if earnings_growth is None:
                continue
            
            if min_growth is not None and earnings_growth < min_growth:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_rsi(self, min_rsi=None, max_rsi=None):
        """
        Screen stocks by RSI (Relative Strength Index).
        
        Args:
            min_rsi (float): Minimum RSI value
            max_rsi (float): Maximum RSI value
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            rsi = data.get('rsi')
            
            if rsi is None:
                continue
            
            if min_rsi is not None and rsi < min_rsi:
                continue
            
            if max_rsi is not None and rsi > max_rsi:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_moving_average(self, ma_type='sma', period=50, relation='above'):
        """
        Screen stocks by relation to moving average.
        
        Args:
            ma_type (str): 'sma' or 'ema'
            period (int): Moving average period
            relation (str): 'above', 'below', or 'cross'
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            price = data.get('price')
            moving_averages = data.get('moving_averages', {})
            
            ma_key = f"{ma_type}_{period}"
            ma_value = moving_averages.get(ma_key)
            
            if price is None or ma_value is None:
                continue
            
            if relation == 'above' and price > ma_value:
                results.append(ticker)
            elif relation == 'below' and price < ma_value:
                results.append(ticker)
            elif relation == 'cross':
                # For cross, we would need historical data to determine crossing
                pass
        
        return results
    
    def screen_by_volume(self, min_ratio=None):
        """
        Screen stocks by volume relative to average.
        
        Args:
            min_ratio (float): Minimum ratio of current volume to average
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            volume = data.get('volume')
            avg_volume = data.get('avg_volume')
            
            if volume is None or avg_volume is None or avg_volume == 0:
                continue
            
            volume_ratio = volume / avg_volume
            
            if min_ratio is not None and volume_ratio < min_ratio:
                continue
            
            results.append(ticker)
        
        return results
    
    def screen_by_macd(self, signal='bullish'):
        """
        Screen stocks by MACD signal.
        
        Args:
            signal (str): 'bullish' or 'bearish'
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            indicators = data.get('indicators', {})
            macd = indicators.get('macd', {})
            
            if not macd:
                continue
            
            macd_line = macd.get('line')
            signal_line = macd.get('signal')
            
            if macd_line is None or signal_line is None:
                continue
            
            if signal == 'bullish' and macd_line > signal_line:
                results.append(ticker)
            elif signal == 'bearish' and macd_line < signal_line:
                results.append(ticker)
        
        return results
    
    def screen_by_bollinger_bands(self, position='lower'):
        """
        Screen stocks by position relative to Bollinger Bands.
        
        Args:
            position (str): 'upper', 'lower', or 'middle'
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            price = data.get('price')
            indicators = data.get('indicators', {})
            bollinger = indicators.get('bollinger', {})
            
            if not bollinger or price is None:
                continue
            
            upper_band = bollinger.get('upper')
            middle_band = bollinger.get('middle')
            lower_band = bollinger.get('lower')
            
            if upper_band is None or middle_band is None or lower_band is None:
                continue
            
            if position == 'upper' and price >= upper_band:
                results.append(ticker)
            elif position == 'lower' and price <= lower_band:
                results.append(ticker)
            elif position == 'middle' and price > lower_band and price < upper_band:
                results.append(ticker)
        
        return results
    
    def screen_by_recommendation(self, recommendation_type):
        """
        Screen stocks by recommendation type.
        
        Args:
            recommendation_type (str): 'buy', 'sell', or 'hold'
            
        Returns:
            list: Tickers that meet the criteria
        """
        if not self.stock_data:
            return []
        
        results = []
        
        for ticker, data in self.stock_data.items():
            recommendation = data.get('recommendation')
            
            if recommendation is None:
                continue
            
            if recommendation_type == 'buy' and recommendation in ['buy', 'strong_buy']:
                results.append(ticker)
            elif recommendation_type == 'sell' and recommendation in ['sell', 'strong_sell']:
                results.append(ticker)
            elif recommendation_type == 'hold' and recommendation == 'hold':
                results.append(ticker)
        
        return results
    
    def apply_multiple_filters(self, filters):
        """
        Apply multiple screening filters.
        
        Args:
            filters (list): List of filter dictionaries
            
        Returns:
            list: Tickers that meet all criteria
        """
        if not self.stock_data or not filters:
            return []
        
        # Start with all tickers
        all_tickers = list(self.stock_data.keys())
        filtered_tickers = set(all_tickers)
        
        for filter_dict in filters:
            filter_type = filter_dict.get('type')
            
            if filter_type == 'price':
                min_price = filter_dict.get('min')
                max_price = filter_dict.get('max')
                result = set(self.screen_by_price(min_price, max_price))
            
            elif filter_type == 'market_cap':
                min_cap = filter_dict.get('min')
                max_cap = filter_dict.get('max')
                result = set(self.screen_by_market_cap(min_cap, max_cap))
            
            elif filter_type == 'sector':
                sectors = filter_dict.get('sectors', [])
                result = set(self.screen_by_sector(sectors))
            
            elif filter_type == 'pe_ratio':
                min_pe = filter_dict.get('min')
                max_pe = filter_dict.get('max')
                result = set(self.screen_by_pe_ratio(min_pe, max_pe))
            
            elif filter_type == 'pb_ratio':
                min_pb = filter_dict.get('min')
                max_pb = filter_dict.get('max')
                result = set(self.screen_by_pb_ratio(min_pb, max_pb))
            
            elif filter_type == 'dividend_yield':
                min_yield = filter_dict.get('min')
                max_yield = filter_dict.get('max')
                result = set(self.screen_by_dividend_yield(min_yield, max_yield))
            
            elif filter_type == 'roe':
                min_roe = filter_dict.get('min')
                result = set(self.screen_by_roe(min_roe))
            
            elif filter_type == 'debt_to_equity':
                max_ratio = filter_dict.get('max')
                result = set(self.screen_by_debt_to_equity(max_ratio))
            
            elif filter_type == 'revenue_growth':
                min_growth = filter_dict.get('min')
                result = set(self.screen_by_revenue_growth(min_growth))
            
            elif filter_type == 'earnings_growth':
                min_growth = filter_dict.get('min')
                result = set(self.screen_by_earnings_growth(min_growth))
            
            elif filter_type == 'rsi':
                min_rsi = filter_dict.get('min')
                max_rsi = filter_dict.get('max')
                result = set(self.screen_by_rsi(min_rsi, max_rsi))
            
            elif filter_type == 'moving_average':
                ma_type = filter_dict.get('ma_type', 'sma')
                period = filter_dict.get('period', 50)
                relation = filter_dict.get('relation', 'above')
                result = set(self.screen_by_moving_average(ma_type, period, relation))
            
            elif filter_type == 'volume':
                min_ratio = filter_dict.get('min_ratio')
                result = set(self.screen_by_volume(min_ratio))
            
            elif filter_type == 'macd':
                signal = filter_dict.get('signal', 'bullish')
                result = set(self.screen_by_macd(signal))
            
            elif filter_type == 'bollinger_bands':
                position = filter_dict.get('position', 'lower')
                result = set(self.screen_by_bollinger_bands(position))
            
            elif filter_type == 'recommendation':
                recommendation_type = filter_dict.get('recommendation_type')
                result = set(self.screen_by_recommendation(recommendation_type))
            
            else:
                # Unknown filter type, skip
                continue
            
            # Intersect with previous results
            filtered_tickers = filtered_tickers.intersection(result)
        
        return list(filtered_tickers)
    
    def get_stock_details(self, tickers):
        """
        Get detailed information for a list of tickers.
        
        Args:
            tickers (list): List of stock tickers
            
        Returns:
            dict: Detailed stock information
        """
        if not self.stock_data:
            return {}
        
        details = {}
        
        for ticker in tickers:
            if ticker in self.stock_data:
                details[ticker] = self.stock_data[ticker]
        
        return details
    
    def rank_stocks(self, tickers, criteria, weights=None):
        """
        Rank stocks based on multiple criteria.
        
        Args:
            tickers (list): List of stock tickers to rank
            criteria (list): List of criteria to rank by
            weights (list): Weights for each criterion
            
        Returns:
            list: Ranked tickers
        """
        if not self.stock_data or not tickers or not criteria:
            return []
        
        # Default equal weights if not provided
        if weights is None:
            weights = [1.0] * len(criteria)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Calculate scores for each ticker
        scores = {}
        
        for ticker in tickers:
            if ticker not in self.stock_data:
                continue
            
            data = self.stock_data[ticker]
            ticker_score = 0
            
            for i, criterion in enumerate(criteria):
                criterion_type = criterion.get('type')
                criterion_weight = weights[i]
                
                # Extract value based on criterion type
                if criterion_type in data:
                    value = data[criterion_type]
                elif criterion_type in data.get('indicators', {}):
                    value = data['indicators'][criterion_type]
                else:
                    value = None
                
                if value is None:
                    continue
                
                # Determine if higher is better
                higher_is_better = criterion.get('higher_is_better', True)
                
                # Normalize value between 0 and 1
                min_val = criterion.get('min', 0)
                max_val = criterion.get('max', 1)
                
                if max_val > min_val:
                    normalized_value = (value - min_val) / (max_val - min_val)
                    normalized_value = max(0, min(1, normalized_value))
                    
                    if not higher_is_better:
                        normalized_value = 1 - normalized_value
                    
                    ticker_score += normalized_value * criterion_weight
            
            scores[ticker] = ticker_score
        
        # Sort tickers by score
        ranked_tickers = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return ranked_tickers
    
    def save_screen_results(self, results, filepath):
        """
        Save screening results to a file.
        
        Args:
            results (list): List of tickers or dict of details
            filepath (str): Path to save the results
            
        Returns:
            str: Path where results were saved
        """
        # Convert results to DataFrame
        if isinstance(results, list):
            df = pd.DataFrame({'ticker': results})
        else:
            df = pd.DataFrame.from_dict(results, orient='index')
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        return filepath