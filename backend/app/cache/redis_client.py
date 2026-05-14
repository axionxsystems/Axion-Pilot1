"""Redis client singleton with connection pooling and graceful fallback."""

import os
import logging
from typing import Optional, Any, Dict
import redis
from redis.connection import ConnectionPool
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)

# Singleton instance
_redis_client: Optional[redis.Redis] = None
_is_redis_available: bool = False


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client singleton with lazy initialization.
    
    Returns None if Redis is unavailable (graceful fallback for development).
    """
    global _redis_client, _is_redis_available
    
    if _redis_client is not None:
        return _redis_client if _is_redis_available else None
    
    # Try to initialize Redis
    try:
        redis_url = os.environ.get(
            "REDIS_URL",
            os.environ.get("REDIS_HOST", "localhost") and
            f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', 6379)}"
        ) or "redis://localhost:6379"
        
        pool = ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
        _redis_client = redis.Redis(connection_pool=pool)
        
        # Test connection
        _redis_client.ping()
        _is_redis_available = True
        logger.info("✓ Redis client initialized successfully")
        return _redis_client
        
    except (RedisError, RedisConnectionError, OSError) as e:
        logger.warning(f"⚠ Redis connection failed (using in-memory fallback): {e}")
        _is_redis_available = False
        _redis_client = None  # Signal that Redis is unavailable
        return None


def is_redis_available() -> bool:
    """Check if Redis is currently available."""
    global _is_redis_available
    if _redis_client is None:
        get_redis_client()
    return _is_redis_available


def close_redis():
    """Close Redis connection (for graceful shutdown)."""
    global _redis_client, _is_redis_available
    if _redis_client:
        try:
            _redis_client.close()
            logger.info("Redis client closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        _redis_client = None
        _is_redis_available = False


class InMemoryRedisBackend:
    """
    In-memory fallback backend for Redis operations when Redis is unavailable.
    Stores data in memory only (resets on restart).
    """
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from memory."""
        if key in self._store:
            return str(self._store[key])
        return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a value in memory with optional expiry (seconds)."""
        self._store[key] = value
        if ex:
            import time
            self._expiry[key] = time.time() + ex
        return True
    
    def incr(self, key: str) -> int:
        """Increment a value in memory."""
        current = self._store.get(key, 0)
        self._store[key] = int(current) + 1
        return self._store[key]
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiry for a key."""
        import time
        self._expiry[key] = time.time() + seconds
        return True
    
    def ttl(self, key: str) -> int:
        """Get time-to-live for a key in seconds."""
        import time
        if key not in self._expiry:
            return -1
        ttl = self._expiry[key] - time.time()
        if ttl <= 0:
            del self._store[key]
            del self._expiry[key]
            return -2
        return int(ttl)
    
    def delete(self, *keys: str) -> int:
        """Delete keys from memory."""
        count = 0
        for key in keys:
            if key in self._store:
                del self._store[key]
                count += 1
            if key in self._expiry:
                del self._expiry[key]
        return count
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._store
    
    def ping(self) -> bool:
        """Ping the backend (always succeeds for in-memory)."""
        return True


# Global in-memory backend
_in_memory_backend: Optional[InMemoryRedisBackend] = None


def get_redis_or_fallback() -> Any:
    """
    Get Redis client or in-memory fallback.
    
    Returns either a redis.Redis instance or InMemoryRedisBackend.
    """
    global _in_memory_backend
    
    redis_client = get_redis_client()
    if redis_client is not None:
        return redis_client
    
    # Fallback to in-memory backend
    if _in_memory_backend is None:
        _in_memory_backend = InMemoryRedisBackend()
        logger.info("Using in-memory Redis fallback")
    
    return _in_memory_backend
