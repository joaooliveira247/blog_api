from uuid import UUID
from pydantic import BaseModel, Field
from blog_api.contrib.schemas import OutMixin


class PostBase(BaseModel):
    title: str = Field(..., description="Post title")
    categories: list[str] = Field(..., description="Post categories")
    content: str = Field(..., description="Post content")


class PostOut(PostBase, OutMixin):
    author_id: UUID = Field(..., description="Post author id")
    author_username: str = Field(..., description="Post author username")


class PostIn(PostBase): ...


class PostUpdate(BaseModel):
    title: str | None = Field(None, description="Post title")
    categories: list[str] | None = Field(None, description="Post categories")
    content: str | None = Field(None, description="Post content")
