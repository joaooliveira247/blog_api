from unittest.mock import AsyncMock, patch
import pytest

from blog_api.contrib.errors import InvalidResource
from blog_api.core.auth import authenticate
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository


@pytest.mark.asyncio
async def test_authenticate_success(
    mock_session, mock_user_inserted, mock_user_out_inserted, password
):
    user = UserModel(
        **mock_user_out_inserted.model_dump(), password=mock_user_inserted.password
    )
    with patch.object(
        UsersRepository,
        "get_user_by_query",
        new=AsyncMock(return_value=user),
    ) as mock_user:
        result = await authenticate(mock_session, mock_user_inserted.email, password)

        assert isinstance(result, UserModel)
        assert result.email == user.email

        mock_user.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_raise_invalid_email(
    mock_session, mock_user_inserted, password
):
    with patch.object(
        UsersRepository,
        "get_user_by_query",
        new=AsyncMock(return_value=None),
    ) as mock_user:
        with pytest.raises(InvalidResource, match="email invalid"):
            await authenticate(mock_user_inserted.email, password, mock_session)

        mock_user.assert_called_once()
