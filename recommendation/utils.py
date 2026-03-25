"""
Utility functions for the recommendation system.

This module provides helper functions and utilities for the
recommendation engine and portfolio optimization components.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def format_recommendation(recommendation, language='ar'):
    """
    Format a recommendation into a human-readable format.
    
    Args:
        recommendation (dict): Recommendation data
        language (str): Language code ('ar' for Arabic, 'en' for English)
        
    Returns:
        dict: Formatted recommendation
    """
    ticker = recommendation['ticker']
    rec_type = recommendation['recommendation']
    score = recommendation['score']
    date = recommendation['analysis_date']
    
    # Map recommendation types to human-readable text
    if language == 'ar':
        rec_map = {
            'strong_buy': 'شراء قوي',
            'buy': 'شراء',
            'hold': 'احتفاظ',
            'sell': 'بيع',
            'strong_sell': 'بيع قوي'
        }
        
        time_horizon_map = {
            'short': 'قصير المدى',
            'medium': 'متوسط المدى',
            'long': 'طويل المدى'
        }
        
        risk_level_map = {
            'low': 'منخفضة',
            'medium': 'متوسطة',
            'high': 'عالية'
        }
    else:  # English
        rec_map = {
            'strong_buy': 'Strong Buy',
            'buy': 'Buy',
            'hold': 'Hold',
            'sell': 'Sell',
            'strong_sell': 'Strong Sell'
        }
        
        time_horizon_map = {
            'short': 'Short-term',
            'medium': 'Medium-term',
            'long': 'Long-term'
        }
        
        risk_level_map = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High'
        }
    
    # Format the recommendation
    formatted = {
        'ticker': ticker,
        'recommendation': rec_map.get(rec_type, rec_type),
        'score': round(score * 100),  # Convert to percentage
        'date': date,
        'time_horizon': time_horizon_map.get(recommendation['time_horizon'], recommendation['time_horizon']),
        'risk_level': risk_level_map.get(recommendation['risk_assessment']['risk_level'], 
                                         recommendation['risk_assessment']['risk_level']),
        'explanation': recommendation['explanation']
    }
    
    return formatted

def calculate_consensus(recommendations):
    """
    Calculate consensus recommendation from multiple sources.
    
    Args:
        recommendations (list): List of recommendation dictionaries
        
    Returns:
        dict: Consensus recommendation
    """
    if not recommendations:
        return None
    
    # Extract scores and weights
    scores = []
    weights = []
    
    for rec in recommendations:
        # Convert recommendation type to numeric score
        if rec['recommendation'] == 'strong_buy':
            score = 1.0
        elif rec['recommendation'] == 'buy':
            score = 0.75
        elif rec['recommendation'] == 'hold':
            score = 0.5
        elif rec['recommendation'] == 'sell':
            score = 0.25
        else:  # strong_sell
            score = 0.0
        
        # Use confidence as weight if available, otherwise equal weights
        weight = rec.get('confidence', 1.0)
        
        scores.append(score)
        weights.append(weight)
    
    # Normalize weights
    weights = np.array(weights) / sum(weights)
    
    # Calculate weighted average score
    consensus_score = sum(np.array(scores) * weights)
    
    # Convert back to recommendation type
    if consensus_score >= 0.875:
        consensus_type = 'strong_buy'
    elif consensus_score >= 0.625:
        consensus_type = 'buy'
    elif consensus_score >= 0.375:
        consensus_type = 'hold'
    elif consensus_score >= 0.125:
        consensus_type = 'sell'
    else:
        consensus_type = 'strong_sell'
    
    # Create consensus recommendation
    consensus = {
        'recommendation': consensus_type,
        'score': consensus_score,
        'sources': len(recommendations),
        'analysis_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    return consensus

def save_recommendation(recommendation, directory, filename=None):
    """
    Save a recommendation to a JSON file.
    
    Args:
        recommendation (dict): Recommendation data
        directory (str): Directory to save the file
        filename (str): Optional filename (default: ticker_date.json)
        
    Returns:
        str: Path to the saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        ticker = recommendation['ticker']
        date = recommendation['analysis_date'].replace('-', '')
        filename = f"{ticker}_{date}.json"
    
    # Save to file
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recommendation, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_recommendation(filepath):
    """
    Load a recommendation from a JSON file.
    
    Args:
        filepath (str): Path to the recommendation file
        
    Returns:
        dict: Recommendation data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        recommendation = json.load(f)
    
    return recommendation

def filter_recommendations(recommendations, criteria):
    """
    Filter recommendations based on criteria.
    
    Args:
        recommendations (list): List of recommendation dictionaries
        criteria (dict): Filtering criteria
        
    Returns:
        list: Filtered recommendations
    """
    filtered = recommendations.copy()
    
    # Filter by recommendation type
    if 'recommendation' in criteria:
        rec_types = criteria['recommendation']
        if not isinstance(rec_types, list):
            rec_types = [rec_types]
        filtered = [r for r in filtered if r['recommendation'] in rec_types]
    
    # Filter by minimum score
    if 'min_score' in criteria:
        min_score = criteria['min_score']
        filtered = [r for r in filtered if r['score'] >= min_score]
    
    # Filter by date range
    if 'date_from' in criteria:
        date_from = criteria['date_from']
        filtered = [r for r in filtered if r['analysis_date'] >= date_from]
    
    if 'date_to' in criteria:
        date_to = criteria['date_to']
        filtered = [r for r in filtered if r['analysis_date'] <= date_to]
    
    # Filter by time horizon
    if 'time_horizon' in criteria:
        horizons = criteria['time_horizon']
        if not isinstance(horizons, list):
            horizons = [horizons]
        filtered = [r for r in filtered if r['time_horizon'] in horizons]
    
    # Filter by risk level
    if 'risk_level' in criteria:
        risk_levels = criteria['risk_level']
        if not isinstance(risk_levels, list):
            risk_levels = [risk_levels]
        filtered = [r for r in filtered if r['risk_assessment']['risk_level'] in risk_levels]
    
    return filtered

def generate_report(recommendations, format_type='html', language='ar'):
    """
    Generate a report from a list of recommendations.
    
    Args:
        recommendations (list): List of recommendation dictionaries
        format_type (str): Report format ('html', 'markdown', 'text')
        language (str): Language code ('ar' for Arabic, 'en' for English)
        
    Returns:
        str: Formatted report
    """
    # Format each recommendation
    formatted_recs = [format_recommendation(r, language) for r in recommendations]
    
    if format_type == 'html':
        return _generate_html_report(formatted_recs, language)
    elif format_type == 'markdown':
        return _generate_markdown_report(formatted_recs, language)
    else:  # text
        return _generate_text_report(formatted_recs, language)

def _generate_html_report(recommendations, language='ar'):
    """
    Generate an HTML report from formatted recommendations.
    
    Args:
        recommendations (list): List of formatted recommendation dictionaries
        language (str): Language code
        
    Returns:
        str: HTML report
    """
    # Set direction based on language
    direction = 'rtl' if language == 'ar' else 'ltr'
    
    # Set labels based on language
    if language == 'ar':
        labels = {
            'title': 'تقرير التوصيات',
            'ticker': 'الرمز',
            'recommendation': 'التوصية',
            'score': 'النتيجة',
            'date': 'التاريخ',
            'time_horizon': 'الأفق الزمني',
            'risk_level': 'مستوى المخاطرة',
            'explanation': 'التفسير'
        }
    else:  # English
        labels = {
            'title': 'Recommendations Report',
            'ticker': 'Ticker',
            'recommendation': 'Recommendation',
            'score': 'Score',
            'date': 'Date',
            'time_horizon': 'Time Horizon',
            'risk_level': 'Risk Level',
            'explanation': 'Explanation'
        }
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="{language}" dir="{direction}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{labels['title']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; direction: {direction}; }}
            .recommendation {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            .strong-buy {{ background-color: #d4edda; }}
            .buy {{ background-color: #e8f4f8; }}
            .hold {{ background-color: #fff3cd; }}
            .sell {{ background-color: #f8d7da; }}
            .strong-sell {{ background-color: #f5c6cb; }}
            .header {{ font-weight: bold; margin-bottom: 5px; }}
            .score {{ font-size: 1.2em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>{labels['title']}</h1>
    """
    
    # Add each recommendation
    for rec in recommendations:
        # Determine CSS class based on recommendation
        if rec['recommendation'] in ['شراء قوي', 'Strong Buy']:
            css_class = 'strong-buy'
        elif rec['recommendation'] in ['شراء', 'Buy']:
            css_class = 'buy'
        elif rec['recommendation'] in ['احتفاظ', 'Hold']:
            css_class = 'hold'
        elif rec['recommendation'] in ['بيع', 'Sell']:
            css_class = 'sell'
        else:  # Strong Sell
            css_class = 'strong-sell'
        
        html += f"""
        <div class="recommendation {css_class}">
            <div class="header">{labels['ticker']}: {rec['ticker']}</div>
            <div class="header">{labels['recommendation']}: {rec['recommendation']}</div>
            <div class="score">{labels['score']}: {rec['score']}%</div>
            <div>{labels['date']}: {rec['date']}</div>
            <div>{labels['time_horizon']}: {rec['time_horizon']}</div>
            <div>{labels['risk_level']}: {rec['risk_level']}</div>
            <div>{labels['explanation']}: {rec['explanation']}</div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html

def _generate_markdown_report(recommendations, language='ar'):
    """
    Generate a Markdown report from formatted recommendations.
    
    Args:
        recommendations (list): List of formatted recommendation dictionaries
        language (str): Language code
        
    Returns:
        str: Markdown report
    """
    # Set labels based on language
    if language == 'ar':
        labels = {
            'title': 'تقرير التوصيات',
            'ticker': 'الرمز',
            'recommendation': 'التوصية',
            'score': 'النتيجة',
            'date': 'التاريخ',
            'time_horizon': 'الأفق الزمني',
            'risk_level': 'مستوى المخاطرة',
            'explanation': 'التفسير'
        }
    else:  # English
        labels = {
            'title': 'Recommendations Report',
            'ticker': 'Ticker',
            'recommendation': 'Recommendation',
            'score': 'Score',
            'date': 'Date',
            'time_horizon': 'Time Horizon',
            'risk_level': 'Risk Level',
            'explanation': 'Explanation'
        }
    
    # Generate Markdown
    markdown = f"# {labels['title']}\n\n"
    
    # Add each recommendation
    for rec in recommendations:
        markdown += f"## {rec['ticker']} - {rec['recommendation']}\n\n"
        markdown += f"**{labels['score']}:** {rec['score']}%\n\n"
        markdown += f"**{labels['date']}:** {rec['date']}\n\n"
        markdown += f"**{labels['time_horizon']}:** {rec['time_horizon']}\n\n"
        markdown += f"**{labels['risk_level']}:** {rec['risk_level']}\n\n"
        markdown += f"**{labels['explanation']}:** {rec['explanation']}\n\n"
        markdown += "---\n\n"
    
    return markdown

def _generate_text_report(recommendations, language='ar'):
    """
    Generate a plain text report from formatted recommendations.
    
    Args:
        recommendations (list): List of formatted recommendation dictionaries
        language (str): Language code
        
    Returns:
        str: Text report
    """
    # Set labels based on language
    if language == 'ar':
        labels = {
            'title': 'تقرير التوصيات',
            'ticker': 'الرمز',
            'recommendation': 'التوصية',
            'score': 'النتيجة',
            'date': 'التاريخ',
            'time_horizon': 'الأفق الزمني',
            'risk_level': 'مستوى المخاطرة',
            'explanation': 'التفسير'
        }
    else:  # English
        labels = {
            'title': 'Recommendations Report',
            'ticker': 'Ticker',
            'recommendation': 'Recommendation',
            'score': 'Score',
            'date': 'Date',
            'time_horizon': 'Time Horizon',
            'risk_level': 'Risk Level',
            'explanation': 'Explanation'
        }
    
    # Generate text
    text = f"{labels['title']}\n"
    text += "=" * len(labels['title']) + "\n\n"
    
    # Add each recommendation
    for rec in recommendations:
        text += f"{rec['ticker']} - {rec['recommendation']}\n"
        text += "-" * (len(rec['ticker']) + len(rec['recommendation']) + 3) + "\n"
        text += f"{labels['score']}: {rec['score']}%\n"
        text += f"{labels['date']}: {rec['date']}\n"
        text += f"{labels['time_horizon']}: {rec['time_horizon']}\n"
        text += f"{labels['risk_level']}: {rec['risk_level']}\n"
        text += f"{labels['explanation']}: {rec['explanation']}\n\n"
        text += "-" * 40 + "\n\n"
    
    return text