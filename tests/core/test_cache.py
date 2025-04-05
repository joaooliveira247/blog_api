from unittest.mock import AsyncMock
import pytest
from blog_api.core.cache import Cache
from blog_api.utils.encoding import encode_pydantic_model


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
