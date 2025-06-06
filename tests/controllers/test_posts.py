from uuid import UUID
from fastapi import status
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
import pytest

from blog_api.commands.app import app
from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    UnableCreateEntity,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from blog_api.core.cache import Cache
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.models.users import UserModel
from blog_api.repositories.posts import PostsRepository
from blog_api.schemas.posts import PostOut
from blog_api.schemas.users import UserOut


@pytest.mark.asyncio
async def test_create_post_success(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user: UserModel,
    mock_user_out_inserted: UserOut,
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


@pytest.mark.asyncio
async def test_create_post_raise_422_invalid_request(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user: UserModel,
    mock_user_out_inserted: UserOut,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.post(
        f"{posts_url}/",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        json={
            "title": mock_post_inserted.title,
            "categories": mock_post_inserted.categories,
        },
    )

    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result.json()["detail"][0]["msg"] == "Field required"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_post_raise_500_database_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user: UserModel,
    mock_user_out_inserted: UserOut,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository, "create_post", AsyncMock(side_effect=DatabaseError)
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

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Database integrity error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_post_raise_500_unable_create_entity(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user: UserModel,
    mock_user_out_inserted: UserOut,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository, "create_post", AsyncMock(side_effect=UnableCreateEntity)
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

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {
        "detail": "Unable Create Entity: Field value already exists"
    }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_post_raise_500_generic_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user: UserModel,
    mock_user_out_inserted: UserOut,
):
    mock_user.role = "user"
    mock_user_out_inserted.role = "user"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository, "create_post", AsyncMock(side_effect=GenericError)
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

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Generic Error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_posts_success(
    client: AsyncClient, posts_url: str, user_agent: str, mock_posts_inserted: PostOut
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(return_value=mock_posts_inserted)
        ) as mock_post,
        patch.multiple(
            Cache, get=AsyncMock(return_value=None), add=AsyncMock(return_value=None)
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()["items"]) > 1


@pytest.mark.asyncio
async def test_get_posts_raise_500_database_error(
    client: AsyncClient, posts_url: str, user_agent: str
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(side_effect=DatabaseError)
        ) as mock_post,
        patch.multiple(
            Cache, get=AsyncMock(return_value=None), add=AsyncMock(return_value=None)
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_get_posts_raise_500_generic_error_from_sql(
    client: AsyncClient, posts_url: str, user_agent: str
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(side_effect=GenericError)
        ) as mock_post,
        patch.multiple(
            Cache, get=AsyncMock(return_value=None), add=AsyncMock(return_value=None)
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_posts_raise_500_cache_error_when_add_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: list[PostOut],
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(return_value=mock_post_inserted)
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_posts_raise_500_encoding_error_when_add_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: list[PostOut],
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(return_value=mock_post_inserted)
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=EncodingError),
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Error when try encoding one object"}


@pytest.mark.asyncio
async def test_get_posts_raise_500_generic_error_when_add_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: list[PostOut],
):
    with (
        patch.object(
            PostsRepository, "get_posts", AsyncMock(return_value=mock_post_inserted)
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_post.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_posts_success_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_posts_inserted: list[PostOut],
):
    with patch.multiple(
        Cache,
        get=AsyncMock(return_value=mock_posts_inserted),
        add=AsyncMock(side_effect=None),
    ):
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()["items"]) > 1


@pytest.mark.asyncio
async def test_get_posts_raise_500_cache_error_when_get_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=CacheError("Cache Error")),
    ) as mock_cache:
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_cache.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_posts_raise_500_generic_error_when_get_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=GenericError),
    ) as mock_cache:
        result = await client.get(f"{posts_url}/", headers={"User-Agent": user_agent})

        mock_cache.assert_awaited_once()

    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_post_by_id_success(
    client: AsyncClient, posts_url: str, user_agent: str, mock_post_inserted
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(return_value=mock_post_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/{mock_post_inserted.id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["title"] == mock_post_inserted.title


@pytest.mark.asyncio
async def test_get_post_by_id_raise_404_not_found(
    client: AsyncClient, posts_url: str, user_agent: str
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(return_value=None),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Post Not Found."}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_database_error(
    client: AsyncClient, posts_url: str, user_agent: str
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(side_effect=DatabaseError),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_generic_error_from_database(
    client: AsyncClient, posts_url: str, user_agent: str
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(side_effect=GenericError),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_post_by_id_success_from_cache(
    client: AsyncClient, posts_url: str, user_agent: str, mock_post_inserted
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(return_value=mock_post_inserted),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["title"] == mock_post_inserted.title


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_cache_error_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=CacheError("Cache Error")),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_generic_error_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
):
    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=GenericError),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_cache_error_when_add(
    client: AsyncClient, posts_url: str, user_agent: str, mock_post_inserted
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(return_value=mock_post_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_encoding_error_when_add(
    client: AsyncClient, posts_url: str, user_agent: str, mock_post_inserted
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(return_value=mock_post_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=EncodingError),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Error when try encoding one object"}


@pytest.mark.asyncio
async def test_get_post_by_id_raise_500_generic_error_when_add(
    client: AsyncClient, posts_url: str, user_agent: str, mock_post_inserted
):
    with (
        patch.object(
            PostsRepository,
            "get_post_by_id",
            AsyncMock(return_value=mock_post_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(
            f"{posts_url}/af557ed2-0a2a-4cd5-bdab-7e0e35c34eb6",
            headers={"User-Agent": user_agent},
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_return_success(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(return_value=mock_posts_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_database_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(side_effect=DatabaseError),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_generic_error_from_sql(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(side_effect=GenericError),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(return_value=None),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_success_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with patch.object(
        Cache,
        "get",
        AsyncMock(return_value=mock_posts_inserted),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_200_OK
        assert len(result.json()["items"]) > 1


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_cache_error_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=CacheError("Cache Error")),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_generic_error_from_cache(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with patch.object(
        Cache,
        "get",
        AsyncMock(side_effect=GenericError),
    ) as mock_post:
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_cache_error_from_cache_when_add(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(side_effect=mock_posts_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=CacheError("Cache Error")),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Cache Error"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_encoding_error_from_cache_when_add(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(side_effect=mock_posts_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=EncodingError),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Error when try encoding one object"}


@pytest.mark.asyncio
async def test_get_posts_by_user_id_raise_500_generic_error_from_cache_when_add(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    user_id: UUID,
    mock_posts_inserted: list[PostOut],
):
    for post in mock_posts_inserted:
        post.author_id = user_id
        post.author_username == "Username"

    with (
        patch.object(
            PostsRepository,
            "get_posts_by_user_id",
            AsyncMock(side_effect=mock_posts_inserted),
        ) as mock_post,
        patch.multiple(
            Cache,
            get=AsyncMock(return_value=None),
            add=AsyncMock(side_effect=GenericError),
        ),
    ):
        result = await client.get(
            f"{posts_url}/user/{user_id}", headers={"User-Agent": user_agent}
        )

        mock_post.assert_awaited_once()

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}


@pytest.mark.asyncio
async def test_update_post_success(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,  # noqa: F811
    mock_update_post,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        update_post=AsyncMock(return_value=None),
    ):
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.text == ""

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_422_invalid_body(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,  # noqa: F811
    mock_update_post,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    result = await client.put(
        f"{posts_url}/{mock_post_inserted.id}",
        headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        json={"title": 1234},
    )

    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result.json()["detail"][0]["msg"] == "Input should be a valid string"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_404_post_not_found(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,  # noqa: F811
    mock_update_post,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository,
        "get_post_by_id",
        AsyncMock(return_value=None),
    ) as mock_post:
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        mock_post.assert_awaited_once_with(mock_post_inserted.id)

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Post not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_401_current_user_not_own_post(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,  # noqa: F811
    mock_update_post,
):
    mock_post_inserted.author_id = "5f7d0e49-e4ff-45d2-bfa8-0a6f41351745"

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository,
        "get_post_by_id",
        AsyncMock(return_value=mock_post_inserted),
    ) as mock_post:
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        mock_post.assert_awaited_once_with(mock_post_inserted.id)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {
            "detail": f"{mock_post_inserted.id} not belongs current user"
        }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_500_database_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,
    mock_update_post,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository,
        "get_post_by_id",
        AsyncMock(side_effect=DatabaseError),
    ) as mock_post:
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        mock_post.assert_awaited_once_with(mock_post_inserted.id)

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_500_unable_update_entity_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,
    mock_update_post,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository,
        "get_post_by_id",
        AsyncMock(side_effect=UnableUpdateEntity),
    ) as mock_post:
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        mock_post.assert_awaited_once_with(mock_post_inserted.id)

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Update Entity"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_post_raise_500_generic_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_user_out_inserted: UserOut,
    mock_user,
    mock_post_inserted,
    mock_update_post,
):
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.object(
        PostsRepository,
        "get_post_by_id",
        AsyncMock(side_effect=GenericError),
    ) as mock_post:
        result = await client.put(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
            json=mock_update_post,
        )

        mock_post.assert_awaited_once_with(mock_post_inserted.id)

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_post_success(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        delete_post=AsyncMock(return_value=None),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.text == ""


@pytest.mark.asyncio
async def test_delete_post_raise_404_post_not_found(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=None),
        delete_post=AsyncMock(return_value=None),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Post not found"}


@pytest.mark.asyncio
async def test_delete_post_raise_401_current_user_not_own_post(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = UUID("c1ac05e4-0e85-454b-9dc4-7d4171642540")

    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        delete_post=AsyncMock(return_value=None),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {
            "detail": f"{mock_post_inserted.id} not belongs current user"
        }


@pytest.mark.asyncio
async def test_delete_post_raise_500_database_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        delete_post=AsyncMock(side_effect=DatabaseError),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Database integrity error"}


@pytest.mark.asyncio
async def test_delete_post_raise_500_unable_delete_entity_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        delete_post=AsyncMock(side_effect=UnableDeleteEntity),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Unable Delete Entity"}


@pytest.mark.asyncio
async def test_delete_post_raise_500_generic_error(
    client: AsyncClient,
    posts_url: str,
    user_agent: str,
    mock_post_inserted: PostOut,
    mock_user,
    mock_user_out_inserted,
):
    mock_post_inserted.author_id = mock_user_out_inserted.id
    jwt = gen_jwt(360, mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user_out_inserted

    with patch.multiple(
        PostsRepository,
        get_post_by_id=AsyncMock(return_value=mock_post_inserted),
        delete_post=AsyncMock(side_effect=GenericError),
    ):
        result = await client.delete(
            f"{posts_url}/{mock_post_inserted.id}",
            headers={"Authorization": f"Bearer {jwt}", "User-Agent": user_agent},
        )

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Generic Error"}
