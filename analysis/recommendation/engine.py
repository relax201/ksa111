"""
Recommendation Engine Module

This module provides a recommendation engine for generating stock recommendations
based on technical and fundamental analysis.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    A class for generating stock recommendations based on technical and fundamental analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the recommendation engine.
        
        Args:
            config: Configuration parameters for the recommendation engine
        """
        self.config = config or {
            'technical_weight': 0.5,
            'fundamental_weight': 0.5,
            'min_confidence': 70,
            'time_frames': ['short', 'medium', 'long'],
            'risk_levels': ['low', 'moderate', 'high']
        }
    
    def generate_recommendation(self, 
                               stock_data: Dict, 
                               technical_analysis: Dict, 
                               fundamental_analysis: Dict,
                               market_data: Optional[Dict] = None,
                               user_preferences: Optional[Dict] = None) -> Dict:
        """
        Generate a stock recommendation based on technical and fundamental analysis.
        
        Args:
            stock_data: Stock information
            technical_analysis: Technical analysis results
            fundamental_analysis: Fundamental analysis results
            market_data: Market data for context
            user_preferences: User preferences for recommendations
            
        Returns:
            Dict: Recommendation details
        """
        try:
            # Apply user preferences if provided
            if user_preferences:
                self._apply_user_preferences(user_preferences)
            
            # Generate technical recommendation
            technical_rec = self._generate_technical_recommendation(stock_data, technical_analysis)
            
            # Generate fundamental recommendation
            fundamental_rec = self._generate_fundamental_recommendation(stock_data, fundamental_analysis, market_data)
            
            # Combine recommendations
            combined_rec = self._combine_recommendations(technical_rec, fundamental_rec)
            
            # Add metadata
            combined_rec['stock'] = {
                'symbol': stock_data.get('symbol'),
                'name': stock_data.get('name'),
                'sector': stock_data.get('sector')
            }
            combined_rec['price'] = stock_data.get('price', 0)
            combined_rec['analysis_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate expiry date based on time frame
            expiry_days = {
                'short': 7,
                'medium': 30,
                'long': 90
            }.get(combined_rec['time_frame'], 30)
            
            combined_rec['expiry_date'] = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
            
            return combined_rec
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return {
                'status': 'error',
                'message': f"Failed to generate recommendation: {str(e)}",
                'stock': {
                    'symbol': stock_data.get('symbol'),
                    'name': stock_data.get('name')
                }
            }
    
    def _apply_user_preferences(self, preferences: Dict) -> None:
        """
        Apply user preferences to the recommendation engine.
        
        Args:
            preferences: User preferences
        """
        if 'technical_weight' in preferences:
            self.config['technical_weight'] = preferences['technical_weight']
            self.config['fundamental_weight'] = 1 - preferences['technical_weight']
        
        if 'min_confidence' in preferences:
            self.config['min_confidence'] = preferences['min_confidence']
        
        if 'preferred_time_frames' in preferences:
            self.config['time_frames'] = preferences['preferred_time_frames']
        
        if 'risk_level' in preferences:
            self.config['risk_level'] = preferences['risk_level']
    
    def _generate_technical_recommendation(self, stock_data: Dict, technical_analysis: Dict) -> Dict:
        """
        Generate a recommendation based on technical analysis.
        
        Args:
            stock_data: Stock information
            technical_analysis: Technical analysis results
            
        Returns:
            Dict: Technical recommendation
        """
        # Initialize recommendation
        recommendation = {
            'type': 'technical',
            'signals': {},
            'action': 'hold',
            'confidence': 0,
            'target_price': stock_data.get('price', 0),
            'stop_loss': stock_data.get('price', 0) * 0.95,  # Default 5% below current price
            'time_frame': 'medium',
            'notes': ''
        }
        
        # Extract signals from technical analysis
        signals = technical_analysis.get('signals', {})
        trend = technical_analysis.get('trend', 'neutral')
        support_resistance = technical_analysis.get('support_resistance', {})
        patterns = technical_analysis.get('patterns', [])
        
        # Count bullish and bearish signals
        bullish_signals = 0
        bearish_signals = 0
        neutral_signals = 0
        total_signals = 0
        signal_details = []
        
        # Process trend
        if trend == 'bullish':
            bullish_signals += 1
            signal_details.append("Overall trend is bullish")
        elif trend == 'bearish':
            bearish_signals += 1
            signal_details.append("Overall trend is bearish")
        else:
            neutral_signals += 1
            signal_details.append("Overall trend is neutral")
        
        total_signals += 1
        
        # Process moving averages
        if 'moving_averages' in signals:
            ma_signals = signals['moving_averages']
            
            if ma_signals.get('sma_crossover') == 'bullish':
                bullish_signals += 1
                signal_details.append("SMA crossover is bullish")
            elif ma_signals.get('sma_crossover') == 'bearish':
                bearish_signals += 1
                signal_details.append("SMA crossover is bearish")
            
            if ma_signals.get('ema_crossover') == 'bullish':
                bullish_signals += 1
                signal_details.append("EMA crossover is bullish")
            elif ma_signals.get('ema_crossover') == 'bearish':
                bearish_signals += 1
                signal_details.append("EMA crossover is bearish")
            
            if ma_signals.get('price_above_ma') == True:
                bullish_signals += 1
                signal_details.append("Price is above major moving averages")
            elif ma_signals.get('price_above_ma') == False:
                bearish_signals += 1
                signal_details.append("Price is below major moving averages")
            
            total_signals += 3
        
        # Process oscillators
        if 'oscillators' in signals:
            osc_signals = signals['oscillators']
            
            if osc_signals.get('rsi') == 'oversold':
                bullish_signals += 1
                signal_details.append("RSI indicates oversold conditions")
            elif osc_signals.get('rsi') == 'overbought':
                bearish_signals += 1
                signal_details.append("RSI indicates overbought conditions")
            
            if osc_signals.get('macd') == 'bullish':
                bullish_signals += 1
                signal_details.append("MACD is bullish")
            elif osc_signals.get('macd') == 'bearish':
                bearish_signals += 1
                signal_details.append("MACD is bearish")
            
            if osc_signals.get('stochastic') == 'bullish':
                bullish_signals += 1
                signal_details.append("Stochastic oscillator is bullish")
            elif osc_signals.get('stochastic') == 'bearish':
                bearish_signals += 1
                signal_details.append("Stochastic oscillator is bearish")
            
            total_signals += 3
        
        # Process patterns
        if patterns:
            bullish_patterns = sum(1 for p in patterns if p.get('type') == 'bullish')
            bearish_patterns = sum(1 for p in patterns if p.get('type') == 'bearish')
            
            if bullish_patterns > bearish_patterns:
                bullish_signals += 1
                signal_details.append(f"Found {bullish_patterns} bullish patterns")
            elif bearish_patterns > bullish_patterns:
                bearish_signals += 1
                signal_details.append(f"Found {bearish_patterns} bearish patterns")
            
            total_signals += 1
        
        # Process support and resistance
        if support_resistance:
            current_price = stock_data.get('price', 0)
            
            # Find nearest support and resistance
            supports = support_resistance.get('support', [])
            resistances = support_resistance.get('resistance', [])
            
            nearest_support = max([s for s in supports if s < current_price], default=current_price * 0.9)
            nearest_resistance = min([r for r in resistances if r > current_price], default=current_price * 1.1)
            
            # Calculate distance to support and resistance
            support_distance = (current_price - nearest_support) / current_price
            resistance_distance = (nearest_resistance - current_price) / current_price
            
            # If price is closer to resistance than support, it's more bearish
            if resistance_distance < support_distance:
                bearish_signals += 1
                signal_details.append(f"Price is closer to resistance ({nearest_resistance:.2f}) than support")
            else:
                bullish_signals += 1
                signal_details.append(f"Price is closer to support ({nearest_support:.2f}) than resistance")
            
            # Set target price and stop loss based on support and resistance
            recommendation['target_price'] = nearest_resistance
            recommendation['stop_loss'] = nearest_support
            
            total_signals += 1
        
        # Determine action and confidence
        if total_signals > 0:
            bullish_percentage = (bullish_signals / total_signals) * 100
            bearish_percentage = (bearish_signals / total_signals) * 100
            
            if bullish_percentage > 60:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = int(bullish_percentage)
                recommendation['notes'] = "Technical analysis indicates a bullish trend. " + " ".join(signal_details)
            elif bearish_percentage > 60:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = int(bearish_percentage)
                recommendation['notes'] = "Technical analysis indicates a bearish trend. " + " ".join(signal_details)
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = int(100 - abs(bullish_percentage - bearish_percentage))
                recommendation['notes'] = "Technical analysis indicates a neutral trend. " + " ".join(signal_details)
        
        # Determine time frame based on signals
        if 'moving_averages' in signals:
            ma_signals = signals['moving_averages']
            
            if ma_signals.get('long_term_trend') == 'bullish' or ma_signals.get('long_term_trend') == 'bearish':
                recommendation['time_frame'] = 'long'
            elif ma_signals.get('medium_term_trend') == 'bullish' or ma_signals.get('medium_term_trend') == 'bearish':
                recommendation['time_frame'] = 'medium'
            else:
                recommendation['time_frame'] = 'short'
        
        recommendation['signals'] = signal_details
        
        return recommendation
    
    def _generate_fundamental_recommendation(self, stock_data: Dict, fundamental_analysis: Dict, 
                                           market_data: Optional[Dict] = None) -> Dict:
        """
        Generate a recommendation based on fundamental analysis.
        
        Args:
            stock_data: Stock information
            fundamental_analysis: Fundamental analysis results
            market_data: Market data for context
            
        Returns:
            Dict: Fundamental recommendation
        """
        # Initialize recommendation
        recommendation = {
            'type': 'fundamental',
            'signals': {},
            'action': 'hold',
            'confidence': 0,
            'target_price': stock_data.get('price', 0),
            'stop_loss': stock_data.get('price', 0) * 0.9,  # Default 10% below current price
            'time_frame': 'long',
            'notes': ''
        }
        
        # Extract data from fundamental analysis
        valuation = fundamental_analysis.get('valuation', {})
        ratios = fundamental_analysis.get('ratios', {})
        growth = fundamental_analysis.get('growth', {})
        peer_comparison = fundamental_analysis.get('peer_comparison', {})
        
        # Count positive and negative signals
        positive_signals = 0
        negative_signals = 0
        neutral_signals = 0
        total_signals = 0
        signal_details = []
        
        # Process valuation metrics
        if valuation:
            current_price = stock_data.get('price', 0)
            fair_value = valuation.get('fair_value', current_price)
            
            # Calculate valuation gap
            valuation_gap = (fair_value - current_price) / current_price
            
            if valuation_gap > 0.2:  # Undervalued by more than 20%
                positive_signals += 1
                signal_details.append(f"Stock is undervalued by {valuation_gap*100:.1f}%")
            elif valuation_gap < -0.2:  # Overvalued by more than 20%
                negative_signals += 1
                signal_details.append(f"Stock is overvalued by {-valuation_gap*100:.1f}%")
            else:
                neutral_signals += 1
                signal_details.append("Stock is fairly valued")
            
            # Set target price based on fair value
            recommendation['target_price'] = fair_value
            
            total_signals += 1
        
        # Process financial ratios
        if ratios:
            # Check P/E ratio
            pe_ratio = ratios.get('pe_ratio')
            sector_pe = ratios.get('sector_average', {}).get('pe_ratio')
            
            if pe_ratio and sector_pe:
                if pe_ratio < sector_pe * 0.8:
                    positive_signals += 1
                    signal_details.append(f"P/E ratio ({pe_ratio:.2f}) is below sector average ({sector_pe:.2f})")
                elif pe_ratio > sector_pe * 1.2:
                    negative_signals += 1
                    signal_details.append(f"P/E ratio ({pe_ratio:.2f}) is above sector average ({sector_pe:.2f})")
                
                total_signals += 1
            
            # Check ROE
            roe = ratios.get('roe')
            sector_roe = ratios.get('sector_average', {}).get('roe')
            
            if roe and sector_roe:
                if roe > sector_roe * 1.2:
                    positive_signals += 1
                    signal_details.append(f"ROE ({roe*100:.1f}%) is above sector average ({sector_roe*100:.1f}%)")
                elif roe < sector_roe * 0.8:
                    negative_signals += 1
                    signal_details.append(f"ROE ({roe*100:.1f}%) is below sector average ({sector_roe*100:.1f}%)")
                
                total_signals += 1
            
            # Check debt to equity
            debt_to_equity = ratios.get('debt_to_equity')
            sector_debt_to_equity = ratios.get('sector_average', {}).get('debt_to_equity')
            
            if debt_to_equity is not None and sector_debt_to_equity:
                if debt_to_equity < sector_debt_to_equity * 0.8:
                    positive_signals += 1
                    signal_details.append(f"Debt to equity ({debt_to_equity:.2f}) is below sector average ({sector_debt_to_equity:.2f})")
                elif debt_to_equity > sector_debt_to_equity * 1.2:
                    negative_signals += 1
                    signal_details.append(f"Debt to equity ({debt_to_equity:.2f}) is above sector average ({sector_debt_to_equity:.2f})")
                
                total_signals += 1
        
        # Process growth metrics
        if growth:
            revenue_growth = growth.get('revenue_growth')
            earnings_growth = growth.get('earnings_growth')
            
            if revenue_growth is not None:
                if revenue_growth > 0.1:  # 10% growth
                    positive_signals += 1
                    signal_details.append(f"Strong revenue growth ({revenue_growth*100:.1f}%)")
                elif revenue_growth < 0:
                    negative_signals += 1
                    signal_details.append(f"Negative revenue growth ({revenue_growth*100:.1f}%)")
                
                total_signals += 1
            
            if earnings_growth is not None:
                if earnings_growth > 0.15:  # 15% growth
                    positive_signals += 1
                    signal_details.append(f"Strong earnings growth ({earnings_growth*100:.1f}%)")
                elif earnings_growth < 0:
                    negative_signals += 1
                    signal_details.append(f"Negative earnings growth ({earnings_growth*100:.1f}%)")
                
                total_signals += 1
        
        # Process peer comparison
        if peer_comparison:
            better_than_peers = peer_comparison.get('better_than_peers', 0)
            worse_than_peers = peer_comparison.get('worse_than_peers', 0)
            
            if better_than_peers > worse_than_peers:
                positive_signals += 1
                signal_details.append(f"Outperforms peers in {better_than_peers} metrics")
            elif worse_than_peers > better_than_peers:
                negative_signals += 1
                signal_details.append(f"Underperforms peers in {worse_than_peers} metrics")
            
            total_signals += 1
        
        # Determine action and confidence
        if total_signals > 0:
            positive_percentage = (positive_signals / total_signals) * 100
            negative_percentage = (negative_signals / total_signals) * 100
            
            if positive_percentage > 60:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = int(positive_percentage)
                recommendation['notes'] = "Fundamental analysis indicates positive outlook. " + " ".join(signal_details)
            elif negative_percentage > 60:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = int(negative_percentage)
                recommendation['notes'] = "Fundamental analysis indicates negative outlook. " + " ".join(signal_details)
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = int(100 - abs(positive_percentage - negative_percentage))
                recommendation['notes'] = "Fundamental analysis indicates mixed outlook. " + " ".join(signal_details)
        
        recommendation['signals'] = signal_details
        
        return recommendation
    
    def _combine_recommendations(self, technical_rec: Dict, fundamental_rec: Dict) -> Dict:
        """
        Combine technical and fundamental recommendations.
        
        Args:
            technical_rec: Technical recommendation
            fundamental_rec: Fundamental recommendation
            
        Returns:
            Dict: Combined recommendation
        """
        # Initialize combined recommendation
        combined_rec = {
            'type': 'mixed',
            'action': 'hold',
            'confidence': 0,
            'target_price': 0,
            'stop_loss': 0,
            'time_frame': 'medium',
            'notes': '',
            'technical_signals': technical_rec.get('signals', []),
            'fundamental_signals': fundamental_rec.get('signals', [])
        }
        
        # Get weights
        tech_weight = self.config.get('technical_weight', 0.5)
        fund_weight = self.config.get('fundamental_weight', 0.5)
        
        # Determine action based on weighted confidence
        tech_confidence = technical_rec.get('confidence', 0)
        fund_confidence = fundamental_rec.get('confidence', 0)
        
        tech_action = technical_rec.get('action', 'hold')
        fund_action = fundamental_rec.get('action', 'hold')
        
        # Calculate weighted confidence for each action
        buy_confidence = 0
        sell_confidence = 0
        hold_confidence = 0
        
        if tech_action == 'buy':
            buy_confidence += tech_confidence * tech_weight
        elif tech_action == 'sell':
            sell_confidence += tech_confidence * tech_weight
        else:
            hold_confidence += tech_confidence * tech_weight
        
        if fund_action == 'buy':
            buy_confidence += fund_confidence * fund_weight
        elif fund_action == 'sell':
            sell_confidence += fund_confidence * fund_weight
        else:
            hold_confidence += fund_confidence * fund_weight
        
        # Determine final action
        max_confidence = max(buy_confidence, sell_confidence, hold_confidence)
        
        if max_confidence == buy_confidence:
            combined_rec['action'] = 'buy'
            combined_rec['confidence'] = int(buy_confidence)
        elif max_confidence == sell_confidence:
            combined_rec['action'] = 'sell'
            combined_rec['confidence'] = int(sell_confidence)
        else:
            combined_rec['action'] = 'hold'
            combined_rec['confidence'] = int(hold_confidence)
        
        # Set target price and stop loss
        if combined_rec['action'] == 'buy':
            # For buy, use the higher target price
            combined_rec['target_price'] = max(
                technical_rec.get('target_price', 0),
                fundamental_rec.get('target_price', 0)
            )
            # For buy, use the higher stop loss (more conservative)
            combined_rec['stop_loss'] = max(
                technical_rec.get('stop_loss', 0),
                fundamental_rec.get('stop_loss', 0)
            )
        elif combined_rec['action'] == 'sell':
            # For sell, use the lower target price
            combined_rec['target_price'] = min(
                technical_rec.get('target_price', float('inf')),
                fundamental_rec.get('target_price', float('inf'))
            )
            # For sell, use the lower stop loss
            combined_rec['stop_loss'] = min(
                technical_rec.get('stop_loss', float('inf')),
                fundamental_rec.get('stop_loss', float('inf'))
            )
        else:
            # For hold, average the values
            combined_rec['target_price'] = (
                technical_rec.get('target_price', 0) * tech_weight +
                fundamental_rec.get('target_price', 0) * fund_weight
            )
            combined_rec['stop_loss'] = (
                technical_rec.get('stop_loss', 0) * tech_weight +
                fundamental_rec.get('stop_loss', 0) * fund_weight
            )
        
        # Determine time frame
        # For mixed recommendations, prefer the longer time frame
        time_frames = ['short', 'medium', 'long']
        tech_time_frame = technical_rec.get('time_frame', 'medium')
        fund_time_frame = fundamental_rec.get('time_frame', 'long')
        
        tech_time_index = time_frames.index(tech_time_frame)
        fund_time_index = time_frames.index(fund_time_frame)
        
        combined_rec['time_frame'] = time_frames[max(tech_time_index, fund_time_index)]
        
        # Generate combined notes
        combined_rec['notes'] = f"Combined recommendation based on technical ({tech_weight*100:.0f}%) and fundamental ({fund_weight*100:.0f}%) analysis. "
        
        if combined_rec['action'] == 'buy':
            combined_rec['notes'] += f"Target price: {combined_rec['target_price']:.2f}, Stop loss: {combined_rec['stop_loss']:.2f}. "
        elif combined_rec['action'] == 'sell':
            combined_rec['notes'] += f"Target price: {combined_rec['target_price']:.2f}, Stop loss: {combined_rec['stop_loss']:.2f}. "
        
        # Add key signals
        if technical_rec.get('signals'):
            combined_rec['notes'] += f"Technical signals: {', '.join(technical_rec['signals'][:2])}. "
        
        if fundamental_rec.get('signals'):
            combined_rec['notes'] += f"Fundamental signals: {', '.join(fundamental_rec['signals'][:2])}."
        
        return combined_rec
    
    def generate_portfolio_recommendations(self, portfolio: Dict, 
                                         stock_data: Dict[str, Dict],
                                         technical_analysis: Dict[str, Dict],
                                         fundamental_analysis: Dict[str, Dict],
                                         market_data: Optional[Dict] = None,
                                         user_preferences: Optional[Dict] = None) -> List[Dict]:
        """
        Generate recommendations for a portfolio of stocks.
        
        Args:
            portfolio: Portfolio information
            stock_data: Stock information for each stock in the portfolio
            technical_analysis: Technical analysis results for each stock
            fundamental_analysis: Fundamental analysis results for each stock
            market_data: Market data for context
            user_preferences: User preferences for recommendations
            
        Returns:
            List[Dict]: List of recommendations for each stock in the portfolio
        """
        recommendations = []
        
        for stock in portfolio.get('stocks', []):
            symbol = stock.get('symbol')
            
            if symbol in stock_data and symbol in technical_analysis and symbol in fundamental_analysis:
                recommendation = self.generate_recommendation(
                    stock_data[symbol],
                    technical_analysis[symbol],
                    fundamental_analysis[symbol],
                    market_data,
                    user_preferences
                )
                
                recommendations.append(recommendation)
        
        # Sort recommendations by confidence
        recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return recommendations
    
    def filter_recommendations(self, recommendations: List[Dict], filters: Optional[Dict] = None) -> List[Dict]:
        """
        Filter recommendations based on criteria.
        
        Args:
            recommendations: List of recommendations
            filters: Filter criteria
            
        Returns:
            List[Dict]: Filtered recommendations
        """
        if not filters:
            return recommendations
        
        filtered_recs = recommendations.copy()
        
        # Filter by action
        if 'action' in filters:
            filtered_recs = [r for r in filtered_recs if r.get('action') == filters['action']]
        
        # Filter by minimum confidence
        if 'min_confidence' in filters:
            filtered_recs = [r for r in filtered_recs if r.get('confidence', 0) >= filters['min_confidence']]
        
        # Filter by type
        if 'type' in filters:
            filtered_recs = [r for r in filtered_recs if r.get('type') == filters['type']]
        
        # Filter by time frame
        if 'time_frame' in filters:
            filtered_recs = [r for r in filtered_recs if r.get('time_frame') == filters['time_frame']]
        
        # Filter by sector
        if 'sector' in filters:
            filtered_recs = [r for r in filtered_recs if r.get('stock', {}).get('sector') == filters['sector']]
        
        return filtered_recs