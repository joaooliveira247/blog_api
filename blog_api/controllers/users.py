from fastapi import APIRouter, Depends, status, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from blog_api.core.auth import authenticate
from blog_api.core.config import get_settings
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import DatabaseDependency
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
from blog_api.schemas.users import UserIn, UserOut
from blog_api.schemas.response import TokenResponse, UserCreatedSchema
from blog_api.contrib.errors import (
    InvalidResource,
    TokenError,
    UnableCreateEntity,
    DatabaseError,
    GenericError,
)


settings = get_settings()

users_controller = APIRouter(tags=["account"])


@users_controller.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: DatabaseDependency,  # type: ignore
    body: UserIn = Body(...),  # type: ignore
) -> UserCreatedSchema:
    repository: UsersRepository = UsersRepository(db)

    user = UserModel(**body.model_dump())

    try:
        user_id = await repository.create_user(user)
        return UserCreatedSchema(id=user_id)
    except DatabaseError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.message
        )
    except UnableCreateEntity as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.message)
    except GenericError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_controller.post("/sign-in", status_code=status.HTTP_200_OK)
async def login(
    db: DatabaseDependency,  # type: ignore
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    try:
        user = await authenticate(db, form_data.username, form_data.password)

        jwt = gen_jwt(settings.JWT_DEFAULT_LIFE_TIME, user)

        return TokenResponse(access_token=jwt)
    except (DatabaseError, TokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except InvalidResource as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@users_controller.get("/", status_code=status.HTTP_200_OK)
async def get_logged_user(user: UserOut = Depends(get_current_user)) -> UserOut:
    return user
