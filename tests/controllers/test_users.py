from typing import Any
from unittest.mock import AsyncMock, patch, ANY
from uuid import UUID

from pydantic import ValidationError
import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient

from blog_api.contrib.errors import (
    DatabaseError,
    GenericError,
    InvalidResource,
    TokenError,
    UnableCreateEntity,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository
from blog_api.commands.app import app


@pytest.mark.asyncio
async def test_create_user_return_201_created(
    client: AsyncClient,
    mock_user: UserModel,
    user_id: UUID,
    account_url: str,
    user_agent,
):
    user_body: dict[str, Any] = {
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Abc@1234",
    }

    with patch.object(
        UsersRepository, "create_user", new_callable=AsyncMock
    ) as mock_create_user:
        mock_create_user.return_value = user_id

        response = await client.post(
            f"{account_url}/sign-up", json=user_body, headers={"User-Agent": user_agent}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": str(user_id)}


@pytest.mark.asyncio
async def test_create_user_return_422_invalid_request_body(
    client: AsyncClient, mock_user: UserModel, account_url: str
):
    user_body: dict[str, Any] = {
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "12345678",
    }

    with patch.object(
        UsersRepository, "create_user", new_callable=AsyncMock
    ) as mock_create_user:
        mock_create_user.side_effect = ValidationError

        response = await client.post(f"{account_url}/sign-up", json=user_body)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"][0]["msg"]
            == "Value error, Wrong password format! characters missing: lower, upper, special"
        )


@pytest.mark.asyncio
async def test_create_user_return_500_internal_server_error_database_error(
    client: AsyncClient, mock_user: UserModel, account_url: str
):
    user_body: dict[str, Any] = {
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Abc@1234",
    }

    with patch.object(
        UsersRepository, "create_user", new_callable=AsyncMock
    ) as mock_create_user:
        mock_create_user.side_effect = DatabaseError

        response = await client.post(f"{account_url}/sign-up", json=user_body)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_create_user_return_409_conflict_unable_create_entity(
    client: AsyncClient, mock_user: UserModel, account_url: str
):
    user_body: dict[str, Any] = {
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Abc@1234",
    }

    with patch.object(
        UsersRepository, "create_user", new_callable=AsyncMock
    ) as mock_create_user:
        mock_create_user.side_effect = UnableCreateEntity

        response = await client.post(f"{account_url}/sign-up", json=user_body)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": "Unable Create Entity: Field value already exists"
        }


@pytest.mark.asyncio
async def test_create_user_return_500_internal_server_error_generic(
    client: AsyncClient, mock_user: UserModel, account_url: str
):
    user_body: dict[str, Any] = {
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Abc@1234",
    }

    with patch.object(
        UsersRepository, "create_user", new_callable=AsyncMock
    ) as mock_create_user:
        mock_create_user.side_effect = GenericError

        response = await client.post(f"{account_url}/sign-up", json=user_body)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_login_200_success(
    client: AsyncClient, account_url: str, password, mock_user, user_agent
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    jwt = gen_jwt(360, mock_user)

    with (
        patch(
            "blog_api.controllers.users.authenticate",
            new_callable=AsyncMock,
        ) as mock_authenticate,
        patch("blog_api.controllers.users.gen_jwt") as mock_jwt,
    ):
        mock_authenticate.return_value = mock_user
        mock_jwt.return_value = jwt

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": user_agent,
            },
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {"access_token": jwt, "token_type": "bearer"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)
        mock_jwt.assert_called_once()


@pytest.mark.asyncio
async def test_login_return_500_internal_server_error_database_error(
    client: AsyncClient, account_url: str, password, mock_user
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    with patch(
        "blog_api.controllers.users.authenticate",
        new_callable=AsyncMock,
    ) as mock_authenticate:
        mock_authenticate.side_effect = DatabaseError

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)


