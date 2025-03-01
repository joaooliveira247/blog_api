from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from blog_api.repositories.posts import PostsRepository
from blog_api.models.posts import PostModel
from blog_api.models.posts import UserModel
from blog_api.contrib.errors import DatabaseError, NoResultFound, UnableCreateEntity
from uuid import UUID
import pytest


@pytest.mark.asyncio
async def test_create_post_success(
    mock_session: AsyncSession,
    mock_post: PostModel,
    post_id: UUID,
    mock_user_inserted: UserModel,
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = mock_user_inserted

    mock_session.commit.side_effect = lambda: setattr(mock_post, "id", post_id)

    posts_repository = PostsRepository(mock_session, users_repository)

    await posts_repository.create_post(mock_post)

    mock_session.add.assert_called_once_with(mock_post)
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    assert mock_post.id == post_id


@pytest.mark.asyncio
async def test_create_post_raise_no_result_found_in_user_id(
    mock_session: AsyncSession, mock_post: PostModel
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = None

    posts_repository = PostsRepository(mock_session, users_repository)

    with pytest.raises(NoResultFound, match="Result not found with user_id"):
        await posts_repository.create_post(mock_post)


@pytest.mark.asyncio
async def test_create_post_raise_database_error(
    mock_session: AsyncMock, mock_post: MagicMock
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = MagicMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    mock_session.flush.side_effect = OperationalError("stmt", "params", "orig")

    with pytest.raises(DatabaseError, match="Database integrity error"):
        await posts_repository.create_post(mock_post)

    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_post_raise_unable_create_entity_error(
    mock_session: AsyncMock, mock_post: MagicMock
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = MagicMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    mock_session.flush.side_effect = IntegrityError("stmt", "params", "orig")

    with pytest.raises(
        UnableCreateEntity, match="Unable Create Entity: Field value already exists"
    ):
        await posts_repository.create_post(mock_post)

    mock_session.rollback.assert_called_once()
