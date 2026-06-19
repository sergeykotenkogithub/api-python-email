"""
Rate limiting middleware module.

This module provides rate limiting middleware to protect against abuse.
"""

import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from app.repositories.rate_limiter import get_rate_limiter, RateLimiter
from app.api.deps import get_client_ip
from app.utils.logger import get_logger

logger = get_logger("RateLimitMiddleware")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app, rate_limiter: RateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or get_rate_limiter()
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response object
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/api/health", "/api/status", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = get_client_ip(request)
        
        # Check rate limit
        is_allowed, rate_limit_info = await self.rate_limiter.check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            
            # Create response with rate limit headers
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "Rate Limit Exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": rate_limit_info.get("retry_after", 3600),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info.get("reset_time", ""))
            response.headers["Retry-After"] = str(rate_limit_info.get("retry_after", 3600))
            
            return response
        
        # Record the request
        await self.rate_limiter.record_request(client_ip)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to successful response
        rate_limit_status = await self.rate_limiter.get_rate_limit_info(client_ip)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_status["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_status["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_status.get("reset_time", ""))
        
        return response


class RateLimitMiddlewareSimple(BaseHTTPMiddleware):
    """Simplified rate limiting middleware for basic use cases."""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # Simple in-memory storage
    
    async def dispatch(self, request: Request, call_next):
        """Process request with simple rate limiting."""
        # Skip rate limiting for certain paths
        if request.url.path in ["/api/health", "/api/status", "/docs", "/redoc"]:
            return await call_next(request)
        
        client_ip = get_client_ip(request)
        current_time = time.time()
        
        # Clean up old entries
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "Rate Limit Exceeded",
                    "message": "Too many requests. Please try again later."
                }
            )
        
        # Record request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response