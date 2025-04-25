from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from blog_api.commands.app import app
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

    with patch.object(
        UsersRepository, "get_users", AsyncMock(return_value=mock_users_out_inserted)
    ) as user_mock:
        result = await client.get(
            f"{admin_url}/users",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()) > 0

        user_mock.assert_awaited_once()

    app.dependency_overrides.clear()
