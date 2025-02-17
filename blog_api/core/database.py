from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from config import settings

engine: AsyncEngine = create_async_engine(settings.postgres_dsn, expire_on_commit=False)

async_session: AsyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
