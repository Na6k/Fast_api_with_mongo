"""
Redis cache implementation with connection pooling and automatic serialization.

Features:
- Async/await support
- Connection pooling for optimal performance
- Automatic JSON serialization with orjson
- TTL (time-to-live) support
- Batch operations
- Context manager support
"""

from typing import Any, Optional, List, Dict
import redis.asyncio as redis
from src.common.serializers import OrjsonSerializer
from src.core.logger import logger


class RedisCache:
    """
    Async Redis cache with automatic JSON serialization.
    
    Example usage:
        >>> cache = RedisCache(host="localhost", port=6379)
        >>> await cache.connect()
        >>> await cache.set("key", {"data": "value"}, ttl=3600)
        >>> value = await cache.get("key")
        >>> await cache.close()
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        max_connections: int = 50,
        decode_responses: bool = False,
    ):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis server host
            port: Redis server port
            password: Redis password (if required)
            db: Redis database number (0-15)
            max_connections: Maximum connections in the pool
            decode_responses: If True, responses are decoded to strings
        """
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.serializer = OrjsonSerializer()
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Establish connection to Redis with connection pooling.
        
        Raises:
            redis.ConnectionError: If connection fails
        """
        try:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                decode_responses=self.decode_responses,
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info(f"Redis connected: {self.host}:{self.port} (db={self.db})")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self._client:
            await self._client.aclose()
            logger.info("Redis connection closed")
        if self._pool:
            await self._pool.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _ensure_connected(self) -> None:
        """Ensure Redis client is connected."""
        if not self._client:
            raise RuntimeError("Redis client not connected. Call connect() first.")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache and deserialize.
        
        Args:
            key: Cache key
            
        Returns:
            Deserialized value or None if key doesn't exist
            
        Example:
            >>> value = await cache.get("user:123")
        """
        self._ensure_connected()
        try:
            data = await self._client.get(key)
            if data is None:
                return None
            return self.serializer.loads(data)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with automatic serialization.
        
        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            ttl: Time-to-live in seconds (None = no expiration)
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> await cache.set("user:123", {"name": "John"}, ttl=3600)
        """
        self._ensure_connected()
        try:
            data = self.serializer.dumps(value)
            if ttl:
                await self._client.setex(key, ttl, data)
            else:
                await self._client.set(key, data)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False otherwise
            
        Example:
            >>> await cache.delete("user:123")
        """
        self._ensure_connected()
        try:
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
            
        Example:
            >>> if await cache.exists("user:123"):
            ...     print("Key exists")
        """
        self._ensure_connected()
        try:
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time on existing key.
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> await cache.expire("user:123", 3600)
        """
        self._ensure_connected()
        try:
            result = await self._client.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values at once (batch operation).
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary with key-value pairs (missing keys are excluded)
            
        Example:
            >>> values = await cache.get_many(["user:1", "user:2", "user:3"])
            >>> print(values)  # {"user:1": {...}, "user:2": {...}}
        """
        self._ensure_connected()
        if not keys:
            return {}

        try:
            values = await self._client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self.serializer.loads(value)
            return result
        except Exception as e:
            logger.error(f"Redis MGET error: {e}")
            return {}

    async def set_many(
        self,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set multiple values at once (batch operation).
        
        Args:
            data: Dictionary with key-value pairs
            ttl: Time-to-live in seconds (applies to all keys)
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> await cache.set_many({
            ...     "user:1": {"name": "Alice"},
            ...     "user:2": {"name": "Bob"}
            ... }, ttl=3600)
        """
        self._ensure_connected()
        if not data:
            return True

        try:
            serialized = {k: self.serializer.dumps(v) for k, v in data.items()}
            
            if ttl:
                # Use pipeline for TTL
                async with self._client.pipeline() as pipe:
                    for key, value in serialized.items():
                        pipe.setex(key, ttl, value)
                    await pipe.execute()
            else:
                await self._client.mset(serialized)
            return True
        except Exception as e:
            logger.error(f"Redis MSET error: {e}")
            return False

    async def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys at once (batch operation).
        
        Args:
            keys: List of cache keys
            
        Returns:
            Number of keys deleted
            
        Example:
            >>> count = await cache.delete_many(["user:1", "user:2"])
            >>> print(f"Deleted {count} keys")
        """
        self._ensure_connected()
        if not keys:
            return 0

        try:
            result = await self._client.delete(*keys)
            return result
        except Exception as e:
            logger.error(f"Redis DELETE MANY error: {e}")
            return 0

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern with wildcards (e.g., "user:*", "session:*")
            
        Returns:
            Number of keys deleted
            
        Warning:
            Use with caution on large datasets!
            
        Example:
            >>> await cache.clear_pattern("user:*")  # Delete all user keys
        """
        self._ensure_connected()
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR PATTERN error for '{pattern}': {e}")
            return 0

    async def ttl(self, key: str) -> int:
        """
        Get remaining time-to-live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Seconds until expiration, -1 if no expiration, -2 if key doesn't exist
            
        Example:
            >>> remaining = await cache.ttl("user:123")
            >>> if remaining > 0:
            ...     print(f"Expires in {remaining} seconds")
        """
        self._ensure_connected()
        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2

    async def ping(self) -> bool:
        """
        Ping Redis server to check connection.
        
        Returns:
            True if server responds, False otherwise
            
        Example:
            >>> if await cache.ping():
            ...     print("Redis is alive")
        """
        self._ensure_connected()
        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False
