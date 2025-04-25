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
