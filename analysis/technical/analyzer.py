#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
محلل فني للأسهم السعودية
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Optional, Tuple
from datetime import datetime, timedelta
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from .indicators import (
    calculate_all_indicators,
    generate_signals,
    calculate_support_resistance,
    calculate_fibonacci_retracement
)


class TechnicalAnalyzer:
    """
    محلل فني للأسهم السعودية
    """
    
    def __init__(self, logger=None):
        """
        تهيئة المحلل الفني
        
        المعلمات:
            logger: كائن التسجيل
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """
        تحليل بيانات السهم فنيًا
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            
        العائد:
            Dict: نتائج التحليل الفني
        """
        if data.empty:
            self.logger.warning("لا توجد بيانات للتحليل")
            return {
                'status': 'error',
                'message': 'لا توجد بيانات للتحليل'
            }
        
        try:
            # حساب جميع المؤشرات الفنية
            indicators = calculate_all_indicators(data)
            
            # توليد إشارات التداول
            signals = generate_signals(data, indicators)
            
            # تحليل الاتجاه
            trend_analysis = self._analyze_trend(data, indicators)
            
            # تحليل الدعم والمقاومة
            support_resistance = self._analyze_support_resistance(data)
            
            # تحليل مستويات فيبوناتشي
            fibonacci_levels = self._analyze_fibonacci(data)
            
            # تحليل التقلب
            volatility_analysis = self._analyze_volatility(data)
            
            # تحليل الزخم
            momentum_analysis = self._analyze_momentum(indicators)
            
            # تحليل حجم التداول
            volume_analysis = self._analyze_volume(data)
            
            # تحديد السعر المستهدف ووقف الخسارة
            price_targets = self._determine_price_targets(data, indicators, signals, support_resistance)
            
            # تقييم عام
            overall_assessment = self._overall_assessment(signals, trend_analysis, momentum_analysis)
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'indicators': {k: v.iloc[-1] if isinstance(v, pd.Series) else v for k, v in indicators.items() if k not in ['support_resistance', 'fibonacci']},
                'signals': signals,
                'trend': trend_analysis,
                'support_resistance': support_resistance,
                'fibonacci': fibonacci_levels,
                'volatility': volatility_analysis,
                'momentum': momentum_analysis,
                'volume': volume_analysis,
                'price_targets': price_targets,
                'assessment': overall_assessment
            }
        
        except Exception as e:
            self.logger.error(f"خطأ في التحليل الفني: {str(e)}")
            return {
                'status': 'error',
                'message': f'خطأ في التحليل الفني: {str(e)}'
            }
    
    def _analyze_trend(self, data: pd.DataFrame, indicators: Dict) -> Dict:
        """
        تحليل اتجاه السهم
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            indicators (Dict): المؤشرات الفنية
            
        العائد:
            Dict: نتائج تحليل الاتجاه
        """
        result = {
            'short_term': 'neutral',
            'medium_term': 'neutral',
            'long_term': 'neutral',
            'strength': 0,
            'description': ''
        }
        
        # تحليل الاتجاه قصير المدى (20 يوم)
        if 'sma_20' in indicators and 'ema_20' in indicators:
            close = data['close'].iloc[-1]
            sma_20 = indicators['sma_20'].iloc[-1]
            ema_20 = indicators['ema_20'].iloc[-1]
            
            if close > sma_20 and close > ema_20:
                result['short_term'] = 'bullish'
            elif close < sma_20 and close < ema_20:
                result['short_term'] = 'bearish'
        
        # تحليل الاتجاه متوسط المدى (50 يوم)
        if 'sma_50' in indicators:
            close = data['close'].iloc[-1]
            sma_50 = indicators['sma_50'].iloc[-1]
            
            if close > sma_50:
                result['medium_term'] = 'bullish'
            elif close < sma_50:
                result['medium_term'] = 'bearish'
        
        # تحليل الاتجاه طويل المدى (200 يوم)
        if 'sma_200' in indicators:
            close = data['close'].iloc[-1]
            sma_200 = indicators['sma_200'].iloc[-1]
            
            if close > sma_200:
                result['long_term'] = 'bullish'
            elif close < sma_200:
                result['long_term'] = 'bearish'
        
        # تحليل قوة الاتجاه
        if 'adx' in indicators:
            adx = indicators['adx']['adx'].iloc[-1]
            plus_di = indicators['adx']['plus_di'].iloc[-1]
            minus_di = indicators['adx']['minus_di'].iloc[-1]
            
            if adx > 25:
                result['strength'] = min(100, adx)
                
                if plus_di > minus_di:
                    result['description'] = f'اتجاه صاعد قوي (ADX: {adx:.2f})'
                else:
                    result['description'] = f'اتجاه هابط قوي (ADX: {adx:.2f})'
            else:
                result['strength'] = adx
                result['description'] = f'اتجاه ضعيف أو عدم وجود اتجاه واضح (ADX: {adx:.2f})'
        
        return result
    
    def _analyze_support_resistance(self, data: pd.DataFrame) -> Dict:
        """
        تحليل مستويات الدعم والمقاومة
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            
        العائد:
            Dict: نتائج تحليل الدعم والمقاومة
        """
        levels = calculate_support_resistance(data)
        last_close = data['close'].iloc[-1]
        
        # تحديد أقرب مستويات الدعم والمقاومة
        resistance_levels = sorted([r for r in levels['resistance'] if r > last_close])
        support_levels = sorted([s for s in levels['support'] if s < last_close], reverse=True)
        
        nearest_resistance = resistance_levels[0] if resistance_levels else None
        nearest_support = support_levels[0] if support_levels else None
        
        return {
            'levels': levels,
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support,
            'resistance_levels': resistance_levels[:3] if len(resistance_levels) >= 3 else resistance_levels,
            'support_levels': support_levels[:3] if len(support_levels) >= 3 else support_levels
        }
    
    def _analyze_fibonacci(self, data: pd.DataFrame) -> Dict:
        """
        تحليل مستويات فيبوناتشي
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            
        العائد:
            Dict: نتائج تحليل فيبوناتشي
        """
        # تحديد أعلى وأدنى سعر في الفترة الأخيرة
        high = data['high'].iloc[-20:].max()
        low = data['low'].iloc[-20:].min()
        
        # حساب مستويات فيبوناتشي
        levels = calculate_fibonacci_retracement(high, low)
        
        # تحديد المستوى الحالي
        last_close = data['close'].iloc[-1]
        current_level = None
        
        for level, value in levels.items():
            if abs(last_close - value) / value < 0.01:  # ضمن 1% من المستوى
                current_level = level
                break
        
        return {
            'levels': levels,
            'current_level': current_level,
            'high': high,
            'low': low
        }
    
    def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """
        تحليل تقلب السهم
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            
        العائد:
            Dict: نتائج تحليل التقلب
        """
        # حساب التقلب اليومي
        daily_returns = data['close'].pct_change()
        volatility_20d = daily_returns.iloc[-20:].std() * np.sqrt(252) * 100  # تقلب سنوي بالنسبة المئوية
        
        # تصنيف التقلب
        volatility_level = 'منخفض'
        if volatility_20d > 40:
            volatility_level = 'مرتفع جدًا'
        elif volatility_20d > 30:
            volatility_level = 'مرتفع'
        elif volatility_20d > 20:
            volatility_level = 'متوسط'
        
        # حساب متوسط المدى اليومي
        avg_range_20d = ((data['high'] - data['low']) / data['close']).iloc[-20:].mean() * 100
        
        return {
            'volatility_20d': volatility_20d,
            'avg_range_20d': avg_range_20d,
            'level': volatility_level,
            'description': f'تقلب {volatility_level} ({volatility_20d:.2f}% سنويًا)'
        }
    
    def _analyze_momentum(self, indicators: Dict) -> Dict:
        """
        تحليل زخم السهم
        
        المعلمات:
            indicators (Dict): المؤشرات الفنية
            
        العائد:
            Dict: نتائج تحليل الزخم
        """
        result = {
            'strength': 0,
            'direction': 'neutral',
            'description': ''
        }
        
        # تحليل RSI
        if 'rsi' in indicators:
            rsi = indicators['rsi'].iloc[-1]
            
            if rsi > 70:
                result['direction'] = 'overbought'
                result['strength'] = min(100, rsi)
                result['description'] = f'ذروة شراء (RSI: {rsi:.2f})'
            elif rsi < 30:
                result['direction'] = 'oversold'
                result['strength'] = max(0, 100 - rsi)
                result['description'] = f'ذروة بيع (RSI: {rsi:.2f})'
            elif rsi > 50:
                result['direction'] = 'positive'
                result['strength'] = rsi
                result['description'] = f'زخم إيجابي (RSI: {rsi:.2f})'
            else:
                result['direction'] = 'negative'
                result['strength'] = 100 - rsi
                result['description'] = f'زخم سلبي (RSI: {rsi:.2f})'
        
        # تحليل MACD
        if 'macd' in indicators:
            macd_line = indicators['macd']['macd_line'].iloc[-1]
            signal_line = indicators['macd']['signal_line'].iloc[-1]
            histogram = indicators['macd']['histogram'].iloc[-1]
            
            if macd_line > signal_line and histogram > 0:
                if result['direction'] != 'overbought':
                    result['direction'] = 'positive'
                result['description'] += f', إشارة MACD إيجابية'
            elif macd_line < signal_line and histogram < 0:
                if result['direction'] != 'oversold':
                    result['direction'] = 'negative'
                result['description'] += f', إشارة MACD سلبية'
        
        # تحليل Stochastic
        if 'stochastic' in indicators:
            k = indicators['stochastic']['k'].iloc[-1]
            d = indicators['stochastic']['d'].iloc[-1]
            
            if k > 80 and d > 80:
                if result['direction'] != 'overbought':
                    result['direction'] = 'overbought'
                result['description'] += f', ستوكاستيك في منطقة ذروة الشراء'
            elif k < 20 and d < 20:
                if result['direction'] != 'oversold':
                    result['direction'] = 'oversold'
                result['description'] += f', ستوكاستيك في منطقة ذروة البيع'
        
        return result
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """
        تحليل حجم التداول
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            
        العائد:
            Dict: نتائج تحليل حجم التداول
        """
        if 'volume' not in data.columns:
            return {
                'trend': 'unknown',
                'strength': 0,
                'description': 'لا توجد بيانات حجم التداول'
            }
        
        # حساب متوسط حجم التداول
        avg_volume_20d = data['volume'].iloc[-20:].mean()
        last_volume = data['volume'].iloc[-1]
        
        # تحليل اتجاه حجم التداول
        volume_trend = 'neutral'
        volume_strength = 0
        
        if last_volume > avg_volume_20d * 1.5:
            volume_trend = 'high'
            volume_strength = min(100, (last_volume / avg_volume_20d) * 50)
            description = f'حجم تداول مرتفع ({last_volume / avg_volume_20d:.2f}x المتوسط)'
        elif last_volume < avg_volume_20d * 0.5:
            volume_trend = 'low'
            volume_strength = min(100, (avg_volume_20d / last_volume) * 25)
            description = f'حجم تداول منخفض ({last_volume / avg_volume_20d:.2f}x المتوسط)'
        else:
            description = f'حجم تداول عادي ({last_volume / avg_volume_20d:.2f}x المتوسط)'
        
        # تحليل تأكيد الاتجاه بحجم التداول
        price_change = data['close'].iloc[-1] - data['close'].iloc[-2]
        
        if price_change > 0 and last_volume > avg_volume_20d:
            description += ', يؤكد حجم التداول الاتجاه الصاعد'
        elif price_change < 0 and last_volume > avg_volume_20d:
            description += ', يؤكد حجم التداول الاتجاه الهابط'
        
        return {
            'trend': volume_trend,
            'strength': volume_strength,
            'avg_volume_20d': avg_volume_20d,
            'last_volume': last_volume,
            'volume_change': (last_volume / avg_volume_20d) - 1,
            'description': description
        }
    
    def _determine_price_targets(self, data: pd.DataFrame, indicators: Dict, signals: Dict, support_resistance: Dict) -> Dict:
        """
        تحديد السعر المستهدف ووقف الخسارة
        
        المعلمات:
            data (pd.DataFrame): إطار بيانات يحتوي على أسعار السهم
            indicators (Dict): المؤشرات الفنية
            signals (Dict): إشارات التداول
            support_resistance (Dict): مستويات الدعم والمقاومة
            
        العائد:
            Dict: السعر المستهدف ووقف الخسارة
        """
        last_close = data['close'].iloc[-1]
        
        # تحديد السعر المستهدف بناءً على الاتجاه
        target_price = last_close
        stop_loss = last_close
        
        if signals['direction'] == 'bullish':
            # استخدام مستوى المقاومة القادم كهدف
            if support_resistance['nearest_resistance']:
                target_price = support_resistance['nearest_resistance']
            else:
                # استخدام نسبة مئوية من السعر الحالي
                target_price = last_close * 1.1
            
            # استخدام مستوى الدعم القادم كوقف خسارة
            if support_resistance['nearest_support']:
                stop_loss = support_resistance['nearest_support']
            else:
                # استخدام نسبة مئوية من السعر الحالي
                stop_loss = last_close * 0.95
        
        elif signals['direction'] == 'bearish':
            # استخدام مستوى الدعم القادم كهدف
            if support_resistance['nearest_support']:
                target_price = support_resistance['nearest_support']
            else:
                # استخدام نسبة مئوية من السعر الحالي
                target_price = last_close * 0.9
            
            # استخدام مستوى المقاومة القادم كوقف خسارة
            if support_resistance['nearest_resistance']:
                stop_loss = support_resistance['nearest_resistance']
            else:
                # استخدام نسبة مئوية من السعر الحالي
                stop_loss = last_close * 1.05
        
        # حساب نسبة المخاطرة/المكافأة
        risk = abs(last_close - stop_loss)
        reward = abs(target_price - last_close)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'current_price': last_close,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'potential_return': (target_price / last_close - 1) * 100,
            'risk_percent': (abs(stop_loss / last_close - 1)) * 100,
            'risk_reward_ratio': risk_reward_ratio
        }
    
    def _overall_assessment(self, signals: Dict, trend: Dict, momentum: Dict) -> Dict:
        """
        التقييم العام للسهم
        
        المعلمات:
            signals (Dict): إشارات التداول
            trend (Dict): تحليل الاتجاه
            momentum (Dict): تحليل الزخم
            
        العائد:
            Dict: التقييم العام
        """
        # تحديد التوصية
        recommendation = 'hold'
        confidence = 0
        
        if signals['direction'] == 'bullish' and trend['short_term'] == 'bullish':
            if trend['medium_term'] == 'bullish':
                recommendation = 'buy'
                confidence = min(85, 50 + signals['strength'] * 0.35)
            else:
                recommendation = 'buy'
                confidence = min(70, 40 + signals['strength'] * 0.3)
        
        elif signals['direction'] == 'bearish' and trend['short_term'] == 'bearish':
            if trend['medium_term'] == 'bearish':
                recommendation = 'sell'
                confidence = min(85, 50 + signals['strength'] * 0.35)
            else:
                recommendation = 'sell'
                confidence = min(70, 40 + signals['strength'] * 0.3)
        
        # تعديل الثقة بناءً على الزخم
        if momentum['direction'] == 'overbought' and recommendation == 'buy':
            confidence = max(30, confidence - 20)
        elif momentum['direction'] == 'oversold' and recommendation == 'sell':
            confidence = max(30, confidence - 20)
        
        # تحديد الفترة الزمنية
        time_frame = 'medium'
        if trend['long_term'] == trend['medium_term'] == trend['short_term']:
            time_frame = 'medium-long'
        elif trend['short_term'] != trend['medium_term']:
            time_frame = 'short'
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'time_frame': time_frame,
            'summary': self._generate_summary(recommendation, confidence, signals, trend, momentum)
        }
    
    def _generate_summary(self, recommendation: str, confidence: float, signals: Dict, trend: Dict, momentum: Dict) -> str:
        """
        توليد ملخص التحليل
        
        المعلمات:
            recommendation (str): التوصية
            confidence (float): مستوى الثقة
            signals (Dict): إشارات التداول
            trend (Dict): تحليل الاتجاه
            momentum (Dict): تحليل الزخم
            
        العائد:
            str: ملخص التحليل
        """
        if recommendation == 'buy':
            summary = f"توصية شراء بثقة {confidence:.0f}%. "
            
            if trend['short_term'] == 'bullish' and trend['medium_term'] == 'bullish':
                summary += "الاتجاه صاعد على المدى القصير والمتوسط. "
            elif trend['short_term'] == 'bullish':
                summary += "الاتجاه صاعد على المدى القصير. "
            
            if momentum['direction'] == 'positive':
                summary += "الزخم إيجابي. "
            elif momentum['direction'] == 'overbought':
                summary += "تحذير: السهم في منطقة ذروة شراء. "
            
            if signals['buy']:
                summary += "إشارات الشراء: "
                summary += ", ".join([s['message'] for s in signals['buy'].values()])
            
        elif recommendation == 'sell':
            summary = f"توصية بيع بثقة {confidence:.0f}%. "
            
            if trend['short_term'] == 'bearish' and trend['medium_term'] == 'bearish':
                summary += "الاتجاه هابط على المدى القصير والمتوسط. "
            elif trend['short_term'] == 'bearish':
                summary += "الاتجاه هابط على المدى القصير. "
            
            if momentum['direction'] == 'negative':
                summary += "الزخم سلبي. "
            elif momentum['direction'] == 'oversold':
                summary += "تحذير: السهم في منطقة ذروة بيع. "
            
            if signals['sell']:
                summary += "إشارات البيع: "
                summary += ", ".join([s['message'] for s in signals['sell'].values()])
            
        else:  # hold
            summary = "توصية انتظار. "
            
            if trend['short_term'] != trend['medium_term']:
                summary += f"تضارب في الاتجاه: {trend['short_term']} على المدى القصير و{trend['medium_term']} على المدى المتوسط. "
            else:
                summary += f"الاتجاه {trend['short_term']} ولكن بقوة منخفضة. "
            
            if momentum['direction'] == 'neutral':
                summary += "الزخم متعادل. "

        return summary

    # ---- واجهة التكامل مع system_integration.py ----

    def get_historical_data(self, symbol: str, timeframe: str = 'daily') -> pd.DataFrame:
        """
        جلب البيانات التاريخية للسهم.
        يستخدم yfinance إن كان متاحاً، وإلا يُعيد DataFrame فارغاً.
        """
        if not YFINANCE_AVAILABLE:
            self.logger.warning("yfinance غير مثبَّت، لا يمكن جلب البيانات التاريخية")
            return pd.DataFrame()
        try:
            period_map = {'daily': '1y', 'weekly': '3y', 'monthly': '5y'}
            interval_map = {'daily': '1d', 'weekly': '1wk', 'monthly': '1mo'}
            period = period_map.get(timeframe, '1y')
            interval = interval_map.get(timeframe, '1d')
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return pd.DataFrame()
            # توحيد أسماء الأعمدة
            df.columns = [c.lower() for c in df.columns]
            df.index.name = 'date'
            self._last_update = {symbol: datetime.now().isoformat()}
            return df
        except Exception as e:
            self.logger.error(f"خطأ في جلب البيانات التاريخية لـ {symbol}: {e}")
            return pd.DataFrame()

    def calculate_indicator(self, data: pd.DataFrame, indicator: str) -> Optional[Dict]:
        """
        حساب مؤشر فني واحد وإعادة آخر قيمة له.
        """
        if data.empty:
            return None
        try:
            from .indicators import (
                calculate_sma, calculate_ema, calculate_macd,
                calculate_rsi, calculate_bollinger_bands,
                calculate_stochastic_oscillator, calculate_adx
            )
            indicator_upper = indicator.upper()
            if indicator_upper == 'SMA':
                series = calculate_sma(data, 20)
                return {'value': float(series.iloc[-1]), 'period': 20}
            elif indicator_upper == 'EMA':
                series = calculate_ema(data, 20)
                return {'value': float(series.iloc[-1]), 'period': 20}
            elif indicator_upper == 'RSI':
                series = calculate_rsi(data)
                val = float(series.iloc[-1])
                return {'value': val, 'signal': 'overbought' if val > 70 else ('oversold' if val < 30 else 'neutral')}
            elif indicator_upper == 'MACD':
                macd = calculate_macd(data)
                return {
                    'macd': float(macd['macd_line'].iloc[-1]),
                    'signal': float(macd['signal_line'].iloc[-1]),
                    'histogram': float(macd['histogram'].iloc[-1])
                }
            elif indicator_upper in ('BB', 'BOLLINGER'):
                bb = calculate_bollinger_bands(data)
                return {
                    'upper': float(bb['upper_band'].iloc[-1]),
                    'middle': float(bb['middle_band'].iloc[-1]),
                    'lower': float(bb['lower_band'].iloc[-1])
                }
            elif indicator_upper == 'STOCHASTIC':
                stoch = calculate_stochastic_oscillator(data)
                return {'k': float(stoch['k'].iloc[-1]), 'd': float(stoch['d'].iloc[-1])}
            elif indicator_upper == 'ADX':
                adx = calculate_adx(data)
                return {
                    'adx': float(adx['adx'].iloc[-1]),
                    'plus_di': float(adx['plus_di'].iloc[-1]),
                    'minus_di': float(adx['minus_di'].iloc[-1])
                }
            else:
                self.logger.warning(f"مؤشر غير معروف: {indicator}")
                return None
        except Exception as e:
            self.logger.error(f"خطأ في حساب المؤشر {indicator}: {e}")
            return None

    def analyze_trends(self, data: pd.DataFrame) -> Dict:
        """
        تحليل الاتجاه العام للسهم (واجهة عامة).
        """
        try:
            from .indicators import calculate_all_indicators
            indicators = calculate_all_indicators(data)
            return self._analyze_trend(data, indicators)
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الاتجاه: {e}")
            return {'short_term': 'neutral', 'medium_term': 'neutral', 'long_term': 'neutral', 'strength': 0}

    def get_last_update_time(self, symbol: str = '') -> str:
        """إعادة وقت آخر تحديث للبيانات."""
        if hasattr(self, '_last_update') and symbol in self._last_update:
            return self._last_update[symbol]
        return datetime.now().isoformat()