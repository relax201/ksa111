#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
مكتبة مؤشرات التحليل الفني للأسهم السعودية
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Optional, Tuple


def calculate_sma(data: pd.DataFrame, period: int = 20, price_col: str = 'close') -> pd.Series:
    """
    حساب المتوسط المتحرك البسيط (Simple Moving Average)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        period (int): فترة المتوسط المتحرك
        price_col (str): اسم العمود الذي يحتوي على السعر

    العائد:
        pd.Series: سلسلة تحتوي على قيم المتوسط المتحرك البسيط
    """
    return data[price_col].rolling(window=period).mean()


def calculate_ema(data: pd.DataFrame, period: int = 20, price_col: str = 'close') -> pd.Series:
    """
    حساب المتوسط المتحرك الأسي (Exponential Moving Average)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        period (int): فترة المتوسط المتحرك
        price_col (str): اسم العمود الذي يحتوي على السعر

    العائد:
        pd.Series: سلسلة تحتوي على قيم المتوسط المتحرك الأسي
    """
    return data[price_col].ewm(span=period, adjust=False).mean()


def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, 
                  signal_period: int = 9, price_col: str = 'close') -> Dict[str, pd.Series]:
    """
    حساب مؤشر تقارب وتباعد المتوسطات المتحركة (MACD)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        fast_period (int): فترة المتوسط المتحرك السريع
        slow_period (int): فترة المتوسط المتحرك البطيء
        signal_period (int): فترة خط الإشارة
        price_col (str): اسم العمود الذي يحتوي على السعر

    العائد:
        Dict[str, pd.Series]: قاموس يحتوي على قيم MACD وخط الإشارة والمدرج التكراري
    """
    ema_fast = calculate_ema(data, fast_period, price_col)
    ema_slow = calculate_ema(data, slow_period, price_col)
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    }


def calculate_rsi(data: pd.DataFrame, period: int = 14, price_col: str = 'close') -> pd.Series:
    """
    حساب مؤشر القوة النسبية (Relative Strength Index)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        period (int): فترة حساب المؤشر
        price_col (str): اسم العمود الذي يحتوي على السعر

    العائد:
        pd.Series: سلسلة تحتوي على قيم مؤشر القوة النسبية
    """
    delta = data[price_col].diff()
    
    gain = delta.copy()
    gain[gain < 0] = 0
    
    loss = delta.copy()
    loss[loss > 0] = 0
    loss = abs(loss)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # تجنب القسمة على صفر: avg_loss=0 يعني قوة شراء كاملة → RSI=100
    avg_loss_safe = avg_loss.replace(0, np.nan)
    rs = avg_gain / avg_loss_safe
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(100)

    return rsi


def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0, 
                             price_col: str = 'close') -> Dict[str, pd.Series]:
    """
    حساب نطاقات بولينجر (Bollinger Bands)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        period (int): فترة المتوسط المتحرك
        std_dev (float): عدد الانحرافات المعيارية
        price_col (str): اسم العمود الذي يحتوي على السعر

    العائد:
        Dict[str, pd.Series]: قاموس يحتوي على قيم الخط الأوسط والنطاق العلوي والنطاق السفلي
    """
    middle_band = calculate_sma(data, period, price_col)
    std = data[price_col].rolling(window=period).std()
    
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }


def calculate_stochastic_oscillator(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
    """
    حساب مذبذب ستوكاستيك (Stochastic Oscillator)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        k_period (int): فترة خط %K
        d_period (int): فترة خط %D

    العائد:
        Dict[str, pd.Series]: قاموس يحتوي على قيم %K و %D
    """
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()

    # تجنب القسمة على صفر عندما high_max = low_min (أسعار ثابتة)
    denom = (high_max - low_min).replace(0, np.nan)
    k = 100 * ((data['close'] - low_min) / denom)
    k = k.fillna(50)  # قيمة محايدة عند السعر الثابت
    d = k.rolling(window=d_period).mean()
    
    return {
        'k': k,
        'd': d
    }


def calculate_adx(data: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
    """
    حساب مؤشر الاتجاه المتوسط (Average Directional Index)

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        period (int): فترة حساب المؤشر

    العائد:
        Dict[str, pd.Series]: قاموس يحتوي على قيم ADX و +DI و -DI
    """
    high = data['high']
    low = data['low']
    close = data['close']
    
    # حساب +DM و -DM
    high_diff = high.diff()
    low_diff = low.diff().multiply(-1)
    
    plus_dm = pd.Series(0, index=high_diff.index)
    minus_dm = pd.Series(0, index=low_diff.index)
    
    plus_dm[(high_diff > low_diff) & (high_diff > 0)] = high_diff
    minus_dm[(low_diff > high_diff) & (low_diff > 0)] = low_diff
    
    # حساب TR (True Range)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # حساب المتوسط الأسي لـ +DM و -DM و TR
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    atr_safe = atr.replace(0, np.nan)  # تجنب القسمة على صفر في TR
    plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr_safe)
    minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr_safe)
    plus_di = plus_di.fillna(0)
    minus_di = minus_di.fillna(0)

    # حساب DX و ADX مع تجنب القسمة على صفر
    di_sum = (plus_di + minus_di).replace(0, np.nan)
    dx = 100 * ((plus_di - minus_di).abs() / di_sum)
    dx = dx.fillna(0)
    adx = dx.ewm(alpha=1/period, adjust=False).mean()
    
    return {
        'adx': adx,
        'plus_di': plus_di,
        'minus_di': minus_di
    }


