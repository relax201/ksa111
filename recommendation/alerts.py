"""
Alerts Module for Saudi Stock Market (Tasi)

This module provides tools for generating and managing investment alerts
based on technical and fundamental analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class AlertSystem:
    """
    A system for generating and managing investment alerts.
    """
    
    def __init__(self, config=None):
        """
        Initialize the alert system.
        
        Args:
            config (dict): Configuration parameters
        """
        self.config = config or {}
        self.alerts = []
    
    def set_config(self, config):
        """
        Set or update configuration.
        
        Args:
            config (dict): Configuration parameters
        """
        self.config = config
    
    def generate_price_alert(self, ticker, current_price, target_price, alert_type='above'):
        """
        Generate a price-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            current_price (float): Current price
            target_price (float): Target price
            alert_type (str): 'above' or 'below'
            
        Returns:
            dict: Alert details
        """
        if alert_type not in ['above', 'below']:
            raise ValueError("Alert type must be 'above' or 'below'")
        
        # Calculate percentage difference
        percent_diff = (target_price - current_price) / current_price * 100
        
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'price',
            'subtype': alert_type,
            'current_price': current_price,
            'target_price': target_price,
            'percent_difference': percent_diff,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"Price alert for {ticker}: Current {current_price}, Target {target_price} ({alert_type})"
        }
        
        self.alerts.append(alert)
        return alert
    
    def generate_technical_alert(self, ticker, indicator, current_value, threshold, alert_type='cross_above'):
        """
        Generate a technical indicator-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            indicator (str): Technical indicator name
            current_value (float): Current indicator value
            threshold (float): Threshold value
            alert_type (str): 'cross_above', 'cross_below', 'divergence'
            
        Returns:
            dict: Alert details
        """
        valid_types = ['cross_above', 'cross_below', 'divergence']
        if alert_type not in valid_types:
            raise ValueError(f"Alert type must be one of: {', '.join(valid_types)}")
        
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'technical',
            'subtype': alert_type,
            'indicator': indicator,
            'current_value': current_value,
            'threshold': threshold,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"Technical alert for {ticker}: {indicator} {alert_type} {threshold}"
        }
        
        self.alerts.append(alert)
        return alert
    
    def generate_pattern_alert(self, ticker, pattern_type, confidence, price_target=None):
        """
        Generate a chart pattern-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            pattern_type (str): Chart pattern type
            confidence (float): Pattern confidence (0-1)
            price_target (float): Optional price target
            
        Returns:
            dict: Alert details
        """
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'pattern',
            'subtype': pattern_type,
            'confidence': confidence,
            'price_target': price_target,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"Pattern alert for {ticker}: {pattern_type} detected with {confidence:.1%} confidence"
        }
        
        if price_target:
            alert['message'] += f", target price: {price_target}"
        
        self.alerts.append(alert)
        return alert
    
    def generate_fundamental_alert(self, ticker, metric, current_value, threshold, alert_type='above'):
        """
        Generate a fundamental metric-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            metric (str): Fundamental metric name
            current_value (float): Current metric value
            threshold (float): Threshold value
            alert_type (str): 'above' or 'below'
            
        Returns:
            dict: Alert details
        """
        if alert_type not in ['above', 'below']:
            raise ValueError("Alert type must be 'above' or 'below'")
        
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'fundamental',
            'subtype': alert_type,
            'metric': metric,
            'current_value': current_value,
            'threshold': threshold,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"Fundamental alert for {ticker}: {metric} {current_value} {alert_type} threshold {threshold}"
        }
        
        self.alerts.append(alert)
        return alert
    
    def generate_news_alert(self, ticker, news_type, source, importance='medium'):
        """
        Generate a news-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            news_type (str): Type of news
            source (str): News source
            importance (str): 'low', 'medium', or 'high'
            
        Returns:
            dict: Alert details
        """
        if importance not in ['low', 'medium', 'high']:
            raise ValueError("Importance must be 'low', 'medium', or 'high'")
        
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'news',
            'subtype': news_type,
            'source': source,
            'importance': importance,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"News alert for {ticker}: {news_type} from {source} ({importance} importance)"
        }
        
        self.alerts.append(alert)
        return alert
    
    def generate_volume_alert(self, ticker, current_volume, average_volume, threshold=2.0):
        """
        Generate a volume-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            current_volume (float): Current trading volume
            average_volume (float): Average trading volume
            threshold (float): Volume multiple threshold
            
        Returns:
            dict: Alert details
        """
        # Calculate volume ratio
        volume_ratio = current_volume / average_volume if average_volume > 0 else 0
        
        # Create alert if volume ratio exceeds threshold
        if volume_ratio >= threshold:
            alert = {
                'id': self._generate_alert_id(),
                'ticker': ticker,
                'type': 'volume',
                'subtype': 'spike',
                'current_volume': current_volume,
                'average_volume': average_volume,
                'volume_ratio': volume_ratio,
                'threshold': threshold,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active',
                'triggered': False,
                'triggered_at': None,
                'message': f"Volume alert for {ticker}: Current volume {current_volume:,.0f} is {volume_ratio:.1f}x average"
            }
            
            self.alerts.append(alert)
            return alert
        
        return None
    
    def generate_volatility_alert(self, ticker, current_volatility, average_volatility, threshold=1.5):
        """
        Generate a volatility-based alert.
        
        Args:
            ticker (str): Stock ticker symbol
            current_volatility (float): Current volatility
            average_volatility (float): Average volatility
            threshold (float): Volatility multiple threshold
            
        Returns:
            dict: Alert details
        """
        # Calculate volatility ratio
        volatility_ratio = current_volatility / average_volatility if average_volatility > 0 else 0
        
        # Create alert if volatility ratio exceeds threshold
        if volatility_ratio >= threshold:
            alert = {
                'id': self._generate_alert_id(),
                'ticker': ticker,
                'type': 'volatility',
                'subtype': 'spike',
                'current_volatility': current_volatility,
                'average_volatility': average_volatility,
                'volatility_ratio': volatility_ratio,
                'threshold': threshold,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active',
                'triggered': False,
                'triggered_at': None,
                'message': f"Volatility alert for {ticker}: Current volatility is {volatility_ratio:.1f}x average"
            }
            
            self.alerts.append(alert)
            return alert
        
        return None
    
    def generate_recommendation_change_alert(self, ticker, old_recommendation, new_recommendation):
        """
        Generate an alert for recommendation changes.
        
        Args:
            ticker (str): Stock ticker symbol
            old_recommendation (str): Previous recommendation
            new_recommendation (str): New recommendation
            
        Returns:
            dict: Alert details
        """
        # Create alert
        alert = {
            'id': self._generate_alert_id(),
            'ticker': ticker,
            'type': 'recommendation',
            'subtype': 'change',
            'old_recommendation': old_recommendation,
            'new_recommendation': new_recommendation,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'triggered': False,
            'triggered_at': None,
            'message': f"Recommendation change for {ticker}: {old_recommendation} → {new_recommendation}"
        }
        
        self.alerts.append(alert)
        return alert
    
    def check_price_alert(self, alert, current_price):
        """
        Check if a price alert should be triggered.
        
        Args:
            alert (dict): Alert details
            current_price (float): Current price
            
        Returns:
            bool: True if alert is triggered, False otherwise
        """
        if alert['type'] != 'price' or alert['triggered'] or alert['status'] != 'active':
            return False
        
        if alert['subtype'] == 'above' and current_price >= alert['target_price']:
            return True
        
        if alert['subtype'] == 'below' and current_price <= alert['target_price']:
            return True
        
        return False
    
    def check_technical_alert(self, alert, current_value, previous_value=None):
        """
        Check if a technical alert should be triggered.
        
        Args:
            alert (dict): Alert details
            current_value (float): Current indicator value
            previous_value (float): Previous indicator value
            
        Returns:
            bool: True if alert is triggered, False otherwise
        """
        if alert['type'] != 'technical' or alert['triggered'] or alert['status'] != 'active':
            return False
        
        if alert['subtype'] == 'cross_above':
            if previous_value is not None:
                return previous_value < alert['threshold'] and current_value >= alert['threshold']
            return current_value >= alert['threshold']
        
        if alert['subtype'] == 'cross_below':
            if previous_value is not None:
                return previous_value > alert['threshold'] and current_value <= alert['threshold']
            return current_value <= alert['threshold']
        
        # For divergence alerts, specific logic would be implemented based on the indicator
        
        return False
    
    def check_fundamental_alert(self, alert, current_value):
        """
        Check if a fundamental alert should be triggered.
        
        Args:
            alert (dict): Alert details
            current_value (float): Current metric value
            
        Returns:
            bool: True if alert is triggered, False otherwise
        """
        if alert['type'] != 'fundamental' or alert['triggered'] or alert['status'] != 'active':
            return False
        
        if alert['subtype'] == 'above' and current_value >= alert['threshold']:
            return True
        
        if alert['subtype'] == 'below' and current_value <= alert['threshold']:
            return True
        
        return False
    
    def trigger_alert(self, alert_id, trigger_price=None, trigger_value=None):
        """
        Mark an alert as triggered.
        
        Args:
            alert_id (str): Alert ID
            trigger_price (float): Price at trigger time
            trigger_value (float): Value at trigger time
            
        Returns:
            dict: Updated alert
        """
        for i, alert in enumerate(self.alerts):
            if alert['id'] == alert_id:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if trigger_price is not None:
                    alert['trigger_price'] = trigger_price
                
                if trigger_value is not None:
                    alert['trigger_value'] = trigger_value
                
                self.alerts[i] = alert
                return alert
        
        return None
    
    def update_alert_status(self, alert_id, status):
        """
        Update alert status.
        
        Args:
            alert_id (str): Alert ID
            status (str): New status ('active', 'inactive', 'expired')
            
        Returns:
            dict: Updated alert
        """
        valid_statuses = ['active', 'inactive', 'expired']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        for i, alert in enumerate(self.alerts):
            if alert['id'] == alert_id:
                alert['status'] = status
                self.alerts[i] = alert
                return alert
        
        return None
    
    def get_alerts(self, ticker=None, alert_type=None, status=None, triggered=None):
        """
        Get alerts filtered by criteria.
        
        Args:
            ticker (str): Filter by ticker
            alert_type (str): Filter by alert type
            status (str): Filter by status
            triggered (bool): Filter by triggered state
            
        Returns:
            list: Filtered alerts
        """
        filtered = self.alerts
        
        if ticker:
            filtered = [a for a in filtered if a['ticker'] == ticker]
        
        if alert_type:
            filtered = [a for a in filtered if a['type'] == alert_type]
        
        if status:
            filtered = [a for a in filtered if a['status'] == status]
        
        if triggered is not None:
            filtered = [a for a in filtered if a['triggered'] == triggered]
        
        return filtered
    
    def get_alert_by_id(self, alert_id):
        """
        Get an alert by ID.
        
        Args:
            alert_id (str): Alert ID
            
        Returns:
            dict: Alert details or None if not found
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                return alert
        
        return None
    
    def expire_old_alerts(self, days=7):
        """
        Mark old alerts as expired.
        
        Args:
            days (int): Number of days after which to expire alerts
            
        Returns:
            int: Number of alerts expired
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        
        count = 0
        for i, alert in enumerate(self.alerts):
            if alert['status'] == 'active' and alert['created_at'] < cutoff_str:
                alert['status'] = 'expired'
                self.alerts[i] = alert
                count += 1
        
        return count
    
    def save_alerts(self, filepath):
        """
        Save alerts to a file.
        
        Args:
            filepath (str): Path to save the alerts
            
        Returns:
            str: Path where alerts were saved
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save alerts to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_alerts(self, filepath):
        """
        Load alerts from a file.
        
        Args:
            filepath (str): Path to the alerts file
            
        Returns:
            list: Loaded alerts
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.alerts = json.load(f)
            return self.alerts
        except FileNotFoundError:
            return []
    
    def _generate_alert_id(self):
        """
        Generate a unique alert ID.
        
        Returns:
            str: Unique ID
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = np.random.randint(1000, 9999)
        return f"alert_{timestamp}_{random_suffix}"


