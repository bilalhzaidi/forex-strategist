import json
import hashlib
from typing import Optional, Any, Dict
import redis.asyncio as redis
from .config import settings
from .logging import get_logger

logger = get_logger("cache")

class CacheManager:
    """Redis-based caching with fallback to memory"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Any] = {}
        self.is_connected = False
    
    async def connect(self):
        """Connect to Redis if available"""
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                await self.redis_client.ping()
                self.is_connected = True
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning("Redis connection failed, using memory cache", error=str(e))
                self.redis_client = None
                self.is_connected = False
        else:
            logger.info("Redis URL not configured, using memory cache")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.is_connected and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to memory cache
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized_value = json.dumps(value, default=str)
            
            if self.is_connected and self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                # Fallback to memory cache (simple, no TTL)
                self.memory_cache[key] = value
                # Keep memory cache size limited
                if len(self.memory_cache) > 100:
                    # Remove oldest items
                    keys_to_remove = list(self.memory_cache.keys())[:20]
                    for k in keys_to_remove:
                        del self.memory_cache[k]
            
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.is_connected and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix"""
        count = 0
        try:
            if self.is_connected and self.redis_client:
                keys = await self.redis_client.keys(f"{prefix}:*")
                if keys:
                    count = await self.redis_client.delete(*keys)
            else:
                # Memory cache
                keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{prefix}:")]
                for k in keys_to_remove:
                    del self.memory_cache[k]
                count = len(keys_to_remove)
            
            logger.info("Cache cleared", prefix=prefix, count=count)
        except Exception as e:
            logger.error("Cache clear failed", prefix=prefix, error=str(e))
        
        return count

# Global cache instance
cache = CacheManager()

class CacheKeys:
    """Cache key constants"""
    FOREX_RATE = "forex_rate"
    FOREX_ANALYSIS = "forex_analysis"
    NEWS_ARTICLES = "news_articles"
    SUPPORTED_PAIRS = "supported_pairs"

def cache_key_for_forex_rate(from_currency: str, to_currency: str) -> str:
    """Generate cache key for forex rate"""
    return cache._generate_key(CacheKeys.FOREX_RATE, from_currency=from_currency, to_currency=to_currency)

def cache_key_for_analysis(currency_pair: str) -> str:
    """Generate cache key for forex analysis"""
    return cache._generate_key(CacheKeys.FOREX_ANALYSIS, currency_pair=currency_pair)

def cache_key_for_news(currency_pair: str, days: int = 7) -> str:
    """Generate cache key for news articles"""
    return cache._generate_key(CacheKeys.NEWS_ARTICLES, currency_pair=currency_pair, days=days)