def calculate_fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
    """
    حساب مستويات فيبوناتشي (Fibonacci Retracement)

    المعلمات:
        high (float): أعلى سعر
        low (float): أدنى سعر

    العائد:
        Dict[str, float]: قاموس يحتوي على مستويات فيبوناتشي
    """
    diff = high - low
    
    return {
        '0.0': low,
        '0.236': low + 0.236 * diff,
        '0.382': low + 0.382 * diff,
        '0.5': low + 0.5 * diff,
        '0.618': low + 0.618 * diff,
        '0.786': low + 0.786 * diff,
        '1.0': high
    }


def calculate_support_resistance(data: pd.DataFrame, window: int = 10, threshold: float = 0.02) -> Dict[str, List[float]]:
    """
    تحديد مستويات الدعم والمقاومة

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        window (int): حجم النافذة للبحث عن القمم والقيعان
        threshold (float): عتبة الاختلاف لتحديد المستويات المتشابهة

    العائد:
        Dict[str, List[float]]: قاموس يحتوي على مستويات الدعم والمقاومة
    """
    highs = data['high']
    lows = data['low']
    
    # تحديد القمم المحلية
    peak_idx = []
    for i in range(window, len(highs) - window):
        if highs.iloc[i] == max(highs.iloc[i-window:i+window+1]):
            peak_idx.append(i)
    
    # تحديد القيعان المحلية
    trough_idx = []
    for i in range(window, len(lows) - window):
        if lows.iloc[i] == min(lows.iloc[i-window:i+window+1]):
            trough_idx.append(i)
    
    # استخراج مستويات المقاومة من القمم
    resistance_levels = [highs.iloc[i] for i in peak_idx]
    
    # استخراج مستويات الدعم من القيعان
    support_levels = [lows.iloc[i] for i in trough_idx]
    
    # دمج المستويات المتشابهة
    resistance_levels = merge_similar_levels(resistance_levels, threshold)
    support_levels = merge_similar_levels(support_levels, threshold)
    
    return {
        'resistance': resistance_levels,
        'support': support_levels
    }


def merge_similar_levels(levels: List[float], threshold: float) -> List[float]:
    """
    دمج المستويات المتشابهة

    المعلمات:
        levels (List[float]): قائمة المستويات
        threshold (float): عتبة الاختلاف

    العائد:
        List[float]: قائمة المستويات بعد الدمج
    """
    if not levels:
        return []
    
    levels = sorted(levels)
    merged_levels = [levels[0]]
    
    for level in levels[1:]:
        base = merged_levels[-1]
        # تجنب القسمة على صفر
        if base == 0 or abs(level - base) / abs(base) > threshold:
            merged_levels.append(level)
    
    return merged_levels


def identify_chart_patterns(data: pd.DataFrame, window: int = 20) -> Dict[str, List[Dict]]:
    """
    تحديد أنماط الرسم البياني

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        window (int): حجم النافذة للبحث عن الأنماط

    العائد:
        Dict[str, List[Dict]]: قاموس يحتوي على الأنماط المكتشفة
    """
    patterns = {
        'head_and_shoulders': [],
        'double_top': [],
        'double_bottom': [],
        'triangle': [],
        'flag': [],
        'wedge': []
    }
    
    # تنفيذ خوارزميات اكتشاف الأنماط
    # ملاحظة: هذه مجرد أمثلة بسيطة وتحتاج إلى تنفيذ أكثر تعقيدًا في البيئة الحقيقية
    
    # اكتشاف نمط الرأس والكتفين
    # ...
    
    # اكتشاف نمط القمة المزدوجة
    # ...
    
    # اكتشاف نمط القاع المزدوج
    # ...
    
    return patterns


