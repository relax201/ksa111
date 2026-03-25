"""
Enhanced Data Collector for Saudi Stock Market (Tadawul)

This module provides functionality to collect data from multiple sources
to enhance the accuracy of stock recommendations.
"""

import os
import json
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from bs4 import BeautifulSoup
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedDataCollector:
    """
    A class for collecting enhanced data from multiple sources for Saudi stocks.
    """
    
    def __init__(self, cache_dir: str = 'cache'):
        """
        Initialize the enhanced data collector.
        
        Args:
            cache_dir: Directory to cache data
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'news'), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'social'), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'analyst'), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'macro'), exist_ok=True)
        
        # Initialize sentiment analyzer
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {e}")
            self.sentiment_analyzer = None
        
        # User agents for web scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def _get_random_user_agent(self) -> str:
        """
        Get a random user agent.
        
        Returns:
            Random user agent string
        """
        return random.choice(self.user_agents)
    
    def _get_cache_path(self, data_type: str, symbol: str, date_str: str = None) -> str:
        """
        Get the cache file path.
        
        Args:
            data_type: Type of data ('news', 'social', 'analyst', 'macro')
            symbol: Stock symbol
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            Cache file path
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        return os.path.join(self.cache_dir, data_type, f"{symbol}_{date_str}.json")
    
    def _load_from_cache(self, cache_path: str) -> Optional[Dict]:
        """
        Load data from cache.
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            Cached data or None if not found
        """
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if cache is still valid (less than 24 hours old)
                if 'timestamp' in data:
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=24):
                        logger.info(f"Loaded data from cache: {cache_path}")
                        return data
            except Exception as e:
                logger.error(f"Error loading from cache: {e}")
        
        return None
    
    def _save_to_cache(self, cache_path: str, data: Dict) -> None:
        """
        Save data to cache.
        
        Args:
            cache_path: Path to cache file
            data: Data to cache
        """
        try:
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved data to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def collect_news_data(self, symbol: str, days: int = 30) -> Dict:
        """
        Collect news data for a stock.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            Dictionary with news data
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        cache_path = self._get_cache_path('news', symbol, date_str)
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_path)
        if cached_data:
            return cached_data
        
        # Sources to collect news from
        sources = [
            self._collect_argaam_news,
            self._collect_tadawul_news,
            self._collect_mubasher_news,
            self._collect_cnbc_arabia_news
        ]
        
        all_news = []
        
        # Collect news from all sources
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {executor.submit(source, symbol, days): source.__name__ for source in sources}
            
            for future in future_to_source:
                source_name = future_to_source[future]
                try:
                    news = future.result()
                    if news:
                        logger.info(f"Collected {len(news)} news items from {source_name}")
                        all_news.extend(news)
                except Exception as e:
                    logger.error(f"Error collecting news from {source_name}: {e}")
        
        # Sort news by date (newest first)
        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Calculate sentiment for each news item
        if self.sentiment_analyzer:
            for news in all_news:
                if 'title' in news and 'content' in news:
                    text = f"{news['title']} {news['content']}"
                    sentiment = self.sentiment_analyzer.polarity_scores(text)
                    news['sentiment'] = sentiment
        
        # Calculate overall sentiment
        if all_news:
            sentiment_scores = [news.get('sentiment', {}).get('compound', 0) for news in all_news if 'sentiment' in news]
            if sentiment_scores:
                overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            else:
                overall_sentiment = 0
        else:
            overall_sentiment = 0
        
        # Prepare result
        result = {
            'symbol': symbol,
            'news_count': len(all_news),
            'news': all_news,
            'overall_sentiment': overall_sentiment,
            'collection_date': date_str
        }
        
        # Save to cache
        self._save_to_cache(cache_path, result)
        
        return result
    
    def _collect_argaam_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Collect news from Argaam.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of news items
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Argaam API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_tadawul_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Collect news from Tadawul.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of news items
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Tadawul API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_mubasher_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Collect news from Mubasher.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of news items
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Mubasher API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_cnbc_arabia_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Collect news from CNBC Arabia.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of news items
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the CNBC Arabia API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def collect_social_sentiment(self, symbol: str) -> Dict:
        """
        Collect social media sentiment for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with social sentiment data
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        cache_path = self._get_cache_path('social', symbol, date_str)
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_path)
        if cached_data:
            return cached_data
        
        # Sources to collect social sentiment from
        sources = [
            self._collect_twitter_sentiment,
            self._collect_stocktwits_sentiment,
            self._collect_reddit_sentiment
        ]
        
        all_posts = []
        
        # Collect sentiment from all sources
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {executor.submit(source, symbol): source.__name__ for source in sources}
            
            for future in future_to_source:
                source_name = future_to_source[future]
                try:
                    posts = future.result()
                    if posts:
                        logger.info(f"Collected {len(posts)} posts from {source_name}")
                        all_posts.extend(posts)
                except Exception as e:
                    logger.error(f"Error collecting sentiment from {source_name}: {e}")
        
        # Calculate overall sentiment
        if all_posts:
            positive_count = sum(1 for post in all_posts if post.get('sentiment', 0) > 0)
            negative_count = sum(1 for post in all_posts if post.get('sentiment', 0) < 0)
            neutral_count = sum(1 for post in all_posts if post.get('sentiment', 0) == 0)
            
            total_count = len(all_posts)
            
            if total_count > 0:
                positive_ratio = positive_count / total_count
                negative_ratio = negative_count / total_count
                neutral_ratio = neutral_count / total_count
                
                # Calculate sentiment score (-1 to 1)
                sentiment_score = (positive_count - negative_count) / total_count
            else:
                positive_ratio = 0
                negative_ratio = 0
                neutral_ratio = 0
                sentiment_score = 0
        else:
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            total_count = 0
            positive_ratio = 0
            negative_ratio = 0
            neutral_ratio = 0
            sentiment_score = 0
        
        # Prepare result
        result = {
            'symbol': symbol,
            'post_count': total_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'neutral_ratio': neutral_ratio,
            'sentiment_score': sentiment_score,
            'posts': all_posts[:100],  # Limit to 100 posts
            'collection_date': date_str
        }
        
        # Save to cache
        self._save_to_cache(cache_path, result)
        
        return result
    
    def _collect_twitter_sentiment(self, symbol: str) -> List[Dict]:
        """
        Collect sentiment from Twitter.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of posts with sentiment
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Twitter API
        
        # Simulate API call
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_stocktwits_sentiment(self, symbol: str) -> List[Dict]:
        """
        Collect sentiment from StockTwits.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of posts with sentiment
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the StockTwits API
        
        # Simulate API call
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_reddit_sentiment(self, symbol: str) -> List[Dict]:
        """
        Collect sentiment from Reddit.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of posts with sentiment
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Reddit API
        
        # Simulate API call
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def collect_analyst_ratings(self, symbol: str) -> Dict:
        """
        Collect analyst ratings for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with analyst ratings
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        cache_path = self._get_cache_path('analyst', symbol, date_str)
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_path)
        if cached_data:
            return cached_data
        
        # Sources to collect analyst ratings from
        sources = [
            self._collect_argaam_ratings,
            self._collect_bloomberg_ratings,
            self._collect_reuters_ratings
        ]
        
        all_ratings = []
        
        # Collect ratings from all sources
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {executor.submit(source, symbol): source.__name__ for source in sources}
            
            for future in future_to_source:
                source_name = future_to_source[future]
                try:
                    ratings = future.result()
                    if ratings:
                        logger.info(f"Collected {len(ratings)} ratings from {source_name}")
                        all_ratings.extend(ratings)
                except Exception as e:
                    logger.error(f"Error collecting ratings from {source_name}: {e}")
        
        # Calculate consensus rating
        if all_ratings:
            buy_count = sum(1 for rating in all_ratings if rating.get('rating', '').lower() in ['buy', 'strong buy', 'outperform', 'overweight'])
            sell_count = sum(1 for rating in all_ratings if rating.get('rating', '').lower() in ['sell', 'strong sell', 'underperform', 'underweight'])
            hold_count = sum(1 for rating in all_ratings if rating.get('rating', '').lower() in ['hold', 'neutral'])
            
            total_count = len(all_ratings)
            
            if total_count > 0:
                buy_ratio = buy_count / total_count
                sell_ratio = sell_count / total_count
                hold_ratio = hold_count / total_count
                
                # Calculate consensus score (-1 to 1)
                consensus_score = (buy_count - sell_count) / total_count
                
                # Determine consensus rating
                if consensus_score >= 0.6:
                    consensus_rating = 'Strong Buy'
                elif consensus_score >= 0.2:
                    consensus_rating = 'Buy'
                elif consensus_score >= -0.2:
                    consensus_rating = 'Hold'
                elif consensus_score >= -0.6:
                    consensus_rating = 'Sell'
                else:
                    consensus_rating = 'Strong Sell'
            else:
                buy_ratio = 0
                sell_ratio = 0
                hold_ratio = 0
                consensus_score = 0
                consensus_rating = 'N/A'
        else:
            buy_count = 0
            sell_count = 0
            hold_count = 0
            total_count = 0
            buy_ratio = 0
            sell_ratio = 0
            hold_ratio = 0
            consensus_score = 0
            consensus_rating = 'N/A'
        
        # Calculate average target price
        target_prices = [rating.get('target_price', 0) for rating in all_ratings if rating.get('target_price', 0) > 0]
        if target_prices:
            avg_target_price = sum(target_prices) / len(target_prices)
        else:
            avg_target_price = 0
        
        # Prepare result
        result = {
            'symbol': symbol,
            'rating_count': total_count,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'hold_count': hold_count,
            'buy_ratio': buy_ratio,
            'sell_ratio': sell_ratio,
            'hold_ratio': hold_ratio,
            'consensus_score': consensus_score,
            'consensus_rating': consensus_rating,
            'avg_target_price': avg_target_price,
            'ratings': all_ratings,
            'collection_date': date_str
        }
        
        # Save to cache
        self._save_to_cache(cache_path, result)
        
        return result
    
    def _collect_argaam_ratings(self, symbol: str) -> List[Dict]:
        """
        Collect analyst ratings from Argaam.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of analyst ratings
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Argaam API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_bloomberg_ratings(self, symbol: str) -> List[Dict]:
        """
        Collect analyst ratings from Bloomberg.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of analyst ratings
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Bloomberg API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def _collect_reuters_ratings(self, symbol: str) -> List[Dict]:
        """
        Collect analyst ratings from Reuters.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of analyst ratings
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Reuters API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty list for now
        return []
    
    def collect_macro_economic_data(self) -> Dict:
        """
        Collect macroeconomic data.
        
        Returns:
            Dictionary with macroeconomic data
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        cache_path = self._get_cache_path('macro', 'general', date_str)
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_path)
        if cached_data:
            return cached_data
        
        # Sources to collect macroeconomic data from
        sources = [
            self._collect_sama_data,
            self._collect_jadwa_data,
            self._collect_imf_data,
            self._collect_world_bank_data
        ]
        
        macro_data = {}
        
        # Collect data from all sources
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {executor.submit(source): source.__name__ for source in sources}
            
            for future in future_to_source:
                source_name = future_to_source[future]
                try:
                    data = future.result()
                    if data:
                        logger.info(f"Collected macroeconomic data from {source_name}")
                        macro_data[source_name.split('_')[1]] = data
                except Exception as e:
                    logger.error(f"Error collecting macroeconomic data from {source_name}: {e}")
        
        # Prepare result
        result = {
            'data': macro_data,
            'collection_date': date_str
        }
        
        # Save to cache
        self._save_to_cache(cache_path, result)
        
        return result
    
    def _collect_sama_data(self) -> Dict:
        """
        Collect macroeconomic data from SAMA (Saudi Arabian Monetary Authority).
        
        Returns:
            Dictionary with macroeconomic data
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the SAMA API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty dict for now
        return {}
    
    def _collect_jadwa_data(self) -> Dict:
        """
        Collect macroeconomic data from Jadwa Investment.
        
        Returns:
            Dictionary with macroeconomic data
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Jadwa API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty dict for now
        return {}
    
    def _collect_imf_data(self) -> Dict:
        """
        Collect macroeconomic data from IMF.
        
        Returns:
            Dictionary with macroeconomic data
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the IMF API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty dict for now
        return {}
    
    def _collect_world_bank_data(self) -> Dict:
        """
        Collect macroeconomic data from World Bank.
        
        Returns:
            Dictionary with macroeconomic data
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the World Bank API or scrape their website
        
        # Simulate API call or web scraping
        time.sleep(random.uniform(0.5, 1.5))
        
        # Return empty dict for now
        return {}
    
    def collect_institutional_ownership(self, symbol: str) -> Dict:
        """
        Collect institutional ownership data for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with institutional ownership data
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        cache_path = os.path.join(self.cache_dir, f"institutional_{symbol}_{date_str}.json")
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_path)
        if cached_data:
            return cached_data
        
        # This is a placeholder implementation
        # In a real implementation, you would collect institutional ownership data
        
        # Simulate data collection
        time.sleep(random.uniform(0.5, 1.5))
        
        # Prepare result
        result = {
            'symbol': symbol,
            'institutional_ownership': 0,
            'major_holders': [],
            'collection_date': date_str
        }
        
        # Save to cache
        self._save_to_cache(cache_path, result)
        
        return result
    
    def collect_enhanced_data(self, symbol: str) -> Dict:
        """
        Collect all enhanced data for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with all enhanced data
        """
        logger.info(f"Collecting enhanced data for {symbol}")
        
        # Collect data from all sources
        try:
            news_data = self.collect_news_data(symbol)
        except Exception as e:
            logger.error(f"Error collecting news data: {e}")
            news_data = {'symbol': symbol, 'news_count': 0, 'news': [], 'overall_sentiment': 0}
        
        try:
            social_sentiment = self.collect_social_sentiment(symbol)
        except Exception as e:
            logger.error(f"Error collecting social sentiment: {e}")
            social_sentiment = {'symbol': symbol, 'post_count': 0, 'sentiment_score': 0}
        
        try:
            analyst_ratings = self.collect_analyst_ratings(symbol)
        except Exception as e:
            logger.error(f"Error collecting analyst ratings: {e}")
            analyst_ratings = {'symbol': symbol, 'rating_count': 0, 'consensus_rating': 'N/A', 'avg_target_price': 0}
        
        try:
            institutional_ownership = self.collect_institutional_ownership(symbol)
        except Exception as e:
            logger.error(f"Error collecting institutional ownership: {e}")
            institutional_ownership = {'symbol': symbol, 'institutional_ownership': 0}
        
        try:
            macro_data = self.collect_macro_economic_data()
        except Exception as e:
            logger.error(f"Error collecting macroeconomic data: {e}")
            macro_data = {'data': {}}
        
        # Combine all data
        result = {
            'symbol': symbol,
            'collection_date': datetime.now().strftime('%Y-%m-%d'),
            'news': {
                'count': news_data.get('news_count', 0),
                'sentiment': news_data.get('overall_sentiment', 0)
            },
            'social': {
                'count': social_sentiment.get('post_count', 0),
                'sentiment': social_sentiment.get('sentiment_score', 0)
            },
            'analyst': {
                'count': analyst_ratings.get('rating_count', 0),
                'consensus': analyst_ratings.get('consensus_rating', 'N/A'),
                'target_price': analyst_ratings.get('avg_target_price', 0)
            },
            'institutional': {
                'ownership': institutional_ownership.get('institutional_ownership', 0)
            },
            'macro': macro_data.get('data', {})
        }
        
        logger.info(f"Collected enhanced data for {symbol}")
        
        return result
    
    def collect_enhanced_data_batch(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Collect enhanced data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to enhanced data
        """
        logger.info(f"Collecting enhanced data for {len(symbols)} symbols")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(10, len(symbols))) as executor:
            future_to_symbol = {executor.submit(self.collect_enhanced_data, symbol): symbol for symbol in symbols}
            
            for future in future_to_symbol:
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    results[symbol] = data
                except Exception as e:
                    logger.error(f"Error collecting enhanced data for {symbol}: {e}")
                    results[symbol] = {'symbol': symbol, 'error': str(e)}
        
        logger.info(f"Collected enhanced data for {len(results)} symbols")
        
        return results