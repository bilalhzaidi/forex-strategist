from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
from starlette.middleware.base import BaseHTTPMiddleware

from .core.config import settings
from .core.database import create_tables
from .core.logging import setup_logging, get_logger
from .core.monitoring import setup_sentry, metrics, HealthChecker
from .core.cache import cache
from .middleware.security import (
    SecurityHeadersMiddleware, 
    RateLimitMiddleware, 
    RequestLoggingMiddleware,
    APIKeyValidationMiddleware
)
from .api.routes import router

# Setup logging first
setup_logging()
logger = get_logger("main")

# Setup monitoring
setup_sentry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Forex Trading Advisor", version=settings.VERSION, environment=settings.ENVIRONMENT)
    
    try:
        # Initialize database
        create_tables()
        logger.info("Database initialized successfully")
        
        # Initialize cache
        await cache.connect()
        logger.info("Cache initialized successfully")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await cache.disconnect()
        logger.info("Cache disconnected")
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Security middleware
if settings.is_production:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.REQUESTS_PER_MINUTE)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(APIKeyValidationMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Metrics middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Record metrics
        metrics.record_request(process_time, response.status_code)
        
        return response

app.add_middleware(MetricsMiddleware)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error", path=request.url.path, errors=str(exc.errors()))
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "message": "Please check your request parameters"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP exception", path=request.url.path, status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error("Internal server error", path=request.url.path, error=str(exc), exc_info=True)
    
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["forex"])

# Health and monitoring endpoints
@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs": "/docs" if settings.is_development else "disabled",
        "health": "/api/v1/health"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    if settings.is_production:
        # In production, you might want to restrict access to this endpoint
        return {"error": "Metrics endpoint disabled in production"}
    
    return metrics.get_metrics()

@app.get("/api/v1/system/health")
async def detailed_health_check():
    """Detailed health check with dependency status"""
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
    
    try:
        # Check database
        db_health = await HealthChecker.check_database_health()
        health_data["database"] = db_health
        
        # Check external APIs
        api_health = await HealthChecker.check_external_apis()
        health_data["external_apis"] = api_health
        
        # Check system info
        if settings.is_development:
            health_data["system"] = HealthChecker.get_system_info()
        
        # Determine overall health
        if db_health["status"] != "healthy":
            health_data["status"] = "unhealthy"
        
        # Check if any critical external APIs are down
        critical_apis = ["alpha_vantage"]
        for api in critical_apis:
            if api in api_health and api_health[api]["status"] == "unhealthy":
                health_data["status"] = "degraded"
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        health_data["status"] = "unhealthy"
        health_data["error"] = str(e)
    
    status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
    return JSONResponse(status_code=status_code, content=health_data)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"Path '{request.url.path}' not found",
            "available_endpoints": [
                "/api/v1/health",
                "/api/v1/analyze",
                "/api/v1/rates/{currency_pair}",
                "/api/v1/news/{currency_pair}",
                "/api/v1/history/{currency_pair}",
                "/api/v1/supported-pairs",
                "/api/v1/system/health"
            ]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )