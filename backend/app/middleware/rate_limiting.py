"""Rate limiting middleware for API keys."""

import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from app.cache import get_rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits for API keys.
    
    Checks rate limit for each request from an API key and:
    - Returns 429 if limit exceeded
    - Adds X-RateLimit-* headers to responses
    
    For JWT auth, rate limits are not enforced (or can be set globally).
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiter."""
        
        # Check if this request has rate limit info in state
        # (populated by auth middleware)
        api_key_id = getattr(request.state, "api_key_id", None)
        rate_limit_rpm = getattr(request.state, "rate_limit_rpm", None)
        
        # If no API key, skip rate limiting (JWT users or public endpoints)
        if not api_key_id or not rate_limit_rpm:
            response = await call_next(request)
            return response
        
        # Check rate limit
        limiter = get_rate_limiter()
        allowed, remaining, reset_at = limiter.check_rate_limit(
            api_key_id,
            rate_limit_rpm,
        )
        
        # If rate limited, return 429 immediately
        if not allowed:
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Limit: {rate_limit_rpm} requests per minute.",
                    "limit": rate_limit_rpm,
                    "remaining": remaining,
                    "reset_at": reset_at.isoformat(),
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit_rpm),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": reset_at.isoformat(),
                    "Retry-After": str((reset_at - __import__("datetime").datetime.utcnow()).seconds),
                },
            )
        
        # Process request normally
        response = await call_next(request)
        
        # Add rate limit headers to successful response
        response.headers["X-RateLimit-Limit"] = str(rate_limit_rpm)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = reset_at.isoformat()
        
        return response
