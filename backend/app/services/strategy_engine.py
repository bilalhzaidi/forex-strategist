from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from ..models.models import RecommendationType
from ..models.schemas import TechnicalAnalysis, SentimentAnalysis, EventAnalysis

class StrategyEngine:
    def __init__(self):
        # Weights for different factors in decision making
        self.weights = {
            'technical': 0.4,
            'sentiment': 0.3,
            'events': 0.3
        }
        
        # Thresholds for buy/sell decisions
        self.buy_threshold = 0.6
        self.sell_threshold = -0.6
    
    def generate_recommendation(self, 
                              currency_pair: str,
                              technical_data: Dict,
                              sentiment_data: Dict,
                              current_rate: float) -> Dict:
        """Generate trading recommendation based on all factors"""
        
        # Calculate individual scores
        technical_score = self._calculate_technical_score(technical_data)
        sentiment_score = self._calculate_sentiment_score(sentiment_data)
        event_score = self._calculate_event_score(sentiment_data)
        
        # Calculate weighted overall score
        overall_score = (
            technical_score * self.weights['technical'] +
            sentiment_score * self.weights['sentiment'] +
            event_score * self.weights['events']
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(overall_score)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(technical_score, sentiment_score, event_score)
        
        # Generate justification
        justification = self._generate_justification(
            currency_pair, recommendation, technical_data, sentiment_data, 
            technical_score, sentiment_score, event_score, overall_score
        )
        
        return {
            'recommendation': recommendation,
            'confidence_score': confidence,
            'overall_score': overall_score,
            'technical_score': technical_score,
            'sentiment_score': sentiment_score,
            'event_score': event_score,
            'justification': justification
        }
    
    def _calculate_technical_score(self, technical_data: Dict) -> float:
        """Calculate score based on technical analysis (-1 to 1)"""
        score = 0.0
        factors = 0
        
        current_rate = technical_data.get('current_rate', 0)
        ma_5 = technical_data.get('moving_average_5')
        ma_20 = technical_data.get('moving_average_20')
        ma_50 = technical_data.get('moving_average_50')
        trend = technical_data.get('trend_direction', 'neutral')
        
        # Moving average analysis
        if ma_5 and ma_20 and current_rate > 0:
            # Price vs MA comparison
            if current_rate > ma_20:
                score += 0.3
            elif current_rate < ma_20:
                score -= 0.3
            factors += 1
            
            # MA crossover signals
            if ma_5 > ma_20:
                score += 0.2
            elif ma_5 < ma_20:
                score -= 0.2
            factors += 1
        
        if ma_20 and ma_50:
            # Long-term trend
            if ma_20 > ma_50:
                score += 0.2
            elif ma_20 < ma_50:
                score -= 0.2
            factors += 1
        
        # Trend direction
        if trend == 'upward':
            score += 0.3
        elif trend == 'downward':
            score -= 0.3
        factors += 1
        
        # Normalize score
        if factors > 0:
            score = score / factors
        
        return max(-1.0, min(1.0, score))
    
    def _calculate_sentiment_score(self, sentiment_data: Dict) -> float:
        """Calculate score based on sentiment analysis (-1 to 1)"""
        sentiment_score = sentiment_data.get('score', 0.0)
        news_count = sentiment_data.get('news_count', 0)
        
        # Adjust sentiment based on news volume
        if news_count > 10:
            # High news volume amplifies sentiment
            sentiment_score *= 1.2
        elif news_count < 3:
            # Low news volume dampens sentiment
            sentiment_score *= 0.5
        
        return max(-1.0, min(1.0, sentiment_score))
    
    def _calculate_event_score(self, sentiment_data: Dict) -> float:
        """Calculate score based on economic and geopolitical events (-1 to 1)"""
        economic_events = sentiment_data.get('economic_events', [])
        geopolitical_events = sentiment_data.get('geopolitical_events', [])
        
        score = 0.0
        
        # Economic events analysis
        for event in economic_events:
            event_lower = event.lower()
            if any(keyword in event_lower for keyword in ['rate cut', 'stimulus', 'growth']):
                score += 0.2
            elif any(keyword in event_lower for keyword in ['rate hike', 'inflation', 'recession']):
                score -= 0.2
        
        # Geopolitical events analysis
        for event in geopolitical_events:
            event_lower = event.lower()
            if any(keyword in event_lower for keyword in ['war', 'conflict', 'sanctions']):
                score -= 0.3
            elif any(keyword in event_lower for keyword in ['deal', 'agreement', 'stability']):
                score += 0.2
        
        return max(-1.0, min(1.0, score))
    
    def _determine_recommendation(self, overall_score: float) -> RecommendationType:
        """Determine buy/hold/sell recommendation based on overall score"""
        if overall_score >= self.buy_threshold:
            return RecommendationType.BUY
        elif overall_score <= self.sell_threshold:
            return RecommendationType.SELL
        else:
            return RecommendationType.HOLD
    
    def _calculate_confidence(self, technical_score: float, sentiment_score: float, event_score: float) -> float:
        """Calculate confidence score based on agreement between factors"""
        scores = [technical_score, sentiment_score, event_score]
        
        # Check alignment of scores
        positive_scores = sum(1 for score in scores if score > 0.1)
        negative_scores = sum(1 for score in scores if score < -0.1)
        neutral_scores = sum(1 for score in scores if -0.1 <= score <= 0.1)
        
        # High confidence when factors agree
        if positive_scores >= 2 and negative_scores == 0:
            confidence = 0.8 + (positive_scores - 2) * 0.1
        elif negative_scores >= 2 and positive_scores == 0:
            confidence = 0.8 + (negative_scores - 2) * 0.1
        elif neutral_scores >= 2:
            confidence = 0.6
        else:
            # Mixed signals reduce confidence
            confidence = 0.5
        
        # Adjust based on score magnitudes
        avg_magnitude = np.mean([abs(score) for score in scores])
        confidence *= (0.5 + avg_magnitude * 0.5)
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_justification(self, currency_pair: str, recommendation: RecommendationType,
                               technical_data: Dict, sentiment_data: Dict,
                               technical_score: float, sentiment_score: float,
                               event_score: float, overall_score: float) -> str:
        """Generate detailed justification for the recommendation"""
        
        justification = f"**Recommendation: {recommendation.value.upper()}** for {currency_pair}\n\n"
        justification += f"**Overall Score:** {overall_score:.3f}\n\n"
        
        # Technical Analysis Section
        justification += "**Technical Analysis:**\n"
        current_rate = technical_data.get('current_rate', 0)
        ma_20 = technical_data.get('moving_average_20')
        trend = technical_data.get('trend_direction', 'neutral')
        
        justification += f"- Current Rate: {current_rate:.4f}\n"
        if ma_20:
            justification += f"- 20-Day Moving Average: {ma_20:.4f}\n"
            if current_rate > ma_20:
                justification += "- Price is above MA20, indicating bullish momentum\n"
            else:
                justification += "- Price is below MA20, indicating bearish momentum\n"
        
        justification += f"- Trend Direction: {trend.title()}\n"
        justification += f"- Technical Score: {technical_score:.3f}\n\n"
        
        # Sentiment Analysis Section
        justification += "**Sentiment Analysis:**\n"
        sentiment_score_raw = sentiment_data.get('score', 0)
        news_count = sentiment_data.get('news_count', 0)
        
        justification += f"- News Articles Analyzed: {news_count}\n"
        justification += f"- Sentiment Score: {sentiment_score_raw:.3f}\n"
        
        if sentiment_score_raw > 0.1:
            justification += "- Market sentiment is positive\n"
        elif sentiment_score_raw < -0.1:
            justification += "- Market sentiment is negative\n"
        else:
            justification += "- Market sentiment is neutral\n"
        
        justification += f"- Weighted Sentiment Score: {sentiment_score:.3f}\n\n"
        
        # Event Analysis Section
        justification += "**Event Analysis:**\n"
        economic_events = sentiment_data.get('economic_events', [])
        geopolitical_events = sentiment_data.get('geopolitical_events', [])
        
        if economic_events:
            justification += f"- Economic Events: {len(economic_events)} detected\n"
            for event in economic_events[:2]:  # Show top 2
                justification += f"  • {event}\n"
        
        if geopolitical_events:
            justification += f"- Geopolitical Events: {len(geopolitical_events)} detected\n"
            for event in geopolitical_events[:2]:  # Show top 2
                justification += f"  • {event}\n"
        
        justification += f"- Event Impact Score: {event_score:.3f}\n\n"
        
        # Final Reasoning
        justification += "**Final Reasoning:**\n"
        
        if recommendation == RecommendationType.BUY:
            justification += "- Multiple factors align to suggest upward price movement\n"
            justification += "- Technical indicators show bullish signals\n"
            if sentiment_score > 0:
                justification += "- Positive market sentiment supports buying\n"
        elif recommendation == RecommendationType.SELL:
            justification += "- Multiple factors align to suggest downward price movement\n"
            justification += "- Technical indicators show bearish signals\n"
            if sentiment_score < 0:
                justification += "- Negative market sentiment supports selling\n"
        else:
            justification += "- Mixed signals suggest maintaining current position\n"
            justification += "- Wait for clearer market direction before taking action\n"
        
        return justification
    
    def update_strategy_weights(self, technical_weight: float, sentiment_weight: float, event_weight: float):
        """Update strategy weights (must sum to 1.0)"""
        total = technical_weight + sentiment_weight + event_weight
        if abs(total - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")
        
        self.weights['technical'] = technical_weight
        self.weights['sentiment'] = sentiment_weight
        self.weights['events'] = event_weight
    
    def update_thresholds(self, buy_threshold: float, sell_threshold: float):
        """Update buy/sell thresholds"""
        if buy_threshold <= sell_threshold:
            raise ValueError("Buy threshold must be greater than sell threshold")
        
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold