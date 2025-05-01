from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from blog_api.commands.app import app
from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    NoResultFound,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from blog_api.core.cache import Cache
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.repositories.users import UsersRepository
from fastapi import status


@pytest.mark.asyncio
async def test_get_users_return_success(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_users_out_inserted,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_users",
            AsyncMock(return_value=mock_users_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache, get=AsyncMock(return_value=None), add=AsyncMock(return_value=None)
        ),
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()) > 0

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_email_return_success(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_query",
            AsyncMock(return_value=mock_user_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache, get=AsyncMock(return_value=None), add=AsyncMock(return_value=None)
        ),
    ):
        result = await client.get(
            f"{admin_url}/users?email={mock_user_out_inserted.email}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) == 1

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_email_from_cache_return_success(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        Cache,
        get=AsyncMock(return_value=mock_user_out_inserted),
        add=AsyncMock(return_value=None),
    ):
        result = await client.get(
            f"{admin_url}/users?email={mock_user_out_inserted.email}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_email_raise_invalid_email(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/users?email=1234@123",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    print(result.json(), result.status_code)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        result.json()["detail"][0]["msg"]
        == "value is not a valid email address: The part after the @-sign is not valid. It should have a period."
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_return_success_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_users_out_inserted,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        Cache,
        get=AsyncMock(return_value=mock_users_out_inserted),
        add=AsyncMock(return_value=None),
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()) > 0

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_database_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_users", AsyncMock(side_effect=DatabaseError)
        ) as user_mock,
        patch.object(Cache, "get", AsyncMock(return_value=None)) as mock_cache,
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        user_mock.assert_awaited_once()
        mock_cache.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_401_invalid_permissions(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/users",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "invalid permissions"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_generic_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository, "get_users", AsyncMock(side_effect=GenericError)
        ) as user_mock,
        patch.object(Cache, "get", AsyncMock(return_value=None)) as mock_cache,
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()
        mock_cache.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_cache_error_when_get_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            Cache, "get", AsyncMock(side_effect=CacheError("Cache Error"))
        ) as mock_cache,
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}

        mock_cache.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_cache_error_when_add_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    mock_users_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_users",
            AsyncMock(return_value=mock_users_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_encoding_error_when_add_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    mock_users_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_users",
            AsyncMock(return_value=mock_users_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=EncodingError),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Error when try encoding one object"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_users_raise_500_generic_error_when_add_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    mock_users_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_users",
            AsyncMock(return_value=mock_users_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_success(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_id",
            AsyncMock(return_value=mock_user_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=None),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["id"] == str(mock_user_out_inserted.id)

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_success_from_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        Cache,
        "get",
        new=AsyncMock(return_value=mock_user_out_inserted),
    ) as user_mock:
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["id"] == str(mock_user_out_inserted.id)

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_422_invalid_uuid(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/users/123",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        result.json()["detail"][0]["msg"]
        == "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3"
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_cache_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        Cache,
        "get",
        new=AsyncMock(side_effect=CacheError("Cache Error")),
    ) as user_mock:
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_encoding_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        Cache,
        "get",
        new=AsyncMock(side_effect=EncodingError),
    ) as user_mock:
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Error when try encoding one object"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_database_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_id",
            AsyncMock(side_effect=DatabaseError),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=None),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_generic_error(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_id",
            AsyncMock(side_effect=GenericError),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=None),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_cache_error_when_add_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_id",
            AsyncMock(return_value=mock_user_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_user_by_id_raise_500_generic_error_when_add_cache(
    mock_user,
    client: AsyncClient,
    admin_url,
    mock_user_out_inserted,
    user_agent,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with (
        patch.object(
            UsersRepository,
            "get_user_by_id",
            AsyncMock(return_value=mock_user_out_inserted),
        ) as user_mock,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_return_success(
    client: AsyncClient, mock_user, admin_url, user_agent, mock_user_out_inserted
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", AsyncMock(return_value=None)
    ) as mock_user:
        result = await client.delete(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.text == ""

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_raise_401_invalid_permission(
    client: AsyncClient, mock_user, admin_url, user_agent, mock_user_out_inserted
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.delete(
        f"{admin_url}/users/{mock_user_out_inserted.id}",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "invalid permissions"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_raise_500_database_error(
    client: AsyncClient, mock_user, admin_url, user_agent, mock_user_out_inserted
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", AsyncMock(side_effect=DatabaseError)
    ) as mock_user:
        result = await client.delete(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_raise_500_unable_delete_entity_error(
    client: AsyncClient, mock_user, admin_url, user_agent, mock_user_out_inserted
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", AsyncMock(side_effect=UnableDeleteEntity)
    ) as mock_user:
        result = await client.delete(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Delete Entity"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_user_raise_500_generic_error(
    client: AsyncClient, mock_user, admin_url, user_agent, mock_user_out_inserted
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "delete_user", AsyncMock(side_effect=GenericError)
    ) as mock_user:
        result = await client.delete(
            f"{admin_url}/users/{mock_user_out_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_success(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
    mock_users_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    user_update = mock_users_out_inserted[0]

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "update_user_role", AsyncMock(return_value=None)
    ) as mock_user:
        result = await client.patch(
            f"{admin_url}/users/{user_update.id}/role",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={"role": "dev"},
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {"message": "User role updated successfully"}

        mock_user.assert_called_once_with(user_update.id, "dev")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_raise_401_invalid_permissions(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
    mock_users_out_inserted,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    user_update = mock_users_out_inserted[0]

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.patch(
        f"{admin_url}/users/{user_update.id}/role",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        json={"role": "dev"},
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "invalid permissions"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_raise_403_change_own_role(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "dev"
    mock_user_out_inserted.role = "dev"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.patch(
        f"{admin_url}/users/{mock_user_out_inserted.id}/role",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        json={"role": "dev"},
    )

    assert result.status_code == status.HTTP_403_FORBIDDEN
    assert result.json() == {"detail": "you are not allowed to change your own role"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_raise_404_no_result_found(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "update_user_role", AsyncMock(side_effect=NoResultFound)
    ) as mock_user:
        result = await client.patch(
            f"{admin_url}/users/cb972123-113c-435d-9236-93d842489682/role",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={"role": "dev"},
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Result not found"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_raise_500_database_error(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "update_user_role", AsyncMock(side_effect=DatabaseError)
    ) as mock_user:
        result = await client.patch(
            f"{admin_url}/users/cb972123-113c-435d-9236-93d842489682/role",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={"role": "dev"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_role_raise_500_unable_update_entity(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "update_user_role", AsyncMock(side_effect=UnableUpdateEntity)
    ) as mock_user:
        result = await client.patch(
            f"{admin_url}/users/cb972123-113c-435d-9236-93d842489682/role",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={"role": "dev"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Update Entity"}

        mock_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_role_raise_500_generic_error(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        UsersRepository, "update_user_role", AsyncMock(side_effect=GenericError)
    ) as mock_user:
        result = await client.patch(
            f"{admin_url}/users/cb972123-113c-435d-9236-93d842489682/role",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={"role": "dev"},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_user.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_docs_html_as_admin_success(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/docs",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_200_OK
    assert "<title>Admin Docs</title>" in result.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_docs_html_as_dev_success(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "dev"
    mock_user_out_inserted.role = "dev"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/docs",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_200_OK
    assert "<title>Admin Docs</title>" in result.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_docs_html_as_user_raise_401_invalid_permissions(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/docs",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {"detail": "invalid permissions"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_open_api_endpoint_as_admin_success(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "admin"
    mock_user_out_inserted.role = "admin"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/openapi.json",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_200_OK
    assert result.json()["openapi"] == "3.1.0"
    assert "paths" in result.json()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_open_api_endpoint_as_dev_success(
    client: AsyncClient,
    mock_user,
    admin_url,
    user_agent,
    mock_user_out_inserted,
):
    mock_user.role = "dev"
    mock_user_out_inserted.role = "dev"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.get(
        f"{admin_url}/openapi.json",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
    )

    assert result.status_code == status.HTTP_200_OK
    assert result.json()["openapi"] == "3.1.0"
    assert "paths" in result.json()

    app.dependency_overrides.clear()
