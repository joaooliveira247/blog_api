from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_pagination import Page, paginate
from pydantic import EmailStr

from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    NoResultFound,
    UnableDeleteEntity,
    UnableUpdateEntity,
)
from blog_api.core.cache import Cache
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import (
    CacheDependency,
    DatabaseDependency,
)
from blog_api.models.users import UserModel
from blog_api.repositories.comments import CommentsRepository
from blog_api.repositories.posts import PostsRepository
from blog_api.repositories.users import UsersRepository
from blog_api.schemas.posts import PostUpdate
from blog_api.schemas.response import UpdateSuccess
from blog_api.schemas.users import RoleUpdate, UserOut

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    repository = UsersRepository(db)

    cache = Cache(cache_conn)

    try:
        if email:
            if cache_user := await cache.get(f"user:{email}", UserOut):
                return paginate([cache_user])

            db_user = await repository.get_user_by_query(
                UserModel(email=email)
            )

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


@admin_controller.get("/users/{user_id}")
async def get_user_by_id(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
    user_id: UUID,
    user: UserOut = Depends(get_current_user),
) -> UserOut:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    repository = UsersRepository(db)

    cache = Cache(cache_conn)

    try:
        cache_user = await cache.get(f"user:{user_id}", UserOut)

        if cache_user is not None and isinstance(cache_user, UserOut):
            return cache_user

        db_user = await repository.get_user_by_id(user_id)

        db_user = UserOut(**db_user.__dict__)

        await cache.add(f"user:{db_user.id}", db_user)

        return db_user

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


@admin_controller.patch(
    "/users/{user_id}/role", status_code=status.HTTP_200_OK
)
async def update_user_role(
    db: DatabaseDependency,  # type:ignore
    user_id: UUID,
    data: RoleUpdate,
    user: UserOut = Depends(get_current_user),
) -> UpdateSuccess:
    if user.role not in ("admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    if user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not allowed to change your own role",
        )

    repository = UsersRepository(db)

    try:
        await repository.update_user_role(user_id, data.role)

        return UpdateSuccess(message="User role updated successfully")

    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
    except (DatabaseError, UnableUpdateEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@admin_controller.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db: DatabaseDependency,  # type:ignore
    user_id: UUID,
    user: UserOut = Depends(get_current_user),
) -> None:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    repository = UsersRepository(db)

    try:
        await repository.delete_user(user_id)
    except (DatabaseError, UnableDeleteEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@admin_controller.put(
    "/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_post(
    db: DatabaseDependency,  # type: ignore
    post_id: UUID,
    user: UserOut = Depends(get_current_user),
    body: PostUpdate = Body(...),
) -> None:
    if user.role not in ("admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    repository = PostsRepository(db)

    try:
        post = await repository.get_post_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        await repository.update_post(post_id, body.model_dump())

    except (DatabaseError, UnableUpdateEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@admin_controller.delete(
    "/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(
    db: DatabaseDependency,  # type: ignore
    post_id: UUID,
    user: UserOut = Depends(get_current_user),
) -> None:
    if user.role not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    repository = PostsRepository(db)

    try:
        post = await repository.get_post_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        await repository.delete_post(post_id)

    except (DatabaseError, UnableDeleteEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@admin_controller.delete(
    "/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    db: DatabaseDependency,  # type: ignore
    comment_id: UUID,
    user: UserOut = Depends(get_current_user),
) -> None:
    if user.role not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    post_repository = PostsRepository(db)
    comment_repository = CommentsRepository(db, post_repository)

    comment = await comment_repository.get_comment_by_id(comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )

    try:
        await comment_repository.delete_comment(comment_id)
    except (DatabaseError, UnableDeleteEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@admin_controller.get(
    "/docs", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def get_swagger_ui(
    user: UserOut = Depends(get_current_user),
) -> HTMLResponse:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    return get_swagger_ui_html(
        openapi_url="/admin/openapi.json", title="Admin Docs"
    )


@admin_controller.get(
    "/openapi.json", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def get_open_api_endpoint(
    user: UserOut = Depends(get_current_user),
) -> HTMLResponse:
    if user.role not in ("admin", "dev"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid permissions",
        )

    from blog_api.commands.app import app

    return JSONResponse(
        get_openapi(title=app.title, version=app.version, routes=app.routes)
    )
