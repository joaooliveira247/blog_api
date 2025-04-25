import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_user_agent_success(client: AsyncClient):
    result = await client.get(
        "/",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36}"
        },
    )

    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert result.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_user_agent_empty_return_400_bad_request(client: AsyncClient):
    result = await client.get(
        "/",
        headers={"User-Agent": ""},
    )

    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert result.json() == {"detail": "User-Agent empty"}


@pytest.mark.asyncio
async def test_user_agent_blocked_return_403_forbidden(client: AsyncClient):
    result = await client.get("/")

    assert result.status_code == status.HTTP_403_FORBIDDEN
    assert result.json() == {"detail": "User-Agent blocked"}
