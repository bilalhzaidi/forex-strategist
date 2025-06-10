from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.schemas import (
    CurrencyPairRequest, ForexRecommendationResponse, 
    HealthResponse, TechnicalAnalysis, SentimentAnalysis, EventAnalysis
)
from ..models.models import ForexRecommendation, ForexRate, NewsArticle
from ..services.forex_api import ForexAPIService
from ..services.news_sentiment import NewsSentimentService
from ..services.strategy_engine import StrategyEngine

router = APIRouter()

# Initialize services
forex_service = ForexAPIService()
news_service = NewsSentimentService()
strategy_engine = StrategyEngine()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Forex Trading Advisor API is running",
        timestamp=datetime.now()
    )


@router.post("/analyze", response_model=ForexRecommendationResponse)
async def analyze_currency_pair(
    request: CurrencyPairRequest,
    db: Session = Depends(get_db)
):
    """Analyze a currency pair and provide trading recommendation"""
    try:
        currency_pair = request.currency_pair.upper()
        
        # Validate currency pair format
        if '/' not in currency_pair:
            raise HTTPException(status_code=400, detail="Currency pair must be in format 'USD/EUR'")
        
        currencies = currency_pair.split('/')
        if len(currencies) != 2 or len(currencies[0]) != 3 or len(currencies[1]) != 3:
            raise HTTPException(status_code=400, detail="Invalid currency pair format")
        
        # Get technical analysis
        technical_data = await forex_service.get_technical_analysis(currency_pair)
        if technical_data['current_rate'] == 0:
            raise HTTPException(status_code=503, detail="Unable to fetch forex data. Please check API configuration.")
        
        # Get news and sentiment analysis
        news_articles = await news_service.fetch_news_articles(currency_pair)
        sentiment_data = news_service.analyze_sentiment(news_articles)
        
        # Generate recommendation using strategy engine
        recommendation_data = strategy_engine.generate_recommendation(
            currency_pair, technical_data, sentiment_data, technical_data['current_rate']
        )
        
        # Create response objects
        technical_analysis = TechnicalAnalysis(
            moving_average_5=technical_data.get('moving_average_5'),
            moving_average_20=technical_data.get('moving_average_20'),
            moving_average_50=technical_data.get('moving_average_50'),
            trend_direction=technical_data.get('trend_direction'),
            summary=technical_data.get('summary')
        )
        
        sentiment_analysis = SentimentAnalysis(
            score=sentiment_data.get('score', 0.0),
            summary=sentiment_data.get('summary', ''),
            news_count=sentiment_data.get('news_count', 0)
        )
        
        event_analysis = EventAnalysis(
            economic_events='; '.join(sentiment_data.get('economic_events', [])),
            geopolitical_events='; '.join(sentiment_data.get('geopolitical_events', [])),
            impact_score=recommendation_data.get('event_score', 0.0)
        )
        
        # Save to database
        db_recommendation = ForexRecommendation(
            currency_pair=currency_pair,
            recommendation=recommendation_data['recommendation'],
            confidence_score=recommendation_data['confidence_score'],
            current_rate=technical_data['current_rate'],
            technical_summary=technical_data.get('summary', ''),
            moving_average_5=technical_data.get('moving_average_5'),
            moving_average_20=technical_data.get('moving_average_20'),
            moving_average_50=technical_data.get('moving_average_50'),
            trend_direction=technical_data.get('trend_direction'),
            sentiment_score=sentiment_data.get('score', 0.0),
            sentiment_summary=sentiment_data.get('summary', ''),
            news_count=sentiment_data.get('news_count', 0),
            economic_events='; '.join(sentiment_data.get('economic_events', [])),
            geopolitical_events='; '.join(sentiment_data.get('geopolitical_events', [])),
            event_impact_score=recommendation_data.get('event_score', 0.0),
            justification=recommendation_data['justification']
        )
        
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        
        # Save news articles
        for article in news_articles[:10]:  # Save top 10 articles
            db_article = NewsArticle(
                title=article.get('title', ''),
                content=article.get('content', ''),
                source=article.get('source', ''),
                url=article.get('url', ''),
                published_at=article.get('published_at'),
                sentiment_score=sentiment_data.get('score', 0.0),
                currency_pairs_mentioned=currency_pair
            )
            db.add(db_article)
        
        db.commit()
        
        # Return response
        return ForexRecommendationResponse(
            currency_pair=currency_pair,
            recommendation=recommendation_data['recommendation'],
            confidence_score=recommendation_data['confidence_score'],
            current_rate=technical_data['current_rate'],
            technical_analysis=technical_analysis,
            sentiment_analysis=sentiment_analysis,
            event_analysis=event_analysis,
            justification=recommendation_data['justification'],
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{currency_pair}")
async def get_recommendation_history(
    currency_pair: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get historical recommendations for a currency pair"""
    recommendations = db.query(ForexRecommendation)\
        .filter(ForexRecommendation.currency_pair == currency_pair.upper())\
        .order_by(ForexRecommendation.created_at.desc())\
        .limit(limit)\
        .all()
    
    return recommendations


@router.get("/rates/{currency_pair}")
async def get_current_rate(currency_pair: str):
    """Get current exchange rate for a currency pair"""
    try:
        from_currency, to_currency = currency_pair.upper().split('/')
        rate_data = await forex_service.get_exchange_rate(from_currency, to_currency)
        
        if not rate_data:
            raise HTTPException(status_code=503, detail="Unable to fetch exchange rate")
        
        return rate_data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid currency pair format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rate: {str(e)}")


@router.get("/news/{currency_pair}")
async def get_currency_news(currency_pair: str, days: int = 7):
    """Get recent news articles for a currency pair"""
    try:
        articles = await news_service.fetch_news_articles(currency_pair.upper(), days)
        return {"articles": articles, "count": len(articles)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")


@router.get("/supported-pairs")
async def get_supported_pairs():
    """Get list of supported currency pairs"""
    major_pairs = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
        "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
        "EUR/JPY", "GBP/JPY", "CHF/JPY", "EUR/CHF",
        "AUD/JPY", "GBP/CHF", "AUD/NZD"
    ]
    
    return {"supported_pairs": major_pairs, "count": len(major_pairs)}