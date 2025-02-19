from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, TEXT
from blog_api.contrib import BaseModel


class UserModel(BaseModel):
    __tablename__: str = "users"

    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="user")
