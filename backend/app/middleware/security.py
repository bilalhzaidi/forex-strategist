from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import time
import hashlib
from typing import Dict, Set
from ..core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with memory-based storage"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self.blocked_ips: Set[str] = set()
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > minute_ago
            ]
        
        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            self.blocked_ips.add(client_ip)
            return True
        
        self.requests[client_ip].append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)
        
        if self.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                }
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client info
        client_ip = request.headers.get("X-Forwarded-For", 
                                      request.headers.get("X-Real-IP", 
                                      request.client.host if request.client else "unknown"))
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request (in production, use proper logging)
        if not settings.is_development:
            print(f"{client_ip} - {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response

class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Validate API keys for sensitive endpoints"""
    
    PROTECTED_PATHS = ["/api/v1/analyze"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for non-protected paths
        if request.url.path not in self.PROTECTED_PATHS:
            return await call_next(request)
        
        # In production, you might want to require API keys
        if settings.is_production:
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                # For now, just add a warning header
                response = await call_next(request)
                response.headers["X-Warning"] = "API key recommended for production use"
                return response
        
        return await call_next(request)