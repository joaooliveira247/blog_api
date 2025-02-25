from unittest.mock import AsyncMock, patch
from uuid import UUID
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
from blog_api.contrib.errors import (
    UnableCreateEntity,
    DatabaseError,
    GenericError,
    NoResultFound,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from pytest import raises


@pytest.mark.asyncio
async def test_create_user_success(
    mock_session: AsyncSession, mock_user: UserModel, user_id: UUID
):
    repository = UsersRepository(mock_session)

    mock_session.commit.side_effect = lambda: setattr(mock_user, "id", user_id)

    await repository.create_user(mock_user)

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
        await repository.create_user(mock_user)

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_raise_database_error(
    mock_session: AsyncSession, mock_user: UserModel
):
    repository = UsersRepository(mock_session)

    mock_session.commit = AsyncMock(
        side_effect=OperationalError("Connection refused", {}, None)
    )
    mock_session.rollback = AsyncMock()

    with raises(DatabaseError, match="Database integrity error"):
        await repository.create_user(mock_user)

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_raise_generic_error(
    mock_session: AsyncSession, mock_user: UserModel
):
    repository = UsersRepository(mock_session)

    mock_session.commit = AsyncMock(side_effect=Exception())
    mock_session.rollback = AsyncMock()

    with raises(GenericError, match="Generic Error"):
        await repository.create_user(mock_user)

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_users_return_success(
    mock_session: AsyncSession, mock_users_inserted: list[UserModel]
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_users", new_callable=AsyncMock
    ) as mock_get_users:
        mock_get_users.return_value = mock_users_inserted

        users = await repository.get_users()

        mock_get_users.assert_called_once()
        assert users == mock_users_inserted
        assert len(users) == len(mock_users_inserted)


@pytest.mark.asyncio
async def test_get_users_return_success_but_empty(mock_session: AsyncSession):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_users", new_callable=AsyncMock
    ) as mock_get_users:
        mock_get_users.return_value = []

        users = await repository.get_users()

        mock_get_users.assert_called_once()
        assert users == []
        assert len(users) == 0


@pytest.mark.asyncio
async def test_get_users_raise_database_error(mock_session: AsyncSession):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_users", new_callable=AsyncMock
    ) as mock_get_users:
        mock_get_users.side_effect = DatabaseError

        with raises(DatabaseError):
            await repository.get_users()

        mock_get_users.assert_called_once()


