import pytest
from uuid import UUID
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.contrib.errors import NoResultFound
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


@pytest.mark.asyncio
async def test_create_comment_raise_no_result_found_user_id(
    mock_session: AsyncSession, mock_comment: CommentModel
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = None

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with pytest.raises(NoResultFound, match="Result not found with user_id"):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)


@pytest.mark.asyncio
async def test_create_comment_raise_no_result_found_post_id(
    mock_session: AsyncSession, mock_comment: CommentModel, mock_user_inserted
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = mock_user_inserted

    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = None

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with pytest.raises(NoResultFound, match="Result not found with post_id"):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)
