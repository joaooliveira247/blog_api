from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.contrib.errors import (
    DatabaseError,
    GenericError,
    NoResultFound,
    NothingToUpdate,
    UnableCreateEntity,
    UnableDeleteEntity,
)
from blog_api.models.comments import CommentModel
from blog_api.repositories.comments import CommentsRepository
from blog_api.schemas.comments import CommentOut


@pytest.mark.asyncio
async def test_create_comment_success(
    mock_session: AsyncSession,
    mock_post_inserted,
    mock_comment: CommentModel,
    comment_id: UUID,
):
    posts_repository = AsyncMock()
    posts_repository.get_post_by_id = AsyncMock(
        return_value=mock_post_inserted
    )

    mock_session.commit.side_effect = lambda: setattr(
        mock_comment, "id", comment_id
    )

    comments_repository = CommentsRepository(mock_session, posts_repository)

    await comments_repository.create_comment(mock_comment)

    mock_session.add.assert_called_once_with(mock_comment)
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    assert mock_comment.id == comment_id


@pytest.mark.asyncio
async def test_create_comment_raise_no_result_found_post_id(
    mock_session: AsyncSession, mock_comment: CommentModel, mock_user_inserted
):
    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = None

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with pytest.raises(NoResultFound, match="Result not found with post_id"):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)


