from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
import pytest
from blog_api.contrib.errors import CacheError, EncodingError
from blog_api.core.cache import Cache
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.users import UserOut


@pytest.mark.asyncio
async def test_get_current_user_success(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=360),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    with (
        patch(
            "blog_api.dependencies.auth.verify_jwt",
            return_value=payload,
        ) as mock_jwt,
        patch.object(
            UsersRepository,
            "get_user_by_id",
            new=AsyncMock(return_value=user),
        ) as mock_user,
    ):
        result = await get_current_user(mock_session, cache_session, token=jwt)

        assert isinstance(result, UserOut)
        assert result.id == mock_user_out_inserted.id
        assert result.email == mock_user_out_inserted.email

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(str(mock_user_out_inserted.id))


@pytest.mark.asyncio
async def test_get_current_user_success_from_cache(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=360),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    with (
        patch(
            "blog_api.dependencies.auth.verify_jwt",
            return_value=payload,
        ) as mock_jwt,
        patch.object(
            Cache,
            "get",
            new=AsyncMock(return_value=mock_user_out_inserted),
        ) as mock_user,
    ):
        result = await get_current_user(mock_session, cache_session, token=jwt)

        assert isinstance(result, UserOut)
        assert result.id == mock_user_out_inserted.id
        assert result.email == mock_user_out_inserted.email

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(
            str(f"user:{mock_user_out_inserted.id}"), UserOut
        )


@pytest.mark.asyncio
async def test_get_current_user_raise_cache_error(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=360),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    with (
        patch(
            "blog_api.dependencies.auth.verify_jwt",
            return_value=payload,
        ) as mock_jwt,
        patch.object(
            Cache,
            "get",
            new=AsyncMock(side_effect=CacheError("Cache Error")),
        ) as mock_user,
    ):
        with pytest.raises(HTTPException, match="401: Cache Error"):
            await get_current_user(mock_session, cache_session, token=jwt)

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(
            str(f"user:{mock_user_out_inserted.id}"), UserOut
        )


@pytest.mark.asyncio
async def test_get_current_user_raise_encoding_error(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=360),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    with (
        patch(
            "blog_api.dependencies.auth.verify_jwt",
            return_value=payload,
        ) as mock_jwt,
        patch.object(
            Cache,
            "get",
            new=AsyncMock(side_effect=EncodingError),
        ) as mock_user,
    ):
        with pytest.raises(
            HTTPException, match="401: Error when try encoding one object"
        ):
            await get_current_user(mock_session, cache_session, token=jwt)

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(
            str(f"user:{mock_user_out_inserted.id}"), UserOut
        )


@pytest.mark.asyncio
async def test_get_current_user_raise_http_exception_invalid_payload(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    with patch(
        "blog_api.dependencies.auth.verify_jwt",
        return_value=None,
    ) as mock_jwt:
        with pytest.raises(HTTPException, match="401: User can't be authenticated"):
            await get_current_user(mock_session, cache_session, token=jwt)
        mock_jwt.assert_called_once_with(jwt)


@pytest.mark.asyncio
async def test_get_current_user_raise_http_exception_user_not_exists(
    mock_session, cache_session, mock_user_out_inserted
):
    user = UserModel(**mock_user_out_inserted.model_dump())
    jwt = gen_jwt(360, user)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=360),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    with (
        patch(
            "blog_api.dependencies.auth.verify_jwt",
            return_value=payload,
        ) as mock_jwt,
        patch.object(
            UsersRepository,
            "get_user_by_id",
            new=AsyncMock(return_value=None),
        ) as mock_user,
    ):
        with pytest.raises(HTTPException, match="401: User can't be authenticated"):
            await get_current_user(mock_session, cache_session, token=jwt)

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(str(mock_user_out_inserted.id))
