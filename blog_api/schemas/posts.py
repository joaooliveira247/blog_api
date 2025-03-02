from pydantic import BaseModel, Field
from blog_api.contrib.schemas import OutMixin


class PostBase(BaseModel):
    title: str = Field(..., description="Post title")
    categories: list[str] = Field(..., description="Post categories")
    content: str = Field(..., description="Post content")


class PostOut(PostBase, OutMixin):
    author: str = Field(..., description="Post author username")
