from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RecommendationType(str, Enum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"

class CurrencyPairRequest(BaseModel):
    currency_pair: str

class TechnicalAnalysis(BaseModel):
    moving_average_5: Optional[float] = None
    moving_average_20: Optional[float] = None
    moving_average_50: Optional[float] = None
    trend_direction: Optional[str] = None
    summary: Optional[str] = None

class SentimentAnalysis(BaseModel):
    score: float  # -1 to 1
    summary: str
    news_count: int

class EventAnalysis(BaseModel):
    economic_events: Optional[str] = None
    geopolitical_events: Optional[str] = None
    impact_score: float  # -1 to 1

class ForexRecommendationResponse(BaseModel):
    currency_pair: str
    recommendation: RecommendationType
    confidence_score: float
    current_rate: float
    technical_analysis: TechnicalAnalysis
    sentiment_analysis: SentimentAnalysis
    event_analysis: EventAnalysis
    justification: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ForexRateResponse(BaseModel):
    currency_pair: str
    rate: float
    timestamp: datetime
    source: str

    class Config:
        from_attributes = True

class NewsArticleResponse(BaseModel):
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    currency_pairs_mentioned: Optional[List[str]] = None

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime