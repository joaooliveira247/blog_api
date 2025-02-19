from typing import AsyncGenerator
from pytest import fixture
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.core.security import gen_hash
from faker import Faker

fake: Faker = Faker()


@fixture
async def mock_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncMock(spec=AsyncSession)
    yield session


@fixture
def password() -> str:
    return fake.password()


@fixture
def hashed_password(password: str) -> str:
    hash_passwd = gen_hash(password)

    return hash_passwd
