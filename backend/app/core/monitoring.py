import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import time
from typing import Dict, List
from datetime import datetime, timedelta
from .config import settings
from .logging import get_logger

logger = get_logger("monitoring")

def setup_sentry():
    """Configure Sentry for error tracking"""
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            environment=settings.ENVIRONMENT,
            release=settings.VERSION,
        )
        logger.info("Sentry monitoring configured", dsn=settings.SENTRY_DSN[:20] + "...")
    else:
        logger.warning("Sentry DSN not configured - error tracking disabled")

class MetricsCollector:
    """Simple metrics collector for monitoring application performance"""
    
    def __init__(self):
        self.request_count = 0
        self.request_duration_sum = 0.0
        self.request_durations: List[float] = []
        self.error_count = 0
        self.api_call_count = 0
        self.api_error_count = 0
        self.last_reset = datetime.now()
        self.recommendation_count = 0
        self.currency_pairs_analyzed: Dict[str, int] = {}
    
    def record_request(self, duration: float, status_code: int):
        """Record a request with its duration and status"""
        self.request_count += 1
        self.request_duration_sum += duration
        self.request_durations.append(duration)
        
        # Keep only last 1000 requests for memory efficiency
        if len(self.request_durations) > 1000:
            self.request_durations = self.request_durations[-1000:]
        
        if status_code >= 400:
            self.error_count += 1
    
    def record_api_call(self, success: bool = True):
        """Record an external API call"""
        self.api_call_count += 1
        if not success:
            self.api_error_count += 1
    
    def record_recommendation(self, currency_pair: str):
        """Record a recommendation generated"""
        self.recommendation_count += 1
        if currency_pair in self.currency_pairs_analyzed:
            self.currency_pairs_analyzed[currency_pair] += 1
        else:
            self.currency_pairs_analyzed[currency_pair] = 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics summary"""
        now = datetime.now()
        uptime = (now - self.last_reset).total_seconds()
        
        avg_duration = (
            self.request_duration_sum / self.request_count 
            if self.request_count > 0 else 0
        )
        
        p95_duration = (
            sorted(self.request_durations)[int(len(self.request_durations) * 0.95)]
            if self.request_durations else 0
        )
        
        error_rate = (
            (self.error_count / self.request_count) * 100
            if self.request_count > 0 else 0
        )
        
        api_error_rate = (
            (self.api_error_count / self.api_call_count) * 100
            if self.api_call_count > 0 else 0
        )
        
        return {
            "uptime_seconds": uptime,
            "requests": {
                "total": self.request_count,
                "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
                "avg_duration_ms": avg_duration * 1000,
                "p95_duration_ms": p95_duration * 1000,
                "error_count": self.error_count,
                "error_rate_percent": error_rate
            },
            "api_calls": {
                "total": self.api_call_count,
                "errors": self.api_error_count,
                "error_rate_percent": api_error_rate
            },
            "business": {
                "recommendations_generated": self.recommendation_count,
                "unique_pairs_analyzed": len(self.currency_pairs_analyzed),
                "top_currency_pairs": dict(
                    sorted(self.currency_pairs_analyzed.items(), 
                          key=lambda x: x[1], reverse=True)[:5]
                )
            },
            "timestamp": now.isoformat()
        }
    
    def reset_metrics(self):
        """Reset all metrics (useful for periodic reporting)"""
        self.__init__()

# Global metrics collector instance
metrics = MetricsCollector()

class HealthChecker:
    """Health check utilities"""
    
    @staticmethod
    async def check_database_health():
        """Check database connectivity"""
        try:
            from ..core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "details": "Database connection successful"}
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {"status": "unhealthy", "details": f"Database error: {str(e)}"}
    
    @staticmethod
    async def check_external_apis():
        """Check external API availability"""
        checks = {}
        
        # Check Alpha Vantage
        if settings.ALPHA_VANTAGE_API_KEY:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{settings.ALPHA_VANTAGE_BASE_URL}?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey={settings.ALPHA_VANTAGE_API_KEY}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            checks["alpha_vantage"] = {"status": "healthy", "response_time_ms": 0}
                        else:
                            checks["alpha_vantage"] = {"status": "unhealthy", "details": f"HTTP {response.status}"}
            except Exception as e:
                checks["alpha_vantage"] = {"status": "unhealthy", "details": str(e)}
        else:
            checks["alpha_vantage"] = {"status": "not_configured", "details": "API key not provided"}
        
        # Check News API
        if settings.NEWS_API_KEY:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{settings.NEWS_API_BASE_URL}/top-headlines?country=us&apiKey={settings.NEWS_API_KEY}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            checks["news_api"] = {"status": "healthy", "response_time_ms": 0}
                        else:
                            checks["news_api"] = {"status": "unhealthy", "details": f"HTTP {response.status}"}
            except Exception as e:
                checks["news_api"] = {"status": "unhealthy", "details": str(e)}
        else:
            checks["news_api"] = {"status": "not_configured", "details": "API key not provided"}
        
        return checks
    
    @staticmethod
    def get_system_info():
        """Get system information"""
        import psutil
        import platform
        
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION
        }