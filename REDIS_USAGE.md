# Redis Cache Usage Guide

## Overview

This project now includes a production-ready Redis cache implementation with:

- ✅ **Connection pooling** for optimal performance
- ✅ **Automatic JSON serialization** using fast orjson library
- ✅ **Async/await** support throughout
- ✅ **TTL (time-to-live)** support
- ✅ **Batch operations** (get_many, set_many, delete_many)
- ✅ **Pattern-based deletion** for cleaning multiple keys
- ✅ **Context manager** support

## Setup

### 1. Environment Variables

Add Redis configuration to your `.env` file:

```env
# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_password_here  # Optional, leave empty if no password
```

### 2. Install Dependencies

```bash
poetry install
```

This will install:
- `redis>=5.0.0` - Async Redis client
- `orjson>=3.10.0` - Fast JSON serializer

## Usage Examples

### Example 1: Basic Usage in Endpoint

```python
from fastapi import APIRouter, Depends
from src.common.cache import RedisCache
from src.api.dependencies import get_redis_cache

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    cache: RedisCache = Depends(get_redis_cache)
):
    # Try to get from cache first
    cached_user = await cache.get(f"user:{user_id}")
    if cached_user:
        return {"source": "cache", "data": cached_user}
    
    # If not in cache, fetch from database
    user = await fetch_user_from_db(user_id)  # Your DB function
    
    # Store in cache for 1 hour
    await cache.set(f"user:{user_id}", user, ttl=3600)
    
    return {"source": "database", "data": user}
```

### Example 2: Caching with MongoDB

```python
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.common.cache import RedisCache
from src.api.dependencies import get_mongo_db, get_redis_cache

router = APIRouter()

@router.get("/products")
async def get_products(
    category: str,
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    cache: RedisCache = Depends(get_redis_cache)
):
    cache_key = f"products:category:{category}"
    
    # Check cache
    cached_products = await cache.get(cache_key)
    if cached_products:
        return cached_products
    
    # Fetch from MongoDB
    products = await db["products"].find({"category": category}).to_list(100)
    
    # Cache for 10 minutes
    await cache.set(cache_key, products, ttl=600)
    
    return products
```

### Example 3: Batch Operations

```python
@router.post("/users/bulk")
async def create_users_bulk(
    users: List[dict],
    cache: RedisCache = Depends(get_redis_cache)
):
    # Save multiple users to cache at once
    cache_data = {
        f"user:{user['id']}": user
        for user in users
    }
    
    # Set all with 1 hour TTL
    await cache.set_many(cache_data, ttl=3600)
    
    return {"cached": len(users)}

@router.get("/users/bulk")
async def get_users_bulk(
    user_ids: List[str],
    cache: RedisCache = Depends(get_redis_cache)
):
    # Get multiple users at once
    keys = [f"user:{uid}" for uid in user_ids]
    users = await cache.get_many(keys)
    
    return users
```

### Example 4: Pattern-Based Deletion

```python
@router.delete("/cache/users")
async def clear_user_cache(
    cache: RedisCache = Depends(get_redis_cache)
):
    # Delete all user keys
    deleted_count = await cache.clear_pattern("user:*")
    
    return {"deleted_keys": deleted_count}

@router.delete("/cache/products/{category}")
async def clear_category_cache(
    category: str,
    cache: RedisCache = Depends(get_redis_cache)
):
    # Delete all products in a category
    deleted_count = await cache.clear_pattern(f"products:category:{category}:*")
    
    return {"deleted_keys": deleted_count}
```

### Example 5: Cache Invalidation on Update

```python
@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    cache: RedisCache = Depends(get_redis_cache)
):
    # Update in database
    result = await db["users"].update_one(
        {"_id": user_id},
        {"$set": user_data}
    )
    
    # Invalidate cache
    await cache.delete(f"user:{user_id}")
    
    return {"updated": result.modified_count}
```

### Example 6: Using Context Manager

```python
from src.common.cache import RedisCache
from src.core.settings import load_settings

async def standalone_function():
    settings = load_settings()
    
    # Context manager automatically connects and closes
    async with RedisCache(
        host=settings.redis.host,
        port=settings.redis.port,
        password=settings.redis.password
    ) as cache:
        await cache.set("key", "value", ttl=3600)
        value = await cache.get("key")
        print(value)
```

### Example 7: Cache Decorator Pattern

```python
from functools import wraps
from src.common.cache import RedisCache

def cached(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, cache: RedisCache, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

# Usage
@router.get("/expensive-calculation")
async def expensive_calculation(
    param: str,
    cache: RedisCache = Depends(get_redis_cache)
):
    @cached(ttl=1800)  # Cache for 30 minutes
    async def do_calculation(param: str, cache: RedisCache):
        # Some heavy computation
        result = complex_calculation(param)
        return result
    
    return await do_calculation(param, cache=cache)
```

