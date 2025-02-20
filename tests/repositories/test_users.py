from unittest.mock import AsyncMock
from uuid import UUID
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
from blog_api.contrib.errors import UnableCreateEntity
from pytest import raises


@pytest.mark.asyncio
async def test_create_user_success(
    mock_session: AsyncSession, mock_user: UserModel, user_id: UUID
):
    repository = UsersRepository(mock_session)

    mock_session.commit.side_effect = lambda: setattr(mock_user, "id", user_id)

    await repository.create(mock_user)

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    assert mock_user.id == user_id


@pytest.mark.asyncio
async def test_create_user_raise_unable_create_entity_error(
    mock_session: AsyncSession, mock_user: UserModel
):
    repository = UsersRepository(mock_session)

    mock_session.commit = AsyncMock(
        side_effect=IntegrityError("duplicate key", {}, None)
    )
    mock_session.rollback = AsyncMock()

    with raises(
        UnableCreateEntity, match="Unable Create Entity: Field value already exists"
    ):
        await repository.create(mock_user)

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
