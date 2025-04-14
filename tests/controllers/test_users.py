from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import UUID

from pydantic import ValidationError
import pytest
from fastapi import status
from httpx import AsyncClient

from blog_api.contrib.errors import DatabaseError, GenericError, UnableCreateEntity
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository


@pytest.mark.asyncio
async def test_create_user_return_201_created(
    client: AsyncClient, mock_user: UserModel, user_id: UUID, account_url: str
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

        response = await client.post(f"{account_url}/sign-up", json=user_body)

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
