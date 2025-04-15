from typing import Annotated
from fastapi import Depends
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.core.database import get_session
from blog_api.core.cache import get_cache_connection


DatabaseDependency: AsyncSession = Annotated[AsyncSession, Depends(get_session)]

CacheDependency: Redis = Annotated[Redis, Depends(get_cache_connection)]
