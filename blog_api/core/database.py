from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from config import settings

engine: AsyncEngine = create_async_engine(settings.postgres_dsn, expire_on_commit=False)
