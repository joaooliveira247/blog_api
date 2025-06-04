from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from blog_api.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(settings.postgres_dsn)

async_session: AsyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_context_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
