import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
import json
from textblob import TextBlob
import feedparser
from bs4 import BeautifulSoup
from ..core.config import settings

class NewsSentimentService:
    def __init__(self):
        self.news_api_key = settings.NEWS_API_KEY
        self.news_api_url = settings.NEWS_API_BASE_URL
        
        # Currency-related keywords for filtering
        self.currency_keywords = {
            'USD': ['dollar', 'usd', 'federal reserve', 'fed', 'united states'],
            'EUR': ['euro', 'eur', 'european central bank', 'ecb', 'eurozone'],
            'GBP': ['pound', 'gbp', 'sterling', 'bank of england', 'boe', 'brexit'],
            'JPY': ['yen', 'jpy', 'bank of japan', 'boj', 'japan'],
            'CHF': ['franc', 'chf', 'swiss national bank', 'snb', 'switzerland'],
            'CAD': ['canadian dollar', 'cad', 'bank of canada', 'boc', 'canada'],
            'AUD': ['australian dollar', 'aud', 'reserve bank of australia', 'rba', 'australia'],
            'NZD': ['new zealand dollar', 'nzd', 'reserve bank of new zealand', 'rbnz']
        }
        
        # Economic event keywords
        self.economic_keywords = [
            'interest rate', 'inflation', 'gdp', 'unemployment', 'employment',
            'trade war', 'tariff', 'economic growth', 'recession', 'stimulus',
            'monetary policy', 'fiscal policy', 'central bank', 'quantitative easing'
        ]
        
        # Geopolitical event keywords
        self.geopolitical_keywords = [
            'war', 'conflict', 'sanctions', 'election', 'political', 'trade deal',
            'diplomatic', 'military', 'terrorism', 'coup', 'brexit', 'pandemic'
        ]

    async def fetch_news_articles(self, currency_pair: str, days: int = 7) -> List[Dict]:
        """Fetch news articles related to the currency pair"""
        articles = []
        
        # Extract currencies from pair
        currencies = currency_pair.split('/')
        
        # Fetch from News API if available
        if self.news_api_key:
            news_api_articles = await self._fetch_from_news_api(currencies, days)
            articles.extend(news_api_articles)
        
        # Always fetch from RSS feeds as backup
        rss_articles = await self._fetch_from_rss_feeds(currencies, days)
        articles.extend(rss_articles)
        
        # Remove duplicates based on title similarity
        articles = self._remove_duplicate_articles(articles)
        
        return articles[:20]  # Limit to 20 most relevant articles
    
    async def _fetch_from_news_api(self, currencies: List[str], days: int) -> List[Dict]:
        """Fetch articles from News API"""
        articles = []
        
        # Build search query
        query_terms = []
        for currency in currencies:
            if currency in self.currency_keywords:
                query_terms.extend(self.currency_keywords[currency])
        
        query = ' OR '.join(query_terms[:5])  # Limit query terms
        
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'relevancy',
            'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'apiKey': self.news_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.news_api_url}/everything", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'ok':
                            for article in data.get('articles', [])[:10]:
                                articles.append({
                                    'title': article.get('title', ''),
                                    'content': article.get('description', ''),
                                    'source': article.get('source', {}).get('name', 'News API'),
                                    'url': article.get('url', ''),
                                    'published_at': self._parse_date(article.get('publishedAt', '')),
                                    'currency_pairs_mentioned': currencies
                                })
            except Exception as e:
                print(f"Error fetching from News API: {str(e)}")
        
        return articles
    
    async def _fetch_from_rss_feeds(self, currencies: List[str], days: int) -> List[Dict]:
        """Fetch articles from financial RSS feeds"""
        articles = []
        
        # Financial RSS feeds
        rss_feeds = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://www.reuters.com/finance/markets/rss',
            'https://www.forexfactory.com/rss',
            'https://www.fxstreet.com/rss/news'
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Limit per feed
                    # Check if article is relevant to currencies
                    title_lower = entry.title.lower()
                    description_lower = getattr(entry, 'description', '').lower()
                    
                    is_relevant = False
                    mentioned_currencies = []
                    
                    for currency in currencies:
                        if currency in self.currency_keywords:
                            for keyword in self.currency_keywords[currency]:
                                if keyword in title_lower or keyword in description_lower:
                                    is_relevant = True
                                    mentioned_currencies.append(currency)
                                    break
                    
                    if is_relevant:
                        articles.append({
                            'title': entry.title,
                            'content': getattr(entry, 'description', ''),
                            'source': feed.feed.get('title', 'RSS Feed'),
                            'url': entry.link,
                            'published_at': self._parse_date(getattr(entry, 'published', '')),
                            'currency_pairs_mentioned': mentioned_currencies
                        })
            except Exception as e:
                print(f"Error fetching RSS feed {feed_url}: {str(e)}")
                continue
        
        return articles
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze sentiment of news articles"""
        if not articles:
            return {
                'score': 0.0,
                'summary': 'No articles available for sentiment analysis',
                'news_count': 0
            }
        
        sentiment_scores = []
        economic_events = []
        geopolitical_events = []
        
        for article in articles:
            # Analyze sentiment of title and content
            text = f"{article.get('title', '')} {article.get('content', '')}"
            
            if text.strip():
                blob = TextBlob(text)
                sentiment_scores.append(blob.sentiment.polarity)
                
                # Categorize events
                text_lower = text.lower()
                
                # Check for economic events
                for keyword in self.economic_keywords:
                    if keyword in text_lower:
                        economic_events.append(f"{keyword.title()} mentioned in: {article.get('title', '')[:50]}...")
                        break
                
                # Check for geopolitical events
                for keyword in self.geopolitical_keywords:
                    if keyword in text_lower:
                        geopolitical_events.append(f"{keyword.title()} mentioned in: {article.get('title', '')[:50]}...")
                        break
        
        # Calculate overall sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # Generate summary
        summary = self._generate_sentiment_summary(avg_sentiment, len(articles), economic_events, geopolitical_events)
        
        return {
            'score': round(avg_sentiment, 3),
            'summary': summary,
            'news_count': len(articles),
            'economic_events': economic_events[:5],  # Top 5
            'geopolitical_events': geopolitical_events[:5]  # Top 5
        }
    
    def _generate_sentiment_summary(self, sentiment_score: float, article_count: int, 
                                  economic_events: List[str], geopolitical_events: List[str]) -> str:
        """Generate a human-readable sentiment summary"""
        if sentiment_score > 0.1:
            sentiment_text = "positive"
        elif sentiment_score < -0.1:
            sentiment_text = "negative"
        else:
            sentiment_text = "neutral"
        
        summary = f"Based on {article_count} news articles, market sentiment is {sentiment_text} "
        summary += f"(score: {sentiment_score:.3f}). "
        
        if economic_events:
            summary += f"Key economic factors include {len(economic_events)} relevant events. "
        
        if geopolitical_events:
            summary += f"Geopolitical factors include {len(geopolitical_events)} relevant events. "
        
        if sentiment_score > 0.2:
            summary += "Strong positive sentiment may support currency strength."
        elif sentiment_score < -0.2:
            summary += "Strong negative sentiment may weaken currency performance."
        else:
            summary += "Moderate sentiment suggests limited news impact on currency movement."
        
        return summary
    
    def _remove_duplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower()
            # Simple deduplication based on first 50 characters
            title_key = title[:50]
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Try other common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %Z']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None