def calculate_all_indicators(data: pd.DataFrame) -> Dict[str, Union[pd.Series, Dict]]:
    """
    حساب جميع المؤشرات الفنية

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم

    العائد:
        Dict[str, Union[pd.Series, Dict]]: قاموس يحتوي على جميع المؤشرات
    """
    indicators = {}
    
    # المتوسطات المتحركة
    indicators['sma_20'] = calculate_sma(data, 20)
    indicators['sma_50'] = calculate_sma(data, 50)
    indicators['sma_200'] = calculate_sma(data, 200)
    indicators['ema_20'] = calculate_ema(data, 20)
    indicators['ema_50'] = calculate_ema(data, 50)
    
    # مؤشرات الزخم
    indicators['macd'] = calculate_macd(data)
    indicators['rsi'] = calculate_rsi(data)
    indicators['stochastic'] = calculate_stochastic_oscillator(data)
    
    # مؤشرات التقلب
    indicators['bollinger_bands'] = calculate_bollinger_bands(data)
    
    # مؤشرات الاتجاه
    indicators['adx'] = calculate_adx(data)
    
    # مستويات الدعم والمقاومة
    if len(data) > 50:
        indicators['support_resistance'] = calculate_support_resistance(data)
    
    # مستويات فيبوناتشي
    if len(data) > 0:
        high = data['high'].max()
        low = data['low'].min()
        indicators['fibonacci'] = calculate_fibonacci_retracement(high, low)
    
    return indicators


def generate_signals(data: pd.DataFrame, indicators: Dict) -> Dict[str, Dict]:
    """
    توليد إشارات التداول بناءً على المؤشرات الفنية

    المعلمات:
        data (pd.DataFrame): إطار بيانات يحتوي على أسعار الأسهم
        indicators (Dict): قاموس يحتوي على المؤشرات الفنية

    العائد:
        Dict[str, Dict]: قاموس يحتوي على إشارات التداول
    """
    signals = {
        'buy': {},
        'sell': {},
        'hold': {},
        'strength': 0,
        'direction': 'neutral'
    }
    
    # آخر سعر إغلاق
    last_close = data['close'].iloc[-1]
    
    # إشارات المتوسطات المتحركة
    if 'sma_20' in indicators and 'sma_50' in indicators:
        sma_20 = indicators['sma_20'].iloc[-1]
        sma_50 = indicators['sma_50'].iloc[-1]
        
        if sma_20 > sma_50:
            signals['buy']['sma_crossover'] = {
                'message': 'المتوسط المتحرك 20 يوم أعلى من المتوسط المتحرك 50 يوم',
                'strength': 0.6
            }
        elif sma_20 < sma_50:
            signals['sell']['sma_crossover'] = {
                'message': 'المتوسط المتحرك 20 يوم أقل من المتوسط المتحرك 50 يوم',
                'strength': 0.6
            }
    
    # إشارات RSI
    if 'rsi' in indicators:
        rsi = indicators['rsi'].iloc[-1]
        
        if rsi < 30:
            signals['buy']['rsi'] = {
                'message': f'مؤشر القوة النسبية في منطقة ذروة البيع ({rsi:.2f})',
                'strength': 0.7
            }
        elif rsi > 70:
            signals['sell']['rsi'] = {
                'message': f'مؤشر القوة النسبية في منطقة ذروة الشراء ({rsi:.2f})',
                'strength': 0.7
            }
    
    # إشارات MACD
    if 'macd' in indicators:
        macd_line = indicators['macd']['macd_line'].iloc[-1]
        signal_line = indicators['macd']['signal_line'].iloc[-1]
        histogram = indicators['macd']['histogram'].iloc[-1]
        
        if macd_line > signal_line and histogram > 0:
            signals['buy']['macd'] = {
                'message': 'خط MACD أعلى من خط الإشارة والمدرج التكراري إيجابي',
                'strength': 0.65
            }
        elif macd_line < signal_line and histogram < 0:
            signals['sell']['macd'] = {
                'message': 'خط MACD أقل من خط الإشارة والمدرج التكراري سلبي',
                'strength': 0.65
            }
    
    # إشارات نطاقات بولينجر
    if 'bollinger_bands' in indicators:
        upper_band = indicators['bollinger_bands']['upper_band'].iloc[-1]
        lower_band = indicators['bollinger_bands']['lower_band'].iloc[-1]
        
        if last_close <= lower_band:
            signals['buy']['bollinger'] = {
                'message': 'السعر عند أو أقل من النطاق السفلي لبولينجر',
                'strength': 0.6
            }
        elif last_close >= upper_band:
            signals['sell']['bollinger'] = {
                'message': 'السعر عند أو أعلى من النطاق العلوي لبولينجر',
                'strength': 0.6
            }
    
    # حساب قوة الإشارة الإجمالية
    buy_strength = sum([signal['strength'] for signal in signals['buy'].values()]) if signals['buy'] else 0
    sell_strength = sum([signal['strength'] for signal in signals['sell'].values()]) if signals['sell'] else 0
    
    if buy_strength > sell_strength:
        signals['strength'] = buy_strength / (len(signals['buy']) if signals['buy'] else 1)
        signals['direction'] = 'bullish'
    elif sell_strength > buy_strength:
        signals['strength'] = sell_strength / (len(signals['sell']) if signals['sell'] else 1)
        signals['direction'] = 'bearish'
    else:
        signals['strength'] = 0
        signals['direction'] = 'neutral'
    
    return signals