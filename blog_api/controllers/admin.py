from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_pagination import Page, paginate

from blog_api.repositories.users import UsersRepository
from blog_api.dependencies.dependencies import DatabaseDependency
from blog_api.dependencies.auth import get_current_user
from blog_api.schemas.users import UserOut
from blog_api.contrib.errors import DatabaseError, GenericError


admin_controller = APIRouter(tags=["admin"])


@admin_controller.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    db: DatabaseDependency,  # type: ignore
    user: UserOut = Depends(get_current_user),
) -> Page[UserOut]:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid permissions"
        )

    repository = UsersRepository(db)

    try:
        users = await repository.get_users()

        print(users)

        users = [UserOut(**user.__dict__) for user in users]

        return paginate(users)

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
