from typing import Any
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from blog_api.core.config import get_settings
from blog_api.core.token import verify_jwt
from blog_api.dependencies.dependencies import DatabaseDependency, TokenDependency
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.users import UserOut
from blog_api.contrib.errors import TokenError, GenericError


settings = get_settings()

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH}/account/sign-in")


async def get_current_user(
    db: DatabaseDependency,  # type: ignore
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

        user_repository = UsersRepository(db)
        user = await user_repository.get_user_by_id(user_id)

        return UserOut(**user.__dict__)

    except TokenError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
    except GenericError as e:
        credencial_exception.detail = e.message
        raise credencial_exception
