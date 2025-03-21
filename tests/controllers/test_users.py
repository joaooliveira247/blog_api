from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import UUID
from httpx import AsyncClient
from fastapi import status
import pytest

from blog_api.contrib.errors import DatabaseError, UnableCreateEntity
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository


@pytest.mark.asyncio
async def test_create_user_return_201_created(
    client: AsyncClient, mock_user: UserModel, user_id: UUID, users_url: str
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

        response = await client.post(users_url, json=user_body)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": str(user_id)}


@pytest.mark.asyncio
async def test_create_user_return_500_internal_server_error_database_error(
    client: AsyncClient, mock_user: UserModel, users_url: str
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

        response = await client.post(users_url, json=user_body)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_create_user_return_409_conflict_unable_create_entity(
    client: AsyncClient, mock_user: UserModel, users_url: str
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

        response = await client.post(users_url, json=user_body)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": "Unable Create Entity: Field value already exists"
        }
