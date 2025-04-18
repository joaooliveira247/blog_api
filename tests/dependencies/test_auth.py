from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import pytest
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.users import UserOut


@pytest.mark.asyncio
async def test_get_current_user_success(mock_session, mock_user_out_inserted):
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
        result = await get_current_user(mock_session, token=jwt)

        assert isinstance(result, UserOut)
        assert result.id == mock_user_out_inserted.id
        assert result.email == mock_user_out_inserted.email

        mock_jwt.assert_called_once_with(jwt)
        mock_user.assert_called_once_with(str(mock_user_out_inserted.id))