@pytest.mark.asyncio
async def test_login_return_500_internal_server_error_token_error(
    client: AsyncClient, account_url: str, password, mock_user
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    with (
        patch(
            "blog_api.controllers.users.authenticate",
            new_callable=AsyncMock,
        ) as mock_authenticate,
        patch("blog_api.controllers.users.gen_jwt") as mock_jwt,
    ):
        mock_authenticate.return_value = mock_user
        mock_jwt.side_effect = TokenError

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Token Error"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)
        mock_jwt.assert_called_once()


@pytest.mark.asyncio
async def test_login_return_400_bad_request_invalid_email(
    client: AsyncClient, account_url: str, password, mock_user
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    with patch(
        "blog_api.controllers.users.authenticate",
        new_callable=AsyncMock,
    ) as mock_authenticate:
        mock_authenticate.side_effect = InvalidResource("email")

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": "email invalid"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)


@pytest.mark.asyncio
async def test_login_return_400_bad_request_invalid_password(
    client: AsyncClient, account_url: str, password, mock_user
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    with patch(
        "blog_api.controllers.users.authenticate",
        new_callable=AsyncMock,
    ) as mock_authenticate:
        mock_authenticate.side_effect = InvalidResource("password")

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": "password invalid"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)


@pytest.mark.asyncio
async def test_login_return_500_internal_server_error_generic_error(
    client: AsyncClient, account_url: str, password, mock_user
):
    login_body: dict[str, Any] = {"username": mock_user.email, "password": password}

    with patch(
        "blog_api.controllers.users.authenticate",
        new_callable=AsyncMock,
    ) as mock_authenticate:
        mock_authenticate.side_effect = GenericError

        result = await client.post(
            f"{account_url}/sign-in",
            data=login_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_authenticate.assert_awaited_once_with(ANY, mock_user.email, password)


@pytest.mark.asyncio
async def test_get_current_user_200_success(
    client: AsyncClient, account_url: str, mock_user_out_inserted, mock_user, user_agent
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{account_url}/",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_200_OK
    assert result.json()["email"] == mock_user_out_inserted.email

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_current_user_return_401_unauthorized(
    client: AsyncClient, account_url: str, mock_user
):
    jwt = gen_jwt(360, mock_user)

    async def override_get_current_user_error():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User can't be authenticated",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user_error

    result = await client.get(
        f"{account_url}/", headers={"Authorization": f"Bearer {jwt}"}
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "User can't be authenticated"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_current_user_return_401_unauthorized_token_error(
    client: AsyncClient, account_url: str, mock_user
):
    jwt = gen_jwt(360, mock_user)

    async def override_get_current_user_error():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Error",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user_error

    result = await client.get(
        f"{account_url}/", headers={"Authorization": f"Bearer {jwt}"}
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "Token Error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_current_user_return_401_unauthorized_generic_error(
    client: AsyncClient, account_url: str, mock_user
):
    jwt = gen_jwt(360, mock_user)

    async def override_get_current_user_error():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Generic Error",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user_error

    result = await client.get(
        f"{account_url}/", headers={"Authorization": f"Bearer {jwt}"}
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "Generic Error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_204_success(
    mock_user, client: AsyncClient, account_url, mock_user_out_inserted, user_agent
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_user_by_id", new=AsyncMock(return_value=mock_user)
        ),
        patch.object(
            UsersRepository, "update_user_password", new=AsyncMock(return_value=None)
        ) as user_mock,
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": "Abc4@6789"},
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.text == ""

        user_mock.assert_awaited_once()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_422_invalid_password_format(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.put(
        f"{account_url}/password",
        json={"password": "A12346789"},
        headers={"Authorization": f"Bearer {jwt}"},
    )

    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        result.json()["detail"][0]["msg"]
        == "Value error, Wrong password format! characters missing: lower, special"
    )
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_401_user_not_found(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "get_user_by_id", new=AsyncMock(return_value=None)
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": "Abc4@6789"},
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "User not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_409_same_password(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
    password,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "get_user_by_id", new=AsyncMock(return_value=mock_user)
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": password},
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_409_CONFLICT
        assert result.json() == {
            "detail": "New password cannot be the same as current password"
        }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_500_database_error(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_user_by_id", new=AsyncMock(return_value=mock_user)
        ),
        patch.object(
            UsersRepository,
            "update_user_password",
            new=AsyncMock(side_effect=DatabaseError),
        ) as user_mock,
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": "Abc4@6789"},
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        user_mock.assert_awaited_once()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_500_unable_update_entity_error(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_user_by_id", new=AsyncMock(return_value=mock_user)
        ),
        patch.object(
            UsersRepository,
            "update_user_password",
            new=AsyncMock(side_effect=UnableUpdateEntity),
        ) as user_mock,
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": "Abc4@6789"},
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Update Entity"}

        user_mock.assert_awaited_once()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_password_500_generic_error(
    mock_user,
    client: AsyncClient,
    account_url,
    mock_user_out_inserted,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_user_by_id", new=AsyncMock(return_value=mock_user)
        ),
        patch.object(
            UsersRepository,
            "update_user_password",
            new=AsyncMock(side_effect=GenericError),
        ) as user_mock,
    ):
        result = await client.put(
            f"{account_url}/password",
            json={"password": "Abc4@6789"},
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_204_success(
    mock_user, client: AsyncClient, account_url, mock_user_out_inserted, user_agent
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", new=AsyncMock(return_value=None)
    ) as user_mock:
        result = await client.delete(
            f"{account_url}/",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.text == ""

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_500_unable_delete_entity(
    mock_user, client: AsyncClient, account_url, mock_user_out_inserted
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", new=AsyncMock(side_effect=UnableDeleteEntity)
    ) as user_mock:
        result = await client.delete(
            f"{account_url}/",
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Delete Entity"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_500_database_error(
    mock_user, client: AsyncClient, account_url, mock_user_out_inserted
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", new=AsyncMock(side_effect=DatabaseError)
    ) as user_mock:
        result = await client.delete(
            f"{account_url}/",
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_500_generic_error(
    mock_user, client: AsyncClient, account_url, mock_user_out_inserted
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", new=AsyncMock(side_effect=GenericError)
    ) as user_mock:
        result = await client.delete(
            f"{account_url}/",
            headers={"Authorization": f"Bearer {jwt}"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()
