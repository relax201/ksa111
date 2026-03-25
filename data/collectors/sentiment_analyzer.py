"""
Sentiment Analyzer for Arabic and English Financial News and Social Media Content

This module provides functionality to analyze sentiment in financial news and
social media content related to Saudi stocks.
"""

import os
import re
import json
import logging
import requests
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import NLTK for text processing
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    logging.warning("NLTK not installed. Some features may not work.")

# Import Arabic NLP libraries if available
try:
    import camel_tools.sentiment
    from camel_tools.tokenizers.word import simple_word_tokenize
    from camel_tools.utils.normalize import normalize_unicode
    ARABIC_NLP_AVAILABLE = True
except ImportError:
    ARABIC_NLP_AVAILABLE = False
    logging.warning("Arabic NLP libraries not installed. Arabic sentiment analysis will be limited.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Analyzes sentiment in financial news and social media content.
    Supports both Arabic and English text.
    """
    
    def __init__(self, cache_dir: str = 'cache/sentiment'):
        """
        Initialize the sentiment analyzer.
        
        Args:
            cache_dir: Directory to cache sentiment analysis results
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize NLTK resources
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.sid = SentimentIntensityAnalyzer()
            self.english_stopwords = set(stopwords.words('english'))
        except Exception as e:
            logger.error(f"Error initializing NLTK resources: {e}")
            self.sid = None
            self.english_stopwords = set()
        
        # Initialize Arabic sentiment analyzer if available
        if ARABIC_NLP_AVAILABLE:
            try:
                self.arabic_analyzer = camel_tools.sentiment.SentimentAnalyzer()
                self.arabic_stopwords = set(nltk.corpus.stopwords.words('arabic'))
            except Exception as e:
                logger.error(f"Error initializing Arabic sentiment analyzer: {e}")
                self.arabic_analyzer = None
                self.arabic_stopwords = set()
        else:
            self.arabic_analyzer = None
            self.arabic_stopwords = set()
        
        # Load financial terms sentiment lexicon
        self.financial_lexicon = self._load_financial_lexicon()
        
        # Load company name variations
        self.company_names = self._load_company_names()
    
    def _load_financial_lexicon(self) -> Dict[str, float]:
        """
        Load financial terms sentiment lexicon.
        
        Returns:
            Dictionary mapping financial terms to sentiment scores
        """
        # Default financial terms with sentiment scores
        default_lexicon = {
            # Positive terms
            "growth": 0.7,
            "profit": 0.8,
            "increase": 0.6,
            "dividend": 0.7,
            "bullish": 0.9,
            "outperform": 0.8,
            "upgrade": 0.7,
            "beat": 0.6,
            "exceed": 0.6,
            "strong": 0.5,
            "positive": 0.6,
            "opportunity": 0.5,
            "recovery": 0.6,
            "gain": 0.6,
            "improved": 0.5,
            "expansion": 0.6,
            "نمو": 0.7,
            "ربح": 0.8,
            "زيادة": 0.6,
            "توزيعات": 0.7,
            "صعود": 0.7,
            "تفوق": 0.6,
            "ترقية": 0.7,
            "تجاوز": 0.6,
            "قوي": 0.5,
            "إيجابي": 0.6,
            "فرصة": 0.5,
            "تعافي": 0.6,
            "مكاسب": 0.6,
            "تحسن": 0.5,
            "توسع": 0.6,
            
            # Negative terms
            "loss": -0.8,
            "decline": -0.7,
            "decrease": -0.6,
            "bearish": -0.9,
            "underperform": -0.8,
            "downgrade": -0.7,
            "miss": -0.6,
            "below": -0.5,
            "weak": -0.5,
            "negative": -0.6,
            "risk": -0.5,
            "debt": -0.5,
            "drop": -0.7,
            "fall": -0.7,
            "concern": -0.5,
            "cut": -0.6,
            "خسارة": -0.8,
            "تراجع": -0.7,
            "انخفاض": -0.6,
            "هبوط": -0.7,
            "ضعف": -0.5,
            "سلبي": -0.6,
            "مخاطر": -0.5,
            "ديون": -0.5,
            "هبوط": -0.7,
            "قلق": -0.5,
            "خفض": -0.6,
        }
        
        # Try to load custom lexicon from file
        lexicon_path = os.path.join(self.cache_dir, 'financial_lexicon.json')
        try:
            if os.path.exists(lexicon_path):
                with open(lexicon_path, 'r', encoding='utf-8') as f:
                    custom_lexicon = json.load(f)
                    # Merge with default lexicon
                    default_lexicon.update(custom_lexicon)
                    logger.info(f"Loaded custom financial lexicon with {len(custom_lexicon)} terms")
        except Exception as e:
            logger.error(f"Error loading custom financial lexicon: {e}")
        
        return default_lexicon
    
    def _load_company_names(self) -> Dict[str, List[str]]:
        """
        Load company name variations.
        
        Returns:
            Dictionary mapping company symbols to name variations
        """
        # Default company names
        default_names = {
            "TASI.2222": ["Aramco", "Saudi Aramco", "أرامكو", "أرامكو السعودية"],
            "TASI.1150": ["Alinma Bank", "Alinma", "بنك الإنماء", "الإنماء"],
            "TASI.2350": ["Saudi Kayan", "Kayan", "كيان", "كيان السعودية"],
            "TASI.2310": ["SIPCHEM", "Saudi International Petrochemical", "سبكيم", "سبكيم العالمية"],
            "TASI.2380": ["Petro Rabigh", "Rabigh Refining", "بترو رابغ"],
            "TASI.1010": ["RIBL", "Riyad Bank", "بنك الرياض", "الرياض"],
            "TASI.1050": ["NCB", "National Commercial Bank", "البنك الأهلي", "الأهلي"],
            "TASI.2001": ["SABIC", "Saudi Basic Industries", "سابك", "سابك السعودية"],
            "TASI.4240": ["FIPCO", "Filing and Packing Materials Manufacturing", "فيبكو"],
            "TASI.4003": ["Ceramic", "Saudi Ceramic", "الخزف", "الخزف السعودي"]
        }
        
        # Try to load custom company names from file
        names_path = os.path.join(self.cache_dir, 'company_names.json')
        try:
            if os.path.exists(names_path):
                with open(names_path, 'r', encoding='utf-8') as f:
                    custom_names = json.load(f)
                    # Merge with default names
                    for symbol, names in custom_names.items():
                        if symbol in default_names:
                            default_names[symbol].extend(names)
                        else:
                            default_names[symbol] = names
                    logger.info(f"Loaded custom company names for {len(custom_names)} symbols")
        except Exception as e:
            logger.error(f"Error loading custom company names: {e}")
        
        return default_names
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('ar' for Arabic, 'en' for English, 'unknown' for others)
        """
        # Simple language detection based on character sets
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        english_chars = re.findall(r'[a-zA-Z]', text)
        
        if len(arabic_chars) > len(english_chars):
            return 'ar'
        elif len(english_chars) > 0:
            return 'en'
        else:
            return 'unknown'
    
    def preprocess_text(self, text: str, language: str = None) -> str:
        """
        Preprocess text for sentiment analysis.
        
        Args:
            text: Text to preprocess
            language: Language code ('ar' for Arabic, 'en' for English)
                     If None, language will be detected
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if language == 'en':
            # Convert to lowercase for English
            text = text.lower()
            
            # Tokenize and remove stopwords for English
            if self.english_stopwords:
                tokens = word_tokenize(text)
                tokens = [token for token in tokens if token not in self.english_stopwords]
                text = ' '.join(tokens)
        
        elif language == 'ar':
            # Normalize Arabic text
            if ARABIC_NLP_AVAILABLE:
                text = normalize_unicode(text)
                
                # Tokenize and remove stopwords for Arabic
                if self.arabic_stopwords:
                    tokens = simple_word_tokenize(text)
                    tokens = [token for token in tokens if token not in self.arabic_stopwords]
                    text = ' '.join(tokens)
        
        return text
    
    def analyze_sentiment_english(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment in English text.
        
        Args:
            text: English text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text or not self.sid:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        # Get VADER sentiment scores
        vader_scores = self.sid.polarity_scores(text)
        
        # Adjust scores using financial lexicon
        words = text.lower().split()
        financial_score = 0.0
        financial_terms_count = 0
        
        for word in words:
            if word in self.financial_lexicon:
                financial_score += self.financial_lexicon[word]
                financial_terms_count += 1
        
        # Combine VADER and financial lexicon scores
        if financial_terms_count > 0:
            # Weighted average: 70% VADER, 30% financial lexicon
            compound = 0.7 * vader_scores['compound'] + 0.3 * (financial_score / financial_terms_count)
            # Ensure compound score is in [-1, 1]
            compound = max(-1.0, min(1.0, compound))
            
            # Adjust positive/negative/neutral based on new compound
            if compound >= 0.05:
                positive = vader_scores['positive'] * (1 + 0.3 * compound)
                negative = vader_scores['negative'] * (1 - 0.3 * compound)
            elif compound <= -0.05:
                positive = vader_scores['positive'] * (1 + 0.3 * compound)
                negative = vader_scores['negative'] * (1 - 0.3 * compound)
            else:
                positive = vader_scores['positive']
                negative = vader_scores['negative']
            
            # Ensure positive and negative are in [0, 1]
            positive = max(0.0, min(1.0, positive))
            negative = max(0.0, min(1.0, negative))
            neutral = 1.0 - positive - negative
            
            return {
                'compound': compound,
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            }
        else:
            return vader_scores
    
    def analyze_sentiment_arabic(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment in Arabic text.
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        if ARABIC_NLP_AVAILABLE and self.arabic_analyzer:
            try:
                # Use CAMeL Tools for Arabic sentiment analysis
                result = self.arabic_analyzer.predict(text)
                
                # Map CAMeL Tools result to our format
                if result == 'positive':
                    return {'compound': 0.6, 'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
                elif result == 'negative':
                    return {'compound': -0.6, 'positive': 0.1, 'negative': 0.8, 'neutral': 0.1}
                else:  # neutral
                    return {'compound': 0.0, 'positive': 0.2, 'negative': 0.2, 'neutral': 0.6}
            except Exception as e:
                logger.error(f"Error using CAMeL Tools for Arabic sentiment analysis: {e}")
        
        # Fallback: Use lexicon-based approach for Arabic
        words = text.split()
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if word in self.financial_lexicon:
                score = self.financial_lexicon[word]
                if score > 0:
                    positive_count += 1
                elif score < 0:
                    negative_count += 1
        
        total_count = len(words)
        if total_count > 0:
            positive_ratio = positive_count / total_count
            negative_ratio = negative_count / total_count
            neutral_ratio = 1.0 - positive_ratio - negative_ratio
            compound = positive_ratio - negative_ratio
            
            return {
                'compound': compound,
                'positive': positive_ratio,
                'negative': negative_ratio,
                'neutral': neutral_ratio
            }
        else:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def analyze_sentiment(self, text: str, language: str = None) -> Dict[str, float]:
        """
        Analyze sentiment in text.
        
        Args:
            text: Text to analyze
            language: Language code ('ar' for Arabic, 'en' for English)
                     If None, language will be detected
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)
        
        # Preprocess text
        preprocessed_text = self.preprocess_text(text, language)
        
        if language == 'en':
            return self.analyze_sentiment_english(preprocessed_text)
        elif language == 'ar':
            return self.analyze_sentiment_arabic(preprocessed_text)
        else:
            # Fallback to English for unknown languages
            return self.analyze_sentiment_english(preprocessed_text)
    
    def analyze_news_sentiment(self, news_items: List[Dict[str, Any]], symbol: str = None) -> Dict[str, Any]:
        """
        Analyze sentiment in news items.
        
        Args:
            news_items: List of news items, each with 'title' and 'content' keys
            symbol: Stock symbol to filter news items (optional)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not news_items:
            return {
                'sentiment': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 1.0,
                'count': 0,
                'items': []
            }
        
        # Filter news items by symbol if provided
        if symbol and symbol in self.company_names:
            company_variations = self.company_names[symbol]
            filtered_items = []
            
            for item in news_items:
                title = item.get('title', '')
                content = item.get('content', '')
                full_text = f"{title} {content}"
                
                # Check if any company name variation is in the text
                if any(variation.lower() in full_text.lower() for variation in company_variations):
                    filtered_items.append(item)
            
            # If no items match the symbol, use all items
            if filtered_items:
                news_items = filtered_items
        
        analyzed_items = []
        total_compound = 0.0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for item in news_items:
            title = item.get('title', '')
            content = item.get('content', '')
            
            # Analyze title and content separately
            title_sentiment = self.analyze_sentiment(title)
            content_sentiment = self.analyze_sentiment(content)
            
            # Combine title and content sentiment (title has more weight)
            compound = 0.6 * title_sentiment['compound'] + 0.4 * content_sentiment['compound']
            
            # Determine sentiment category
            if compound >= 0.05:
                sentiment_category = 'positive'
                positive_count += 1
            elif compound <= -0.05:
                sentiment_category = 'negative'
                negative_count += 1
            else:
                sentiment_category = 'neutral'
                neutral_count += 1
            
            total_compound += compound
            
            analyzed_items.append({
                'title': title,
                'sentiment': compound,
                'category': sentiment_category,
                'date': item.get('date', '')
            })
        
        total_count = len(news_items)
        average_sentiment = total_compound / total_count if total_count > 0 else 0.0
        
        return {
            'sentiment': average_sentiment,
            'positive_ratio': positive_count / total_count if total_count > 0 else 0.0,
            'negative_ratio': negative_count / total_count if total_count > 0 else 0.0,
            'neutral_ratio': neutral_count / total_count if total_count > 0 else 0.0,
            'count': total_count,
            'items': analyzed_items
        }
    
    def analyze_social_sentiment(self, posts: List[Dict[str, Any]], symbol: str = None) -> Dict[str, Any]:
        """
        Analyze sentiment in social media posts.
        
        Args:
            posts: List of social media posts, each with 'text' key
            symbol: Stock symbol to filter posts (optional)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not posts:
            return {
                'sentiment': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 1.0,
                'count': 0,
                'items': []
            }
        
        # Filter posts by symbol if provided
        if symbol and symbol in self.company_names:
            company_variations = self.company_names[symbol]
            filtered_posts = []
            
            for post in posts:
                text = post.get('text', '')
                
                # Check if any company name variation is in the text
                if any(variation.lower() in text.lower() for variation in company_variations):
                    filtered_posts.append(post)
            
            # If no posts match the symbol, use all posts
            if filtered_posts:
                posts = filtered_posts
        
        analyzed_posts = []
        total_compound = 0.0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for post in posts:
            text = post.get('text', '')
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)
            compound = sentiment['compound']
            
            # Determine sentiment category
            if compound >= 0.05:
                sentiment_category = 'positive'
                positive_count += 1
            elif compound <= -0.05:
                sentiment_category = 'negative'
                negative_count += 1
            else:
                sentiment_category = 'neutral'
                neutral_count += 1
            
            total_compound += compound
            
            analyzed_posts.append({
                'text': text[:100] + '...' if len(text) > 100 else text,  # Truncate long texts
                'sentiment': compound,
                'category': sentiment_category,
                'date': post.get('date', ''),
                'source': post.get('source', '')
            })
        
        total_count = len(posts)
        average_sentiment = total_compound / total_count if total_count > 0 else 0.0
        
        return {
            'sentiment': average_sentiment,
            'positive_ratio': positive_count / total_count if total_count > 0 else 0.0,
            'negative_ratio': negative_count / total_count if total_count > 0 else 0.0,
            'neutral_ratio': neutral_count / total_count if total_count > 0 else 0.0,
            'count': total_count,
            'items': analyzed_posts
        }
    
    def get_sentiment_trend(self, items: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
        """
        Calculate sentiment trend over time.
        
        Args:
            items: List of items with 'date' and 'sentiment' keys
            days: Number of days to include in the trend
            
        Returns:
            Dictionary with sentiment trend data
        """
        if not items:
            return {
                'trend': [],
                'overall_change': 0.0,
                'recent_change': 0.0
            }
        
        # Convert dates to datetime objects
        for item in items:
            if 'date' in item and isinstance(item['date'], str):
                try:
                    item['date'] = datetime.strptime(item['date'], '%Y-%m-%d')
                except ValueError:
                    try:
                        item['date'] = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        item['date'] = datetime.now()
        
        # Filter items by date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        filtered_items = [item for item in items if 'date' in item and start_date <= item['date'] <= end_date]
        
        if not filtered_items:
            return {
                'trend': [],
                'overall_change': 0.0,
                'recent_change': 0.0
            }
        
        # Group items by date
        date_groups = {}
        for item in filtered_items:
            date_str = item['date'].strftime('%Y-%m-%d')
            if date_str not in date_groups:
                date_groups[date_str] = []
            date_groups[date_str].append(item['sentiment'])
        
        # Calculate average sentiment for each date
        trend = []
        for date_str, sentiments in sorted(date_groups.items()):
            average_sentiment = sum(sentiments) / len(sentiments)
            trend.append({
                'date': date_str,
                'sentiment': average_sentiment
            })
        
        # Calculate overall change
        if len(trend) >= 2:
            overall_change = trend[-1]['sentiment'] - trend[0]['sentiment']
        else:
            overall_change = 0.0
        
        # Calculate recent change (last 7 days)
        recent_trend = trend[-7:] if len(trend) >= 7 else trend
        if len(recent_trend) >= 2:
            recent_change = recent_trend[-1]['sentiment'] - recent_trend[0]['sentiment']
        else:
            recent_change = 0.0
        
        return {
            'trend': trend,
            'overall_change': overall_change,
            'recent_change': recent_change
        }
    
    def update_financial_lexicon(self, new_terms: Dict[str, float]) -> None:
        """
        Update financial terms sentiment lexicon.
        
        Args:
            new_terms: Dictionary mapping financial terms to sentiment scores
        """
        if not new_terms:
            return
        
        # Update lexicon
        self.financial_lexicon.update(new_terms)
        
        # Save updated lexicon to file
        lexicon_path = os.path.join(self.cache_dir, 'financial_lexicon.json')
        try:
            with open(lexicon_path, 'w', encoding='utf-8') as f:
                json.dump(self.financial_lexicon, f, ensure_ascii=False, indent=2)
            logger.info(f"Updated financial lexicon with {len(new_terms)} new terms")
        except Exception as e:
            logger.error(f"Error saving updated financial lexicon: {e}")
    
    def update_company_names(self, symbol: str, new_names: List[str]) -> None:
        """
        Update company name variations.
        
        Args:
            symbol: Stock symbol
            new_names: List of new name variations
        """
        if not symbol or not new_names:
            return
        
        # Update company names
        if symbol in self.company_names:
            # Add new names that don't already exist
            self.company_names[symbol].extend([name for name in new_names if name not in self.company_names[symbol]])
        else:
            self.company_names[symbol] = new_names
        
        # Save updated company names to file
        names_path = os.path.join(self.cache_dir, 'company_names.json')
        try:
            with open(names_path, 'w', encoding='utf-8') as f:
                json.dump(self.company_names, f, ensure_ascii=False, indent=2)
            logger.info(f"Updated company names for {symbol} with {len(new_names)} new variations")
        except Exception as e:
            logger.error(f"Error saving updated company names: {e}")

    # ---- واجهة التكامل مع system_integration.py ----

    def analyze(self, symbols: List[str], sources: Optional[List[str]] = None,
                time_range: str = '1w') -> Dict[str, Any]:
        """
        تحليل المشاعر لمجموعة من رموز الأسهم.

        المعلمات:
            symbols: قائمة رموز الأسهم
            sources: مصادر البيانات (news, social_media, analyst_ratings)
            time_range: النطاق الزمني (1d, 1w, 1m)

        العائد:
            Dict: نتائج تحليل المشاعر لكل رمز
        """
        if sources is None:
            sources = ['news', 'social_media', 'analyst_ratings']
        result = {}
        for symbol in symbols:
            try:
                symbol_sentiment = {
                    'overall': 0.0,
                    'positive_ratio': 0.0,
                    'negative_ratio': 0.0,
                    'neutral_ratio': 1.0,
                    'sources': {}
                }
                # Fetch real news items via yfinance
                news_items = []
                if 'news' in sources:
                    try:
                        import yfinance as yf
                        ticker_news = yf.Ticker(symbol).news or []
                        for item in ticker_news:
                            news_items.append({
                                'title': item.get('title', ''),
                                'content': item.get('summary', item.get('title', '')),
                                'date': item.get('providerPublishTime', ''),
                            })
                    except Exception as news_err:
                        logger.warning(f"Could not fetch yfinance news for {symbol}: {news_err}")
                    symbol_sentiment['sources']['news'] = self.analyze_news_sentiment(news_items, symbol)
                if 'social_media' in sources:
                    symbol_sentiment['sources']['social_media'] = self.analyze_social_sentiment([], symbol)
                # Aggregate overall sentiment from news source
                news_result = symbol_sentiment['sources'].get('news', {})
                symbol_sentiment['overall'] = news_result.get('sentiment', 0.0)
                symbol_sentiment['positive_ratio'] = news_result.get('positive_ratio', 0.0)
                symbol_sentiment['negative_ratio'] = news_result.get('negative_ratio', 0.0)
                symbol_sentiment['neutral_ratio'] = news_result.get('neutral_ratio', 1.0)
                result[symbol] = symbol_sentiment
            except Exception as e:
                logger.error(f"Error analyzing sentiment for {symbol}: {e}")
                result[symbol] = {'overall': 0.0, 'error': str(e)}
        self._last_update_time = datetime.now().isoformat()
        return result

    def get_last_update_time(self) -> str:
        """إعادة وقت آخر تحديث."""
        if hasattr(self, '_last_update_time'):
            return self._last_update_time
        return datetime.now().isoformat()
