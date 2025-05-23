from unittest.mock import AsyncMock
import pytest
from blog_api.contrib.errors import CacheError, GenericError
from blog_api.core.cache import Cache
from blog_api.utils.encoding import encode_pydantic_model
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    DataError,
)
from blog_api.schemas.users import UserOut


@pytest.mark.asyncio
async def test_add_cache_one_model_return_success(mock_session, mock_user_out_inserted):
    mock_session.set = AsyncMock(return_value=None)

    cache = Cache(mock_session)

    await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_cache_many_models_return_success(
    mock_session, mock_users_out_inserted
):
    mock_session.set = AsyncMock(return_value=None)

    cache = Cache(mock_session)

    await cache.add("user:all", mock_users_out_inserted)

    mock_session.set.assert_awaited_once_with(
        "user:all",
        encode_pydantic_model(mock_users_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_cache_connection_error_return_cache_error(
    mock_session, mock_user_out_inserted
):
    mock_session.set = AsyncMock(side_effect=ConnectionError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="ConnectionError"):
        await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_cache_timeout_error_return_cache_error(
    mock_session, mock_user_out_inserted
):
    mock_session.set = AsyncMock(side_effect=TimeoutError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="TimeoutError"):
        await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_cache_authentication_error_return_cache_error(
    mock_session, mock_user_out_inserted
):
    mock_session.set = AsyncMock(side_effect=AuthenticationError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="AuthenticationError"):
        await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_data_error_return_cache_error(mock_session, mock_user_out_inserted):
    mock_session.set = AsyncMock(side_effect=DataError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="DataError"):
        await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_add_non_mapped_exception_return_generic_error(
    mock_session, mock_user_out_inserted
):
    mock_session.set = AsyncMock(side_effect=Exception)

    cache = Cache(mock_session)

    with pytest.raises(GenericError, match="Exception"):
        await cache.add(f"user:{mock_user_out_inserted.id}", mock_user_out_inserted)

    mock_session.set.assert_called_once_with(
        f"user:{mock_user_out_inserted.id}",
        encode_pydantic_model(mock_user_out_inserted),
        ex=360,
    )


@pytest.mark.asyncio
async def test_get_one_model_success(mock_session, mock_user_out_inserted):
    mock_session.get = AsyncMock(
        return_value=encode_pydantic_model(mock_user_out_inserted)
    )

    cache = Cache(mock_session)

    result = await cache.get(f"user:{mock_user_out_inserted.id}", UserOut)

    mock_session.get.assert_called_once_with(f"user:{mock_user_out_inserted.id}")

    assert result == mock_user_out_inserted


@pytest.mark.asyncio
async def test_get_many_models_success(mock_session, mock_users_out_inserted):
    mock_session.get = AsyncMock(
        return_value=encode_pydantic_model(mock_users_out_inserted)
    )

    cache = Cache(mock_session)

    result = await cache.get("user:all", UserOut)

    mock_session.get.assert_called_once_with("user:all")

    assert result == mock_users_out_inserted


@pytest.mark.asyncio
async def test_get_one_model_return_none(mock_session, mock_users_out_inserted):
    mock_session.get = AsyncMock(return_value=None)

    cache = Cache(mock_session)

    result = await cache.get("user:9345098b-99a3-4494-862d-9cf77d25fe7d", UserOut)

    mock_session.get.assert_called_once_with(
        "user:9345098b-99a3-4494-862d-9cf77d25fe7d"
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_connection_error_return_cache_error(mock_session, user_id):
    mock_session.get = AsyncMock(side_effect=ConnectionError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="ConnectionError"):
        await cache.get(f"user:{user_id}", UserOut)

    mock_session.get.assert_called_once_with(
        f"user:{user_id}",
    )


@pytest.mark.asyncio
async def test_get_timeout_error_return_cache_error(mock_session, user_id):
    mock_session.get = AsyncMock(side_effect=TimeoutError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="TimeoutError"):
        await cache.get(f"user:{user_id}", UserOut)

    mock_session.get.assert_called_once_with(
        f"user:{user_id}",
    )


@pytest.mark.asyncio
async def test_get_authentication_error_return_cache_error(mock_session, user_id):
    mock_session.get = AsyncMock(side_effect=AuthenticationError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="AuthenticationError"):
        await cache.get(f"user:{user_id}", UserOut)

    mock_session.get.assert_called_once_with(
        f"user:{user_id}",
    )


@pytest.mark.asyncio
async def test_get_data_error_return_cache_error(mock_session, user_id):
    mock_session.get = AsyncMock(side_effect=DataError)

    cache = Cache(mock_session)

    with pytest.raises(CacheError, match="DataError"):
        await cache.get(f"user:{user_id}", UserOut)

    mock_session.get.assert_called_once_with(
        f"user:{user_id}",
    )


@pytest.mark.asyncio
async def test_get_non_mapped_exception_return_generic_error(mock_session, user_id):
    mock_session.get = AsyncMock(side_effect=Exception)

    cache = Cache(mock_session)

    with pytest.raises(GenericError, match="Exception"):
        await cache.get(f"user:{user_id}", UserOut)

    mock_session.get.assert_called_once_with(
        f"user:{user_id}",
    )
