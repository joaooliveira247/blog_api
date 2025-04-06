from datetime import datetime
from typing import AsyncGenerator
from pytest import fixture
from uuid import UUID, uuid4
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.commands.app import app
from blog_api.core.security import gen_hash
from blog_api.models.comments import CommentModel
from blog_api.models.users import UserModel
from blog_api.models.posts import PostModel
from blog_api.schemas.comments import CommentOut
from blog_api.schemas.posts import PostOut
from blog_api.schemas.users import UserOut
from tests.factories import (
    comment_data,
    many_comments_data,
    many_posts_data,
    single_comment_update,
    single_post_data,
    single_user_data,
    many_users_data,
    update_post_data,
)
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
def hashed_string_password() -> str:
    return "$2b$12$4Tcq4pZxdbBH1OkC2EzJ3eW.HpuSPgYj7mrRIABQ7ifY/CAvPE2/a"


@fixture
def user_id() -> UUID:
    return uuid4()


@fixture
def post_id() -> UUID:
    return uuid4()


@fixture
def comment_id() -> UUID:
    return uuid4()


@fixture
def mock_user(hashed_password: str) -> UserModel:
    return UserModel(**single_user_data(), password=hashed_password)


@fixture
def mock_post(user_id: UUID) -> PostModel:
    return PostModel(**single_post_data(), user_id=user_id)


@fixture
def mock_user_inserted(hashed_password: str, user_id: UUID) -> UserModel:
    return UserModel(**single_user_data(), password=hashed_password, id=user_id)


@fixture
def mock_user_out_inserted(mock_user_inserted) -> UserOut:
    return UserOut(
        **mock_user_inserted.__dict__,
        role="user",
        created_at=datetime.now().timestamp(),
        updated_at=datetime.now().timestamp(),
    )


@fixture
def mock_users_out_inserted() -> list[UserOut]:
    return [
        UserOut(
            **user,
            created_at=datetime.now().timestamp(),
            updated_at=datetime.now().timestamp(),
        )
        for user in many_users_data()
    ]


@fixture
def mock_users_inserted() -> list[UserModel]:
    users = [UserModel(**user) for user in many_users_data()]

    return users


@fixture
def mock_post_inserted() -> PostOut:
    return PostOut(**many_posts_data()[0])


@fixture
def mock_posts_inserted() -> list[PostOut]:
    return [PostOut(**post) for post in many_posts_data()]


@fixture
def mock_update_post() -> dict:
    return update_post_data()


@fixture
def mock_comment(user_id: UUID, post_id: UUID) -> CommentModel:
    return CommentModel(**comment_data(), user_id=user_id, post_id=post_id)


@fixture
def mock_comment_inserted() -> CommentOut:
    return CommentOut(**many_comments_data()[0])


@fixture
def mock_comments_inserted() -> list[CommentOut]:
    return [CommentOut(**comment) for comment in many_comments_data()]


@fixture
def mock_comments_inserted_same_author(
    mock_user_inserted: UserModel, mock_comments_inserted: list[CommentOut]
) -> list[CommentOut]:
    return [
        CommentOut(
            **comment.model_dump(exclude="author"), author=mock_user_inserted.username
        )
        for comment in mock_comments_inserted
    ]


@fixture
def mock_comments_inserted_same_post(
    mock_post_inserted: PostOut, mock_comments_inserted: list[CommentOut]
) -> list[CommentOut]:
    return [
        CommentOut(
            **comment.model_dump(exclude="post_title"),
            post_title=mock_post_inserted.title,
        )
        for comment in mock_comments_inserted
    ]


@fixture
def mock_comment_update() -> str:
    return single_comment_update()


@fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@fixture
def users_url() -> str:
    return "/users/"
