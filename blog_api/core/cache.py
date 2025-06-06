from typing import AsyncGenerator, TypeVar, Type
from pydantic import BaseModel
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    DataError,
)
from blog_api.contrib.errors import CacheError, EncodingError, GenericError
from blog_api.core.config import get_settings
from blog_api.utils.encoding import encode_pydantic_model, decode_pydantic_model

settings = get_settings()


T = TypeVar("T", bound=BaseModel)


async def get_cache_connection() -> AsyncGenerator[Redis, None]:
    pool = ConnectionPool.from_url(settings.redis_dsn)
    client = Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()


class Cache:
    def __init__(self, cache_conn: Redis):
        self.cache_conn = cache_conn

    async def add(self, key: str, value: Type[T] | list[T]) -> None:
        try:
            await self.cache_conn.set(key, encode_pydantic_model(value), ex=360)
        except (ConnectionError, TimeoutError, AuthenticationError, DataError) as e:
            raise CacheError(e.__class__.__name__)
        except TypeError:
            raise EncodingError
        except Exception as e:
            raise GenericError(e.__class__.__name__)

    async def get(self, key: str, decode_model: Type[T]) -> T | list[T] | None:
        try:
            cache_string = await self.cache_conn.get(key)

            models = decode_pydantic_model(cache_string, decode_model)

            return models
        except (ConnectionError, TimeoutError, AuthenticationError, DataError) as e:
            raise CacheError(e.__class__.__name__)
        except Exception as e:
            raise GenericError(e.__class__.__name__)
