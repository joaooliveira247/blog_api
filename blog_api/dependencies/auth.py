from typing import Any, cast
from fastapi import HTTPException, status
from blog_api.core.cache import Cache
from blog_api.core.token import verify_jwt
from blog_api.dependencies.dependencies import (
    CacheDependency,
    DatabaseDependency,
    TokenDependency,
)
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.users import UserOut
from blog_api.contrib.errors import CacheError, EncodingError, TokenError, GenericError


async def get_current_user(
    db: DatabaseDependency,  # type: ignore
    cache: CacheDependency,  # type: ignore
    token: TokenDependency,  # type: ignore
) -> UserOut:
    credencial_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload: dict[str, Any] | None = verify_jwt(token)

        if payload is None or (user_id := payload["sub"]) is None:
            credencial_exception.detail = "User can't be authenticated"
            raise credencial_exception

        cache_service = Cache(cache_conn=cache)

        user_cache = await cache_service.get(f"user:{user_id}", UserOut)

        if user_cache is not None:
            return cast(UserOut, user_cache)

        user_repository = UsersRepository(db)
        user = await user_repository.get_user_by_id(user_id)

        if user is None:
            credencial_exception.detail = "User can't be authenticated"
            raise credencial_exception

        user_out = UserOut(**user.__dict__)

        await cache_service.add(f"user:{user_id}", user_out)

        return user_out

    except TokenError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
    except CacheError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
    except EncodingError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
    except GenericError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
