from typing import AsyncGenerator
from pytest import fixture
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

fake: Faker = Faker()


@fixture
async def mock_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncMock(spec=AsyncSession)
    yield session


@fixture
def password() -> str:
    return fake.password()
