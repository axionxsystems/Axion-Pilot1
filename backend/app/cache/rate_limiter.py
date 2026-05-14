"""Redis-backed rate limiter for API keys."""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional
from app.cache import get_redis_or_fallback, is_redis_available
from app.models.rate_limit import RateLimitLog

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Rate limiter using Redis for fast, distributed tracking.
    
    Uses a per-minute rolling window approach:
    - Redis key: "ratelimit:{api_key_id}:{minute_bucket}"
    - Value: request count for that minute
    - Expiry: 90 seconds (ensures window clears)
    
    Falls back to in-memory implementation if Redis unavailable.
    """
    
    def __init__(self):
        self.redis = get_redis_or_fallback()
        self.window_seconds = 60  # 1-minute window
        self.key_prefix = "ratelimit"
    
    def _get_minute_bucket(self, dt: datetime = None) -> str:
        """
        Generate a minute bucket string.
        
        Example: 2026-05-14 12:30:45 → "2026-05-14_12_30"
        """
        if dt is None:
            dt = datetime.utcnow()
        return dt.strftime("%Y-%m-%d_%H_%M")
    
    def _get_redis_key(self, api_key_id: str, minute_bucket: str) -> str:
        """Generate Redis key for rate limit tracking."""
        return f"{self.key_prefix}:{api_key_id}:{minute_bucket}"
    
    def check_rate_limit(
        self,
        api_key_id: str,
        rpm_limit: int,
        db_session=None,
    ) -> Tuple[bool, int, datetime]:
        """
        Check if API key has exceeded rate limit.
        
        Args:
            api_key_id: The API key ID (UUID string)
            rpm_limit: Requests per minute limit
            db_session: Optional database session for async logging (not used currently)
        
        Returns:
            Tuple of (allowed, remaining, reset_at):
            - allowed: True if request should be allowed, False if rate limited
            - remaining: Requests remaining before hitting limit
            - reset_at: Datetime when this minute's limit resets
        
        Example:
            allowed, remaining, reset = limiter.check_rate_limit(
                "key-123",
                rpm_limit=1000
            )
            if not allowed:
                # Return 429 Too Many Requests
        """
        now = datetime.utcnow()
        minute_bucket = self._get_minute_bucket(now)
        redis_key = self._get_redis_key(api_key_id, minute_bucket)
        
        try:
            # Increment request count in Redis
            # INCR is atomic and safe for concurrent requests
            count = self.redis.incr(redis_key)
            
            # Set expiry on first request of this minute
            # (90 seconds ensures window clears after minute expires)
            if count == 1:
                self.redis.expire(redis_key, 90)
            
            # Calculate reset time (end of current minute)
            reset_at = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
            
            # Determine if allowed
            allowed = count <= rpm_limit
            remaining = max(0, rpm_limit - count)
            
            return allowed, remaining, reset_at
            
        except Exception as e:
            logger.error(f"Rate limiter check failed for key {api_key_id}: {e}")
            # On error, allow the request (fail open) to prevent outages
            reset_at = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=1)
            return True, rpm_limit, reset_at
    
    def get_usage(
        self,
        api_key_id: str,
        minutes: int = 1,
        db_session=None,
    ) -> int:
        """
        Get total requests for API key in the last N minutes.
        
        Args:
            api_key_id: The API key ID
            minutes: Number of minutes to look back
            db_session: Optional database session (for future DB-backed lookups)
        
        Returns:
            Total request count across all minute buckets
        """
        try:
            total = 0
            now = datetime.utcnow()
            
            # Check current and previous minute buckets
            for offset in range(minutes):
                check_time = now - timedelta(minutes=offset)
                minute_bucket = self._get_minute_bucket(check_time)
                redis_key = self._get_redis_key(api_key_id, minute_bucket)
                
                count = self.redis.get(redis_key)
                if count:
                    total += int(count)
            
            return total
            
        except Exception as e:
            logger.error(f"Failed to get usage for key {api_key_id}: {e}")
            return 0
    
    def reset(self, api_key_id: str) -> bool:
        """
        Reset rate limit counter for an API key (e.g., for testing or abuse recovery).
        
        Args:
            api_key_id: The API key ID
        
        Returns:
            True if reset successful, False otherwise
        """
        try:
            now = datetime.utcnow()
            minute_bucket = self._get_minute_bucket(now)
            redis_key = self._get_redis_key(api_key_id, minute_bucket)
            
            self.redis.delete(redis_key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit for key {api_key_id}: {e}")
            return False
    
    def get_all_keys_usage(self, limit: int = 100) -> dict:
        """
        Get usage statistics for all active API keys (for monitoring/admin).
        
        Args:
            limit: Maximum number of keys to return
        
        Returns:
            Dict mapping api_key_id to request count
        """
        try:
            keys = self.redis.keys(f"{self.key_prefix}:*")[:limit]
            usage = {}
            
            for key in keys:
                # Parse key: "ratelimit:{api_key_id}:{minute_bucket}"
                parts = key.split(":")
                if len(parts) >= 3:
                    api_key_id = parts[1]
                    count = self.redis.get(key)
                    if count:
                        usage[api_key_id] = usage.get(api_key_id, 0) + int(count)
            
            return usage
            
        except Exception as e:
            logger.error(f"Failed to get all keys usage: {e}")
            return {}


# Global rate limiter instance
_rate_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    """Get or create the rate limiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter
