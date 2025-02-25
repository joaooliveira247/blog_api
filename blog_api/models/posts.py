from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, TEXT, ARRAY
from blog_api.contrib import BaseModel
from blog_api.models.users import UserModel


class PostModel(BaseModel):
    __tablename__: str = "posts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String(30)))
    content: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user: Mapped[UserModel] = relationship(UserModel, lazy="selectin")
