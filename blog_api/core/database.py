from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from blog_api.core.config import settings
from typing import AsyncGenerator

engine: AsyncEngine = create_async_engine(settings.postgres_dsn)

async_session: AsyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
