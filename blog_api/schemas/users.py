import re
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from blog_api.contrib.schemas import OutMixin


class BaseUser(BaseModel):
    username: str = Field(
        ..., description="Username", min_length=3, max_length=255
    )
    email: EmailStr = Field(
        ..., description="User Email", min_length=5, max_length=255
    )


class PasswordMixin(BaseModel):
    password: str = Field(
        ..., description="User Password", min_length=8, max_length=128
    )

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        pattern = {
            "lower": r"[a-z]",
            "upper": r"[A-Z]",
            "digit": r"\d",
            "special": r"[@$!%*?&]",
        }

        components = {
            key: "".join(re.findall(regex, value)) or None
            for key, regex in pattern.items()
        }

        missing_components = [
            key for key, value in components.items() if value is None
        ]

        if missing_components:
            raise ValueError(
                f"Wrong password format! characters missing: {', '.join(missing_components)}"
            )

        return value


class UserIn(BaseUser, PasswordMixin): ...


class UserOut(BaseUser, OutMixin):
    role: str = Field(..., description="User Role")


class PasswordUpdate(PasswordMixin): ...


class RoleUpdate(BaseModel):
    role: Literal["user", "admin", "dev"]
