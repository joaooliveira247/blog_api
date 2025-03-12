from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str = Field(..., description="Comment content")
