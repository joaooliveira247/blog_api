from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi_pagination import Page, paginate
from pydantic import EmailStr

from blog_api.core.cache import Cache
from blog_api.models.users import UserModel
from blog_api.repositories.users import UsersRepository
from blog_api.dependencies.dependencies import CacheDependency, DatabaseDependency
from blog_api.dependencies.auth import get_current_user
from blog_api.schemas.users import UserOut
from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
)


admin_controller = APIRouter(tags=["admin"])


@admin_controller.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
    user: UserOut = Depends(get_current_user),
    email: EmailStr = Query(None),
) -> Page[UserOut]:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid permissions"
        )

    repository = UsersRepository(db)

    cache = Cache(cache_conn)

    try:
        if email:
            if cache_user := await cache.get(f"user:{email}", UserOut):
                return paginate([cache_user])

            db_user = await repository.get_user_by_query(UserModel(email=email))

            return paginate([UserOut(**db_user.__dict__)])

        users = await cache.get("user:all", UserOut)

        if users is not None:
            return paginate(users)

        users = await repository.get_users()

        users = [UserOut(**user.__dict__) for user in users]

        await cache.add("user:all", users)

        return paginate(users)

    except (CacheError, EncodingError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
