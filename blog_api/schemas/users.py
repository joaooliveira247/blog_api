from pydantic import BaseModel, Field, EmailStr, field_validator
import re

from blog_api.contrib.schemas import OutMixin


class BaseUser(BaseModel):
    username: str = Field(..., description="Username", min_length=3, max_length=255)
    email: EmailStr = Field(..., description="User Email", min_length=5, max_length=255)


class UserIn(BaseUser):
    password: str = Field(
        ..., description="User Password", min_length=8, max_length=128
    )

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", value
        ):
            raise ValueError("Invalid password format")
        return value


class UserOut(BaseUser, OutMixin):
    role: str = Field(..., description="User Role")
