from typing import AsyncGenerator
from pytest import fixture
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


@fixture
async def mock_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncMock(spec=AsyncSession)
    yield session
