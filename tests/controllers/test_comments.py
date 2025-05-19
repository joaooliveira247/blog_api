from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from blog_api.commands.app import app
from blog_api.contrib.errors import DatabaseError, NoResultFound
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.repositories.comments import CommentsRepository


@pytest.mark.asyncio
async def test_create_comment_success(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comment_inserted,
    mock_user_out_inserted,
    mock_user,
):
    jwt = gen_jwt(360, mock_user)
    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        CommentsRepository,
        "create_comment",
        AsyncMock(return_value=mock_comment_inserted.id),
    ) as comment_mock:
        result = await client.post(
            f"{comments_url}/",
            json={
                "content": mock_comment_inserted.content,
                "post_id": str(mock_comment_inserted.id),
            },
            headers={
                "Authorization": f"Bearer {jwt}",
                "User-Agent": user_agent,
            },
        )

        assert result.status_code == status.HTTP_201_CREATED
        assert result.json() == {"id": str(mock_comment_inserted.id)}

        comment_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_comment_raise_404_no_result_found(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comment_inserted,
    mock_user_out_inserted,
    mock_user,
):
    jwt = gen_jwt(360, mock_user)
    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        CommentsRepository,
        "create_comment",
        AsyncMock(side_effect=NoResultFound("post_id")),
    ) as comment_mock:
        result = await client.post(
            f"{comments_url}/",
            json={
                "content": mock_comment_inserted.content,
                "post_id": str(mock_comment_inserted.id),
            },
            headers={
                "Authorization": f"Bearer {jwt}",
                "User-Agent": user_agent,
            },
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Result not found with post_id"}

        comment_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_comment_raise_500_database_error(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comment_inserted,
    mock_user_out_inserted,
    mock_user,
):
    jwt = gen_jwt(360, mock_user)
    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        CommentsRepository,
        "create_comment",
        AsyncMock(side_effect=DatabaseError),
    ) as comment_mock:
        result = await client.post(
            f"{comments_url}/",
            json={
                "content": mock_comment_inserted.content,
                "post_id": str(mock_comment_inserted.id),
            },
            headers={
                "Authorization": f"Bearer {jwt}",
                "User-Agent": user_agent,
            },
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        comment_mock.assert_awaited_once()

    app.dependency_overrides.clear()
