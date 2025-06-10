from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class RecommendationType(enum.Enum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"

class ForexRecommendation(Base):
    __tablename__ = "forex_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    currency_pair = Column(String(10), nullable=False, index=True)
    recommendation = Column(Enum(RecommendationType), nullable=False)
    confidence_score = Column(Float, nullable=False)
    current_rate = Column(Float, nullable=False)
    
    # Technical Analysis
    technical_summary = Column(Text)
    moving_average_5 = Column(Float)
    moving_average_20 = Column(Float)
    moving_average_50 = Column(Float)
    trend_direction = Column(String(20))
    
    # Sentiment Analysis
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_summary = Column(Text)
    news_count = Column(Integer, default=0)
    
    # Event Analysis
    economic_events = Column(Text)
    geopolitical_events = Column(Text)
    event_impact_score = Column(Float)  # -1 to 1
    
    # Justification
    justification = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ForexRate(Base):
    __tablename__ = "forex_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    currency_pair = Column(String(10), nullable=False, index=True)
    rate = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50), default="alpha_vantage")

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(100))
    url = Column(String(1000))
    published_at = Column(DateTime)
    sentiment_score = Column(Float)
    currency_pairs_mentioned = Column(String(200))  # JSON string of currency pairs
    created_at = Column(DateTime(timezone=True), server_default=func.now())