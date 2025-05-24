from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from blog_api.commands.app import app
from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    NoResultFound,
    UnableCreateEntity,
)
from blog_api.core.cache import Cache
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


@pytest.mark.asyncio
async def test_create_comment_raise_500_unable_create_entity_error(
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
        AsyncMock(side_effect=UnableCreateEntity),
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
        assert result.json() == {
            "detail": "Unable Create Entity: Field value already exists"
        }

        comment_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_comment_raise_500_generic_error(
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
        AsyncMock(side_effect=GenericError),
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
        assert result.json() == {"detail": "Generic Error"}

        comment_mock.assert_awaited_once()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_success(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comments_inserted_same_post,
):
    post_id = mock_comments_inserted_same_post[0].post_id

    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(return_value=mock_comments_inserted_same_post),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_success_from_cache(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comments_inserted_same_post,
):
    post_id = mock_comments_inserted_same_post[0].post_id

    with patch.object(
        Cache, "get", AsyncMock(return_value=mock_comments_inserted_same_post)
    ) as mock_comments:
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_404_no_result_found(
    client: AsyncClient, comments_url, user_agent, post_id
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(side_effect=NoResultFound("post_id")),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Result not found with post_id"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_500_generic_error(
    client: AsyncClient, comments_url, user_agent, post_id
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(side_effect=GenericError),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_500_generic_error_from_cache(
    client: AsyncClient, comments_url, user_agent, post_id
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=GenericError),
    ) as mock_comments:
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_500_cache_error_when_add(
    client: AsyncClient,
    comments_url,
    user_agent,
    post_id,
    mock_comments_inserted_same_post,
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(return_value=mock_comments_inserted_same_post),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_500_encoding_error_when_add(
    client: AsyncClient,
    comments_url,
    user_agent,
    post_id,
    mock_comments_inserted_same_post,
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(return_value=mock_comments_inserted_same_post),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=EncodingError),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {
            "detail": "Error when try encoding one object"
        }

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_post_id_raise_500_generic_error_when_add(
    client: AsyncClient,
    comments_url,
    user_agent,
    post_id,
    mock_comments_inserted_same_post,
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_post_id",
            AsyncMock(return_value=mock_comments_inserted_same_post),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(
            f"{comments_url}/post/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_user_id_success(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comments_inserted_same_author,
):
    author_id = mock_comments_inserted_same_author[0].author_id

    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_user_id",
            AsyncMock(return_value=mock_comments_inserted_same_author),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/user/{author_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_user_id_success_from_cache(
    client: AsyncClient,
    comments_url,
    user_agent,
    mock_comments_inserted_same_author,
):
    author_id = mock_comments_inserted_same_author[0].author_id

    with patch.object(
        Cache,
        "get",
        AsyncMock(return_value=mock_comments_inserted_same_author),
    ) as mock_comments:
        result = await client.get(
            f"{comments_url}/user/{author_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_404_no_result_found(
    client: AsyncClient, comments_url, user_agent, post_id
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_user_id",
            AsyncMock(side_effect=NoResultFound("user_id")),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/user/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Result not found with user_id"}

        mock_comments.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comments_by_user_id_raise_500_database_error(
    client: AsyncClient, comments_url, user_agent, post_id
):
    with (
        patch.object(
            CommentsRepository,
            "get_comments_by_user_id",
            AsyncMock(side_effect=DatabaseError),
        ) as mock_comments,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{comments_url}/user/{post_id}",
            headers={"User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

        mock_comments.assert_awaited_once()