@pytest.mark.asyncio
async def test_get_users_raise_generic_error(mock_session: AsyncSession):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_users", new_callable=AsyncMock
    ) as mock_get_users:
        mock_get_users.side_effect = GenericError

        with raises(GenericError):
            await repository.get_users()

        mock_get_users.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_id_success(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_user_inserted

        user = await repository.get_user_by_id(mock_user_inserted.id)

        mock.assert_called_once_with(mock_user_inserted.id)
        assert user == mock_user_inserted


@pytest.mark.asyncio
async def test_get_user_by_id_success_return_none(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_id", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        user = await repository.get_user_by_id(user_id)

        mock.assert_awaited_once_with(user_id)
        assert user is None


@pytest.mark.asyncio
async def test_get_user_by_id_raise_database_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with raises(DatabaseError):
            await repository.get_user_by_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_by_id_raise_generic_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_id", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with raises(GenericError):
            await repository.get_user_by_id(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_by_query_username_success(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_user_inserted

        method_arg = UserModel(username=mock_user_inserted.username)

        user = await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)
        assert user == mock_user_inserted


@pytest.mark.asyncio
async def test_get_user_by_query_email_success(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_user_inserted

        method_arg = UserModel(email=mock_user_inserted.email)

        user = await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)
        assert user == mock_user_inserted


@pytest.mark.asyncio
async def test_get_user_by_query_full_success(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.return_value = mock_user_inserted

        method_arg = UserModel(
            username=mock_user_inserted.username, email=mock_user_inserted.email
        )

        user = await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)
        assert user == mock_user_inserted


@pytest.mark.asyncio
async def test_get_user_by_query_success_return_none(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        method_arg = UserModel(
            username=mock_user_inserted.username, email=mock_user_inserted.email
        )

        user = await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)
        assert user is None


@pytest.mark.asyncio
async def test_get_user_by_query_raise_database_error(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        method_arg = UserModel(
            username=mock_user_inserted.username, email=mock_user_inserted.email
        )

        with raises(DatabaseError):
            await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)


@pytest.mark.asyncio
async def test_get_user_by_query_raise_generic_error(
    mock_session: AsyncSession, mock_user_inserted: UserModel
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "get_user_by_query", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        method_arg = UserModel(
            username=mock_user_inserted.username, email=mock_user_inserted.email
        )

        with raises(GenericError):
            await repository.get_user_by_query(method_arg)

        mock.assert_called_once_with(method_arg)


@pytest.mark.asyncio
async def test_update_user_password_success(
    mock_session: AsyncSession,
    mock_user_inserted: UserModel,
    hashed_string_password: str,
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_password", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        await repository.update_user_password(
            mock_user_inserted.id, hashed_string_password
        )

        mock.assert_called_once_with(mock_user_inserted.id, hashed_string_password)


@pytest.mark.asyncio
async def test_update_user_raise_no_result_found_error(
    mock_session: AsyncSession, user_id: UUID, hashed_string_password
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_password", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = NoResultFound

        with raises(NoResultFound):
            await repository.update_user_password(user_id, hashed_string_password)

        mock.assert_called_once_with(user_id, hashed_string_password)


@pytest.mark.asyncio
async def test_update_user_raise_database_error(
    mock_session: AsyncSession, user_id: UUID, hashed_string_password
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_password", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with raises(DatabaseError):
            await repository.update_user_password(user_id, hashed_string_password)

        mock.assert_called_once_with(user_id, hashed_string_password)


@pytest.mark.asyncio
async def test_update_user_raise_unable_update_entity_error(
    mock_session: AsyncSession, user_id: UUID, hashed_string_password
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_password", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = UnableUpdateEntity

        with raises(UnableUpdateEntity):
            await repository.update_user_password(user_id, hashed_string_password)

        mock.assert_called_once_with(user_id, hashed_string_password)


@pytest.mark.asyncio
async def test_update_user_raise_generic_error(
    mock_session: AsyncSession, user_id: UUID, hashed_string_password
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_password", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with raises(GenericError):
            await repository.update_user_password(user_id, hashed_string_password)

        mock.assert_called_once_with(user_id, hashed_string_password)


@pytest.mark.asyncio
async def test_update_user_role_success(
    mock_session: AsyncSession,
    mock_user_inserted: UserModel,
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_role", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None

        await repository.update_user_role(mock_user_inserted.id, "Administrator")

        mock.assert_called_once_with(mock_user_inserted.id, "Administrator")


@pytest.mark.asyncio
async def test_update_user_role_raise_no_result_found_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_role", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = NoResultFound

        with raises(NoResultFound):
            await repository.update_user_role(user_id, "Administrator")

        mock.assert_called_once_with(user_id, "Administrator")


@pytest.mark.asyncio
async def test_update_user_role_raise_database_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_role", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = DatabaseError

        with raises(DatabaseError):
            await repository.update_user_role(user_id, "Administrator")

        mock.assert_called_once_with(user_id, "Administrator")


@pytest.mark.asyncio
async def test_update_user_role_raise_unable_update_entity_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_role", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = UnableUpdateEntity

        with raises(UnableUpdateEntity):
            await repository.update_user_role(user_id, "Administrator")

        mock.assert_called_once_with(user_id, "Administrator")


@pytest.mark.asyncio
async def test_update_user_role_raise_generic_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(
        UsersRepository, "update_user_role", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = GenericError

        with raises(GenericError):
            await repository.update_user_role(user_id, "Administrator")

        mock.assert_called_once_with(user_id, "Administrator")


@pytest.mark.asyncio
async def test_delete_user_success(
    mock_session: AsyncSession,
    user_id: UUID,
):
    repository = UsersRepository(mock_session)

    with patch.object(UsersRepository, "delete_user", new_callable=AsyncMock) as mock:
        mock.return_value = None

        await repository.delete_user(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_delete_user_raise_no_result_found_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(UsersRepository, "delete_user", new_callable=AsyncMock) as mock:
        mock.side_effect = NoResultFound

        with raises(NoResultFound):
            await repository.delete_user(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_delete_user_raise_database_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(UsersRepository, "delete_user", new_callable=AsyncMock) as mock:
        mock.side_effect = DatabaseError

        with raises(DatabaseError):
            await repository.delete_user(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_delete_user_raise_unable_delete_entity_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(UsersRepository, "delete_user", new_callable=AsyncMock) as mock:
        mock.side_effect = UnableDeleteEntity

        with raises(UnableDeleteEntity):
            await repository.delete_user(user_id)

        mock.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_delete_user_raise_generic_error(
    mock_session: AsyncSession, user_id: UUID
):
    repository = UsersRepository(mock_session)

    with patch.object(UsersRepository, "delete_user", new_callable=AsyncMock) as mock:
        mock.side_effect = GenericError

        with raises(GenericError):
            await repository.delete_user(user_id)

        mock.assert_called_once_with(user_id)
