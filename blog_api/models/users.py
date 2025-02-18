from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, TEXT
from blog_api.models.base import BaseModel


class UserModel(BaseModel):
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(TEXT, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="user")
