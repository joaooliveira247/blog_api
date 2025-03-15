from pydantic import BaseModel, Field, EmailStr


class BaseUser(BaseModel):
    username: str = Field(..., description="Username", min_length=3, max_length=255)
    email: EmailStr = Field(..., description="User Email", min_length=5, max_length=255)