class AlertNotifier:
    """
    A class for sending notifications for triggered alerts.
    """
    
    def __init__(self, config=None):
        """
        Initialize the alert notifier.
        
        Args:
            config (dict): Configuration parameters
        """
        self.config = config or {}
    
    def set_config(self, config):
        """
        Set or update configuration.
        
        Args:
            config (dict): Configuration parameters
        """
        self.config = config
    
    def format_alert_message(self, alert, language='ar'):
        """
        Format an alert message for notification.
        
        Args:
            alert (dict): Alert details
            language (str): Language code ('ar' for Arabic, 'en' for English)
            
        Returns:
            str: Formatted message
        """
        if language == 'ar':
            # Arabic message formatting
            ticker = alert['ticker']
            
            if alert['type'] == 'price':
                direction = 'أعلى من' if alert['subtype'] == 'above' else 'أقل من'
                return f"تنبيه سعر {ticker}: السعر الحالي {alert['current_price']} {direction} {alert['target_price']}"
            
            elif alert['type'] == 'technical':
                indicator = alert['indicator']
                if alert['subtype'] == 'cross_above':
                    return f"تنبيه فني {ticker}: {indicator} تجاوز {alert['threshold']}"
                elif alert['subtype'] == 'cross_below':
                    return f"تنبيه فني {ticker}: {indicator} انخفض تحت {alert['threshold']}"
                else:
                    return f"تنبيه فني {ticker}: {indicator} {alert['subtype']}"
            
            elif alert['type'] == 'pattern':
                return f"تنبيه نمط {ticker}: تم اكتشاف {alert['subtype']} بثقة {alert['confidence']:.1%}"
            
            elif alert['type'] == 'fundamental':
                direction = 'أعلى من' if alert['subtype'] == 'above' else 'أقل من'
                return f"تنبيه أساسي {ticker}: {alert['metric']} {alert['current_value']} {direction} {alert['threshold']}"
            
            elif alert['type'] == 'news':
                importance = {'low': 'منخفضة', 'medium': 'متوسطة', 'high': 'عالية'}
                return f"تنبيه أخبار {ticker}: {alert['subtype']} من {alert['source']} (أهمية {importance[alert['importance']]})"
            
            elif alert['type'] == 'volume':
                return f"تنبيه حجم {ticker}: الحجم الحالي {alert['current_volume']:,.0f} أعلى بـ {alert['volume_ratio']:.1f} مرة من المتوسط"
            
            elif alert['type'] == 'volatility':
                return f"تنبيه تقلب {ticker}: التقلب الحالي أعلى بـ {alert['volatility_ratio']:.1f} مرة من المتوسط"
            
            elif alert['type'] == 'recommendation':
                return f"تغيير توصية {ticker}: من {alert['old_recommendation']} إلى {alert['new_recommendation']}"
            
            else:
                return alert['message']
        
        else:  # English
            return alert['message']
    
    def send_email_notification(self, alert, recipient_email):
        """
        Send an email notification for an alert.
        
        Args:
            alert (dict): Alert details
            recipient_email (str): Recipient email address
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # This would integrate with an email service
        # For now, just return a placeholder
        print(f"Email notification would be sent to {recipient_email} for alert: {alert['id']}")
        return True
    
    def send_sms_notification(self, alert, phone_number):
        """
        Send an SMS notification for an alert.
        
        Args:
            alert (dict): Alert details
            phone_number (str): Recipient phone number
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # This would integrate with an SMS service
        # For now, just return a placeholder
        print(f"SMS notification would be sent to {phone_number} for alert: {alert['id']}")
        return True
    
    def send_push_notification(self, alert, device_token):
        """
        Send a push notification for an alert.
        
        Args:
            alert (dict): Alert details
            device_token (str): Device token for push notification
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # This would integrate with a push notification service
        # For now, just return a placeholder
        print(f"Push notification would be sent to device {device_token} for alert: {alert['id']}")
        return True
    
    def send_notification(self, alert, notification_type, recipient, language='ar'):
        """
        Send a notification for an alert.
        
        Args:
            alert (dict): Alert details
            notification_type (str): 'email', 'sms', or 'push'
            recipient (str): Recipient identifier (email, phone, or device token)
            language (str): Language code
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Format message
        message = self.format_alert_message(alert, language)
        
        # Send notification based on type
        if notification_type == 'email':
            return self.send_email_notification(alert, recipient)
        elif notification_type == 'sms':
            return self.send_sms_notification(alert, recipient)
        elif notification_type == 'push':
            return self.send_push_notification(alert, recipient)
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")
    
    def send_batch_notifications(self, alerts, notification_type, recipients, language='ar'):
        """
        Send batch notifications for multiple alerts.
        
        Args:
            alerts (list): List of alert details
            notification_type (str): 'email', 'sms', or 'push'
            recipients (list): List of recipient identifiers
            language (str): Language code
            
        Returns:
            dict: Results for each recipient
        """
        results = {}
        
        for recipient in recipients:
            success_count = 0
            
            for alert in alerts:
                if self.send_notification(alert, notification_type, recipient, language):
                    success_count += 1
            
            results[recipient] = {
                'total': len(alerts),
                'success': success_count,
                'failed': len(alerts) - success_count
            }
        
        return results