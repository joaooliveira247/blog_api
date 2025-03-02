from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(..., description="Post title")
    categories: list[str] = Field(..., description="Post categories")
    content: str = Field(..., description="Post content")
