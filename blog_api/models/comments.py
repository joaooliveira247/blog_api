from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from blog_api.contrib.models import BaseModel
from blog_api.models.users import UserModel
from blog_api.models.posts import PostModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TEXT


class CommentModel(BaseModel):
    __tablename__: str = "comments"

    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    post_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False
    )

    user: Mapped[UserModel] = relationship(UserModel, lazy="selectin")
    post: Mapped[PostModel] = relationship(PostModel, lazy="selectin")
