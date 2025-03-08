from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from blog_api.repositories.posts import PostsRepository
from blog_api.models.posts import PostModel
from blog_api.models.posts import UserModel
from blog_api.contrib.errors import (
    DatabaseError,
    GenericError,
    NoResultFound,
    UnableCreateEntity,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from uuid import UUID
import pytest

from blog_api.schemas.posts import PostOut


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


@pytest.mark.asyncio
async def test_create_post_raise_generic_error(
    mock_session: AsyncMock, mock_post: MagicMock
):
    users_repository = AsyncMock()
    users_repository.get_user_by_id.return_value = MagicMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    mock_session.flush.side_effect = Exception()

    with pytest.raises(GenericError, match="Generic Error"):
        await posts_repository.create_post(mock_post)

    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_posts_return_success(
    mock_session: AsyncMock, mock_posts_inserted: list[PostOut]
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "get_posts", new_callable=AsyncMock) as mock:
        mock.return_value = mock_posts_inserted

        posts = await posts_repository.get_posts()

        mock.assert_called_once()
        assert posts == mock_posts_inserted
        assert len(posts) == len(mock_posts_inserted)


@pytest.mark.asyncio
async def test_get_posts_return_success_but_empty(
    mock_session: AsyncMock,
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "get_posts", new_callable=AsyncMock) as mock:
        mock.return_value = []

        posts = await posts_repository.get_posts()

        mock.assert_called_once()
        assert posts == []
        assert len(posts) == 0


@pytest.mark.asyncio
async def test_get_posts_raise_database_error(
    mock_session: AsyncMock,
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "get_posts", new_callable=AsyncMock) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await posts_repository.get_posts()

        mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_posts_raise_generic_error(
    mock_session: AsyncMock,
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "get_posts", new_callable=AsyncMock) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await posts_repository.get_posts()

        mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_post_by_id_return_success(
    mock_session: AsyncMock, mock_post_inserted: PostOut, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_post_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_post_inserted

        result = await posts_repository.get_post_by_id(post_id)

        mock.assert_called_once_with(post_id)
        assert result == mock_post_inserted


@pytest.mark.asyncio
async def test_get_post_by_id_return_none(mock_session: AsyncMock, post_id: UUID):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_post_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        result = await posts_repository.get_post_by_id(post_id)

        mock.assert_called_once_with(post_id)
        assert result is None


@pytest.mark.asyncio
async def test_get_post_by_id_raise_database_error(
    mock_session: AsyncMock, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_post_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await posts_repository.get_post_by_id(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_get_post_by_id_raise_generic_error(
    mock_session: AsyncMock, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_post_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await posts_repository.get_post_by_id(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_get_post_by_user_id_success(
    mock_session: AsyncMock, user_id: UUID, mock_posts_inserted: list[PostOut]
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    mock_return_value = mock_posts_inserted[1:2]

    for post in mock_return_value:
        post.author = "joshingly"

    with patch.object(
        PostsRepository, "get_posts_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_return_value

        posts = await posts_repository.get_posts_by_user_id(user_id)

        mock.assert_called_once_with(user_id)
        assert mock_return_value == posts
        assert len(mock_return_value) == len(posts)


@pytest.mark.asyncio
async def test_get_post_by_user_id_return_empty(mock_session: AsyncMock, user_id: UUID):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_posts_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []

        posts = await posts_repository.get_posts_by_user_id(user_id)

        mock.assert_called_once_with(user_id)
        assert posts == []
        assert len(posts) == 0


@pytest.mark.asyncio
async def test_get_post_by_user_id_raise_database_error(
    mock_session: AsyncMock, user_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_posts_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await posts_repository.get_posts_by_user_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_post_by_user_id_raise_generic_error(
    mock_session: AsyncMock, user_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(
        PostsRepository, "get_posts_by_user_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await posts_repository.get_posts_by_user_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_post_success(
    mock_session: AsyncMock, post_id: UUID, mock_update_post: dict
):
    users_repository = AsyncMock()

    posts_reposiotry = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "update_post", new_callable=AsyncMock) as mock:
        mock.return_value = None

        await posts_reposiotry.update_post(post_id, mock_update_post)

        mock.assert_called_once_with(post_id, mock_update_post)


@pytest.mark.asyncio
async def test_update_post_raise_no_result_found(
    mock_session: AsyncMock, post_id: UUID, mock_update_post: dict
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "update_post", new_callable=AsyncMock) as mock:
        mock.side_effect = NoResultFound("post_id")

        with pytest.raises(NoResultFound, match="Result not found with post_id"):
            await posts_repository.update_post(post_id, mock_update_post)

        mock.assert_called_once_with(post_id, mock_update_post)


@pytest.mark.asyncio
async def test_update_post_raise_database_error(
    mock_session: AsyncMock, post_id: UUID, mock_update_post: dict
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "update_post", new_callable=AsyncMock) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await posts_repository.update_post(post_id, mock_update_post)

        mock.assert_called_once_with(post_id, mock_update_post)


@pytest.mark.asyncio
async def test_update_post_raise_unable_update_entity(
    mock_session: AsyncMock, post_id: UUID, mock_update_post: dict
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "update_post", new_callable=AsyncMock) as mock:
        mock.side_effect = UnableUpdateEntity

        with pytest.raises(UnableUpdateEntity, match="Unable Update Entity"):
            await posts_repository.update_post(post_id, mock_update_post)

        mock.assert_called_once_with(post_id, mock_update_post)


@pytest.mark.asyncio
async def test_update_post_raise_generic_error(
    mock_session: AsyncMock, post_id: UUID, mock_update_post: dict
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "update_post", new_callable=AsyncMock) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await posts_repository.update_post(post_id, mock_update_post)

        mock.assert_called_once_with(post_id, mock_update_post)


@pytest.mark.asyncio
async def test_delete_post_return_success(mock_session: AsyncMock, post_id: UUID):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "delete_post", new_callable=AsyncMock) as mock:
        mock.return_value = None

        await posts_repository.delete_post(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_raise_unable_delete_entity(
    mock_session: AsyncMock, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "delete_post", new_callable=AsyncMock) as mock:
        mock.side_effect = UnableDeleteEntity

        with pytest.raises(UnableDeleteEntity, match="Unable Delete Entity"):
            await posts_repository.delete_post(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_raise_database_error(mock_session: AsyncMock, post_id: UUID):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "delete_post", new_callable=AsyncMock) as mock:
        mock.side_effect = DatabaseError

        with pytest.raises(DatabaseError, match="Database integrity error"):
            await posts_repository.delete_post(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_raise_no_result_found(
    mock_session: AsyncMock, post_id: UUID
):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "delete_post", new_callable=AsyncMock) as mock:
        mock.side_effect = NoResultFound("user_id")

        with pytest.raises(NoResultFound, match="Result not found with user_id"):
            await posts_repository.delete_post(post_id)

        mock.assert_called_once_with(post_id)


@pytest.mark.asyncio
async def test_delete_post_raise_generic_error(mock_session: AsyncMock, post_id: UUID):
    users_repository = AsyncMock()

    posts_repository = PostsRepository(mock_session, users_repository)

    with patch.object(PostsRepository, "delete_post", new_callable=AsyncMock) as mock:
        mock.side_effect = GenericError

        with pytest.raises(GenericError, match="Generic Error"):
            await posts_repository.delete_post(post_id)

        mock.assert_called_once_with(post_id)
