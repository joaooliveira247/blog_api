from uuid import UUID

from pydantic import BaseModel, Field

from blog_api.contrib.schemas import OutMixin


class CommentBase(BaseModel):
    content: str = Field(..., description="Comment content")


class CommentOut(CommentBase, OutMixin):
    post_id: UUID = Field(..., description="Post id")
    post_title: str = Field(..., description="Title post")
    author_id: UUID = Field(..., description="Comment author id")
    author_username: str = Field(..., description="Comment author username")


class CommentIn(CommentBase):
    post_id: UUID = Field(..., description="Post id")


class CommentUpdate(CommentBase): ...
