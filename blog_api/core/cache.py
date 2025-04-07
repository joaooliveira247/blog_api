from typing import AsyncGenerator
from pydantic import BaseModel
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    DataError,
)
from blog_api.contrib.errors import CacheError, EncodingError
from blog_api.core.config import settings
from blog_api.utils.encoding import encode_pydantic_model


async def get_cache_connection() -> AsyncGenerator[Redis, None]:
    pool = ConnectionPool.from_url(settings.redis_dsn)
    client = Redis(connection_pool=pool)
    try:
        yield client
    finally:
        client.close()


class Cache:
    def __init__(self, cache_conn: Redis):
        self.cache_conn = cache_conn

    async def add(self, key: str, value: BaseModel | list[BaseModel]) -> None:
        try:
            await self.cache_conn.set(key, encode_pydantic_model(value), ex=360)
        except (ConnectionError, TimeoutError, AuthenticationError, DataError) as e:
            raise CacheError(e.__class__.__name__)
        except TypeError:
            raise EncodingError
