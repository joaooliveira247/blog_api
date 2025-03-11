import pytest
from uuid import UUID
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.repositories.comments import CommentsRepository
from blog_api.models.comments import CommentModel


@pytest.mark.asyncio
async def test_create_comment_success(
    mock_session: AsyncSession,
    mock_user_inserted,
    mock_post_inserted,
    mock_comment: CommentModel,
    comment_id: UUID,
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id = AsyncMock(return_value=mock_user_inserted)

    posts_repository = AsyncMock()
    posts_repository.get_post_by_id = AsyncMock(return_value=mock_post_inserted)

    mock_session.commit.side_effect = lambda: setattr(mock_comment, "id", comment_id)

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    await comments_repository.create_comment(mock_comment)

    mock_session.add.assert_called_once_with(mock_comment)
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    assert mock_comment.id == comment_id
