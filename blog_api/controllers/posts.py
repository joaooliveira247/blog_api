from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    UnableCreateEntity,
    UnableUpdateEntity,
)
from blog_api.core.cache import Cache
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import CacheDependency, DatabaseDependency
from blog_api.models.posts import PostModel
from blog_api.repositories.posts import PostsRepository
from blog_api.schemas.posts import PostIn, PostOut, PostUpdate
from blog_api.schemas.response import PostCreatedSchema
from blog_api.schemas.users import UserOut


posts_controller = APIRouter(tags=["posts"])


@posts_controller.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    db: DatabaseDependency,  # type: ignore
    user: UserOut = Depends(get_current_user),
    body: PostIn = Body(...),
):
    repository = PostsRepository(db)

    post_model = PostModel(**body.model_dump(), user_id=user.id)

    try:
        post_id = await repository.create_post(post_model)

        return PostCreatedSchema(id=post_id)

    except (DatabaseError, UnableCreateEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@posts_controller.get("/", status_code=status.HTTP_200_OK)
async def get_posts(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
) -> Page[PostOut]:
    repository = PostsRepository(db)

    cache = Cache(cache_conn)

    try:
        if posts := await cache.get("post:all", PostOut):
            return paginate(posts)

        posts = await repository.get_posts()

        await cache.add("post:all", posts)

        return paginate(posts)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except (CacheError, EncodingError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@posts_controller.get("/{post_id}", status_code=status.HTTP_200_OK)
async def get_post_by_id(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
    post_id: UUID,
) -> PostOut:
    repository = PostsRepository(db)

    cache = Cache(cache_conn)

    try:
        post = await cache.get(f"post:{post_id}", PostOut)

        if isinstance(post, PostOut):
            return post

        post = await repository.get_post_by_id(post_id)

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found."
            )

        await cache.add(f"post:{post.id}", post)

        return post

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except (CacheError, EncodingError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@posts_controller.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_post_by_user_id(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
    user_id: UUID,
) -> Page[PostOut]:
    repository = PostsRepository(db)

    cache = Cache(cache_conn)

    try:
        if posts := await cache.get(f"posts:{user_id}", PostOut):
            return paginate(posts)

        posts = await repository.get_posts_by_user_id(user_id)

        await cache.add(f"posts:{user_id}", posts)

        return paginate(posts)

    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except (CacheError, EncodingError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@posts_controller.put("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(
    db: DatabaseDependency,  # type: ignore
    post_id: UUID,
    user: UserOut = Depends(get_current_user),
    body: PostUpdate = Body(...),
) -> None:
    repository = PostsRepository(db)

    try:
        post = await repository.get_post_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        if post.author_id is not user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{post_id} not belongs current user",
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
