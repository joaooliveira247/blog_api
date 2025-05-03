from fastapi import status
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
import pytest

from blog_api.commands.app import app
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.repositories.posts import PostsRepository
from blog_api.schemas.posts import PostOut


@pytest.mark.asyncio
async def test_create_post_success(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository, "create_post", AsyncMock(return_value=mock_post_inserted.id)
    ) as mock_post:
        result = await client.post(
            f"{posts_url}/",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json={
                "title": mock_post_inserted.title,
                "categories": mock_post_inserted.categories,
                "content": mock_post_inserted.content,
            },
        )

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_201_CREATED
    assert result.json() == {"id": str(mock_post_inserted.id)}

    app.dependency_overrides.clear()
