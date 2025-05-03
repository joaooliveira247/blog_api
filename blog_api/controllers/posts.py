from fastapi import APIRouter, Body, Depends, HTTPException, status

from blog_api.contrib.errors import DatabaseError, GenericError, UnableCreateEntity
from blog_api.dependencies.auth import get_current_user
from blog_api.dependencies.dependencies import DatabaseDependency
from blog_api.models.posts import PostModel
from blog_api.repositories.posts import PostsRepository
from blog_api.schemas.posts import PostIn
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
