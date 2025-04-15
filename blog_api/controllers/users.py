from fastapi import APIRouter, status, Body, HTTPException
from blog_api.dependencies.dependencies import DatabaseDependency
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
from blog_api.schemas.users import UserIn
from blog_api.schemas.response import UserCreatedSchema
from blog_api.contrib.errors import UnableCreateEntity, DatabaseError, GenericError


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
