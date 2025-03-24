from typing import AsyncGenerator
from redis.asyncio import ConnectionPool, Redis
from blog_api.core.config import settings


async def get_cache_connection() -> AsyncGenerator[Redis, None]:
    pool = ConnectionPool.from_url(settings.redis_dsn)
    client = Redis(connection_pool=pool)
    try:
        yield client
    finally:
        client.close()
