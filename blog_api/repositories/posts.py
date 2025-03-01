from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.users import UsersRepository
from blog_api.models.posts import PostModel
from blog_api.models.users import UserModel
from blog_api.contrib.errors import (
    NoResultFound,
    DatabaseError,
    UnableCreateEntity,
    GenericError,
)
from sqlalchemy.exc import OperationalError, IntegrityError


class PostsRepository(BaseRepository):
    def __init__(self, db: AsyncSession, user_repository: UsersRepository):
        super().__init__(db)
        self.user_repository = user_repository

    async def create_post(self, post: PostModel) -> None:
        user: UserModel | None = await self.user_repository.get_user_by_id(post.user_id)

        if user is None:
            raise NoResultFound("user_id")

        try:
            self.db.add(post)
            await self.db.flush()
            await self.db.commit()

        except OperationalError:
            await self.db.rollback()
            raise DatabaseError
        except IntegrityError:
            await self.db.rollback()
            raise UnableCreateEntity
        except Exception:
            await self.db.rollback()
            raise GenericError
