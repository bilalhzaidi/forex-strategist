from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv
import json

# Load environment-specific .env file
env = os.getenv("ENVIRONMENT", "development")
if env == "production":
    load_dotenv(".env.production")
elif env == "staging":
    load_dotenv(".env.staging")
else:
    load_dotenv(".env")

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALLOWED_HOSTS: List[str] = json.loads(os.getenv("ALLOWED_HOSTS", '["localhost", "127.0.0.1"]'))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./forex_advisor.db")
    
    # API Configuration
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    
    # Application
    APP_NAME: str = "Forex Trading Advisor"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered Forex Trading Advisor providing buy/hold/sell recommendations"
    
    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = json.loads(os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000", "http://127.0.0.1:3000"]'))
    
    # Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    MAX_REQUESTS_PER_DAY: int = int(os.getenv("MAX_REQUESTS_PER_DAY", "1000"))
    
    # Caching
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # API Timeouts
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()