@pytest.mark.asyncio
async def test_create_comment_raise_database_error(
    mock_session: AsyncSession, mock_comment: CommentModel
):
    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = MagicMock()

    mock_session.add.side_effect = OperationalError("stmt", "params", "orig")

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with pytest.raises(DatabaseError, match="Database integrity error"):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)
        mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_comment_raise_unable_create_entity(
    mock_session: AsyncSession, mock_comment: CommentModel
):
    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = MagicMock()

    mock_session.add.side_effect = IntegrityError("stmt", "params", "orig")

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with pytest.raises(
        UnableCreateEntity,
        match="Unable Create Entity: Field value already exists",
    ):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)
        mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_comment_raise_generic_error(
    mock_session: AsyncSession, mock_comment: CommentModel
):
    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = MagicMock()

    mock_session.add.side_effect = Exception()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with pytest.raises(GenericError, match="Generic Error"):
        await comments_repository.create_comment(mock_comment)

        mock_session.assert_called_once_with(mock_comment)
        mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_comments_return_success(
    mock_session: AsyncSession, mock_comments_inserted: list[CommentOut]
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comments", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_comments_inserted

        result = await comments_repository.get_comments()

        mock.assert_called_once()
        assert result == mock_comments_inserted


@pytest.mark.asyncio
async def test_get_comments_return_success_but_empty(
    mock_session: AsyncSession,
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comments", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []

        result = await comments_repository.get_comments()

        mock.assert_called_once()
        assert result == []


@pytest.mark.asyncio
async def test_get_comments_raise_database_error(mock_session: AsyncSession):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comments", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.get_comments()

        mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_comments_raise_generic_error(mock_session: AsyncSession):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comments", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.get_comments()

        mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_comment_by_id_return_success(
    mock_session: AsyncSession, mock_comment_inserted: CommentOut
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comment_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_comment_inserted

        result = await comments_repository.get_comment_by_id(
            mock_comment_inserted.id
        )

        mock.assert_called_once_with(mock_comment_inserted.id)
        assert result == mock_comment_inserted


@pytest.mark.asyncio
async def test_get_comment_by_id_return_success_but_none(
    mock_session: AsyncSession, mock_comment_inserted: CommentOut
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comment_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        result = await comments_repository.get_comment_by_id(
            mock_comment_inserted.id
        )

        mock.assert_called_once_with(mock_comment_inserted.id)
        assert result is None


@pytest.mark.asyncio
async def test_get_comment_by_id_raise_database_error(
    mock_session: AsyncSession, mock_comment_inserted: CommentOut
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comment_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.get_comment_by_id(
                mock_comment_inserted.id
            )

        mock.assert_called_once_with(mock_comment_inserted.id)


@pytest.mark.asyncio
async def test_get_comment_by_id_raise_generic_error(
    mock_session: AsyncSession, mock_comment_inserted: CommentOut
):
    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(mock_session, posts_repository)

    with patch.object(
        CommentsRepository, "get_comment_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.get_comment_by_id(
                mock_comment_inserted.id
            )

        mock.assert_called_once_with(mock_comment_inserted.id)


@pytest.mark.asyncio
async def test_get_comments_by_user_id_return_success(
    mock_session: AsyncSession,
    mock_comments_inserted_same_author: list[CommentOut],
    user_id: UUID,
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_comments_inserted_same_author

        result = await comments_repository.get_comments_by_user_id(user_id)

        mock.assert_called_once_with(user_id)
        assert result == mock_comments_inserted_same_author


@pytest.mark.asyncio
async def test_get_comments_by_user_id_return_success_but_empty(
    mock_session: AsyncSession,
    user_id: UUID,
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []

        result = await comments_repository.get_comments_by_user_id(user_id)

        mock.assert_called_once_with(user_id)
        assert result == []


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_no_result_found_user_id(
    mock_session: AsyncSession, user_id
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = None

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with pytest.raises(NoResultFound, match="Result not found with user_id"):
        await comments_repository.get_comments_by_user_id(user_id)


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_database_error(
    mock_session: AsyncSession, user_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.get_comments_by_user_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_generic_error(
    mock_session: AsyncSession, user_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.get_comments_by_user_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_comments_by_post_id_return_success(
    mock_session: AsyncSession,
    mock_comments_inserted_same_post: list[CommentOut],
    post_id: UUID,
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_post_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_comments_inserted_same_post

        result = await comments_repository.get_comments_by_post_id(post_id)

        mock.assert_called_once_with(post_id)
        assert result == mock_comments_inserted_same_post


@pytest.mark.asyncio
async def test_get_comments_by_post_id_return_success_but_empty(
    mock_session: AsyncSession,
    post_id: UUID,
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_post_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []

        result = await comments_repository.get_comments_by_post_id(post_id)

        mock.assert_called_once_with(post_id)
        assert result == []


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_no_result_found_post_id(
    mock_session: AsyncSession, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()
    posts_repository.get_post_by_id.return_value = None

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with pytest.raises(NoResultFound, match="Result not found with post_id"):
        await comments_repository.get_comments_by_post_id(post_id)


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_database_error(
    mock_session: AsyncSession, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_post_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.get_comments_by_post_id(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_generic_error(
    mock_session: AsyncSession, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "get_comments_by_post_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.get_comments_by_post_id(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_update_comment_return_success(
    mock_session: AsyncSession, comment_id: UUID, mock_comment_update: str
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "update_comment", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        await comments_repository.update_comment(
            comment_id, mock_comment_update
        )

        mock.assert_called_once_with(comment_id, mock_comment_update)


@pytest.mark.asyncio
async def test_update_comment_raise_nothing_to_update(
    mock_session: AsyncSession, comment_id: UUID, mock_comment_update: str
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "update_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = NothingToUpdate

        with pytest.raises(NothingToUpdate, match="Nothing to update"):
            await comments_repository.update_comment(
                comment_id, mock_comment_update
            )

        mock.assert_called_once_with(comment_id, mock_comment_update)


@pytest.mark.asyncio
async def test_update_comment_raise_no_result_found(
    mock_session: AsyncSession, comment_id: UUID, mock_comment_update: str
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "update_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = NoResultFound("comment_id")

        with pytest.raises(
            NoResultFound, match="Result not found with comment_id"
        ):
            await comments_repository.update_comment(
                comment_id, mock_comment_update
            )

        mock.assert_called_once_with(comment_id, mock_comment_update)


@pytest.mark.asyncio
async def test_update_comment_raise_database_error(
    mock_session: AsyncSession, comment_id: UUID, mock_comment_update: str
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "update_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.update_comment(
                comment_id, mock_comment_update
            )

        mock.assert_called_once_with(comment_id, mock_comment_update)


@pytest.mark.asyncio
async def test_update_comment_raise_generic_error(
    mock_session: AsyncSession, comment_id: UUID, mock_comment_update: str
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "update_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.update_comment(
                comment_id, mock_comment_update
            )

        mock.assert_called_once_with(comment_id, mock_comment_update)


@pytest.mark.asyncio
async def test_delete_comment_return_success(
    mock_session: AsyncSession, comment_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "delete_comment", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        await comments_repository.delete_comment(comment_id)

        mock.assert_called_once_with(comment_id)


@pytest.mark.asyncio
async def test_delete_comment_raise_no_result_found(
    mock_session: AsyncSession, comment_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "delete_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = NoResultFound("comment_id")

        with pytest.raises(
            NoResultFound, match="Result not found with comment_id"
        ):
            await comments_repository.delete_comment(comment_id)

        mock.assert_called_once_with(comment_id)


@pytest.mark.asyncio
async def test_delete_comment_raise_database_error(
    mock_session: AsyncSession, comment_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "delete_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await comments_repository.delete_comment(comment_id)

        mock.assert_called_once_with(comment_id)


@pytest.mark.asyncio
async def test_delete_comment_raise_unable_delete_entity(
    mock_session: AsyncSession, comment_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "delete_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = UnableDeleteEntity

        with pytest.raises(UnableDeleteEntity, match="Unable Delete Entity"):
            await comments_repository.delete_comment(comment_id)

        mock.assert_called_once_with(comment_id)


@pytest.mark.asyncio
async def test_delete_comment_raise_generic_error(
    mock_session: AsyncSession, comment_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = AsyncMock()

    comments_repository = CommentsRepository(
        mock_session, posts_repository, users_repository
    )

    with patch.object(
        CommentsRepository, "delete_comment", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await comments_repository.delete_comment(comment_id)

        mock.assert_called_once_with(comment_id)
