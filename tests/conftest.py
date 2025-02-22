from typing import AsyncGenerator
from pytest import fixture
from uuid import UUID, uuid4
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.core.security import gen_hash
from blog_api.models.users import UserModel
from tests.factories import single_user_data, many_users_data
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


@fixture
def user_id() -> UUID:
    return uuid4()


@fixture
def mock_user(hashed_password: str) -> UserModel:
    return UserModel(**single_user_data(), password=hashed_password)


@fixture
def mock_user_inserted(hashed_password: str, user_id: UUID) -> UserModel:
    return UserModel(**single_user_data(), password=hashed_password, id=user_id)


@fixture
async def mock_users_inserted() -> list[UserModel]:
    users = [UserModel(**user) for user in many_users_data()]

    return users
