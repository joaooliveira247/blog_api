from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from blog_api.contrib.errors import (
    DatabaseError,
    GenericError,
    InvalidResource,
    TokenError,
    UnableCreateEntity,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from blog_api.core.auth import authenticate
from blog_api.core.config import get_settings
from blog_api.core.security import check_password, gen_hash
from blog_api.core.token import gen_jwt
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import DatabaseDependency
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.response import TokenResponse, UserCreatedSchema
from blog_api.schemas.users import PasswordUpdate, UserIn, UserOut

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
        user_password = gen_hash(user.password)
        user.password = user_password
        user_id = await repository.create_user(user)
        return UserCreatedSchema(id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except DatabaseError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err.message,
        )
    except UnableCreateEntity as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.message
        )
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@users_controller.get("/", status_code=status.HTTP_200_OK)
async def get_logged_user(
    user: UserOut = Depends(get_current_user),
) -> UserOut:
    return user


@users_controller.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    db: DatabaseDependency,  # type: ignore
    form: PasswordUpdate,  # type: ignore
    user: UserOut = Depends(get_current_user),
) -> None:
    repository: UsersRepository = UsersRepository(db)

    try:
        user_db = await repository.get_user_by_id(user.id)

        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if check_password(form.password, user_db.password):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New password cannot be the same as current password",
            )

        await repository.update_user_password(user.id, form.password)

        return None

    except (DatabaseError, UnableUpdateEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@users_controller.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: DatabaseDependency,  # type: ignore
    user: UserOut = Depends(get_current_user),
) -> None:
    repository: UsersRepository = UsersRepository(db)

    try:
        await repository.delete_user(user.id)

        return None

    except (DatabaseError, UnableDeleteEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
