from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from blog_api.contrib.errors import (
    CacheError,
    DatabaseError,
    EncodingError,
    GenericError,
    NoResultFound,
    UnableCreateEntity,
)
from blog_api.core.cache import Cache
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import (
    CacheDependency,
    DatabaseDependency,
)
from blog_api.models.comments import CommentModel
from blog_api.repositories.comments import CommentsRepository
from blog_api.repositories.posts import PostsRepository
from blog_api.schemas.comments import CommentIn, CommentOut
from blog_api.schemas.response import CommentCreatedSchema
from blog_api.schemas.users import UserOut

comments_controller = APIRouter(tags=["comments"])


@comments_controller.post("/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    db: DatabaseDependency,  # type: ignore
    user: UserOut = Depends(get_current_user),
    body: CommentIn = Body(...),
) -> CommentCreatedSchema:
    post_repository = PostsRepository(db)
    comment_repository = CommentsRepository(db, post_repository)

    try:
        model = CommentModel(**body.model_dump(), user_id=user.id)
        comment_id = await comment_repository.create_comment(model)

        return CommentCreatedSchema(id=comment_id)
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
    except (DatabaseError, UnableCreateEntity) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )
    except GenericError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@comments_controller.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def get_comments_by_post_id(
    db: DatabaseDependency,  # type: ignore
    cache_conn: CacheDependency,  # type: ignore
    post_id: UUID,
) -> Page[CommentOut]:
    post_repository = PostsRepository(db)
    comment_repository = CommentsRepository(db, post_repository)
    cache = Cache(cache_conn)

    try:
        if comments := await cache.get(f"comment:{post_id}", CommentOut):
            return paginate(comments)

        comments = await comment_repository.get_comments_by_post_id(
            post_id=post_id
        )

        await cache.add(f"comment:{post_id}", comments)

        return paginate(comments)
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
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