## Available Methods

### Basic Operations
- `await cache.get(key)` - Get value
- `await cache.set(key, value, ttl=3600)` - Set value with TTL
- `await cache.delete(key)` - Delete key
- `await cache.exists(key)` - Check if key exists
- `await cache.expire(key, ttl)` - Update TTL
- `await cache.ttl(key)` - Get remaining TTL

### Batch Operations
- `await cache.get_many(keys)` - Get multiple values
- `await cache.set_many(data, ttl=3600)` - Set multiple values
- `await cache.delete_many(keys)` - Delete multiple keys
- `await cache.clear_pattern("pattern:*")` - Delete by pattern

### Utility
- `await cache.ping()` - Check connection
- `await cache.connect()` - Manual connect
- `await cache.close()` - Manual close

## Best Practices

### 1. Use Meaningful Cache Keys

```python
# ❌ Bad
await cache.set("u123", user_data)

# ✅ Good
await cache.set(f"user:{user_id}:profile", user_data)
```

### 2. Always Set TTL

```python
# ❌ Bad - stays forever
await cache.set("data", value)

# ✅ Good - expires after 1 hour
await cache.set("data", value, ttl=3600)
```

### 3. Use Namespacing for Related Keys

```python
# User data
await cache.set(f"user:{user_id}:profile", profile, ttl=3600)
await cache.set(f"user:{user_id}:settings", settings, ttl=3600)

# Later, clear all user data
await cache.clear_pattern(f"user:{user_id}:*")
```

### 4. Handle Cache Misses Gracefully

```python
cached = await cache.get(key)
if cached is None:
    # Fetch from source
    data = await fetch_from_db()
    await cache.set(key, data, ttl=3600)
else:
    data = cached
```

### 5. Use Batch Operations When Possible

```python
# ❌ Slow - N network calls
for user_id in user_ids:
    user = await cache.get(f"user:{user_id}")

# ✅ Fast - 1 network call
keys = [f"user:{uid}" for uid in user_ids]
users = await cache.get_many(keys)
```

## Common TTL Values

```python
CACHE_TTL = {
    "1_minute": 60,
    "5_minutes": 300,
    "10_minutes": 600,
    "30_minutes": 1800,
    "1_hour": 3600,
    "6_hours": 21600,
    "12_hours": 43200,
    "1_day": 86400,
    "1_week": 604800,
}
```

## Troubleshooting

### Connection Issues

```python
# Check if Redis is reachable
cache = RedisCache(host="localhost", port=6379)
await cache.connect()
is_alive = await cache.ping()
print(f"Redis alive: {is_alive}")
```

### Memory Issues

```python
# See how long until key expires
remaining = await cache.ttl("my_key")
if remaining == -1:
    print("Key has no expiration!")
    await cache.expire("my_key", 3600)  # Add 1 hour TTL
```

### Debugging Cache Keys

```python
# List all keys matching pattern (use carefully!)
import redis.asyncio as redis

r = redis.Redis(host="localhost", port=6379)
keys = []
async for key in r.scan_iter(match="user:*"):
    keys.append(key.decode())
    
print(f"Found keys: {keys}")
```

## Performance Tips

1. **Use connection pooling** (already configured with `max_connections=50`)
2. **Batch operations** when fetching/setting multiple keys
3. **Appropriate TTL** - longer for rarely-changing data
4. **Namespace keys** for easy pattern-based deletion
5. **Monitor cache hit rate** to optimize TTL values

## MongoDB + Redis Pattern

Typical flow for optimal performance:

```
User Request
    ↓
Check Redis Cache
    ↓
[Cache Hit] → Return cached data
    ↓
[Cache Miss] → Query MongoDB
    ↓
Store result in Redis (with TTL)
    ↓
Return data to user
```

## Production Checklist

- [ ] Set `REDIS_HOST` in production environment
- [ ] Set `REDIS_PASSWORD` for security
- [ ] Configure appropriate TTL values
- [ ] Monitor Redis memory usage
- [ ] Set up Redis persistence (RDB/AOF)
- [ ] Configure Redis maxmemory policy
- [ ] Enable Redis auth in production
- [ ] Monitor cache hit/miss rates

## Additional Resources

- [Redis Documentation](https://redis.io/documentation)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [OrJSON Documentation](https://github.com/ijl/orjson)

---

**Need help?** Check the code in `src/common/cache/redis.py` for full implementation details.
