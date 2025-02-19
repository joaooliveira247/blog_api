from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
import pytest


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
