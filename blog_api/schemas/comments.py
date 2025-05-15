from uuid import UUID
from pydantic import BaseModel, Field
from blog_api.contrib.schemas import OutMixin


class CommentBase(BaseModel):
    content: str = Field(..., description="Comment content")


class CommentOut(CommentBase, OutMixin):
    post_title: str = Field(..., description="Title post")
    author: str = Field(..., description="Comment author username")


class CommentIn(CommentBase):
    post_id: UUID = Field(..., description="Post id")
