from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.repositories.posts import PostsRepository
from blog_api.models.posts import PostModel
from blog_api.models.posts import UserModel
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
