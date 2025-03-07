from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.users import UsersRepository
from blog_api.models.posts import PostModel
from blog_api.models.users import UserModel
from blog_api.contrib.errors import (
    NoResultFound,
    DatabaseError,
    UnableCreateEntity,
    GenericError,
    UnableUpdateEntity,
)
from sqlalchemy.exc import OperationalError, IntegrityError
from blog_api.schemas.posts import PostOut


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

    async def get_posts(self) -> list[PostOut]:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(PostModel).options(joinedload(PostModel.user))
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            posts: list[PostModel] = result.scalars().all()
            return [
                PostOut(
                    id=post.id,
                    title=post.title,
                    categories=post.categories,
                    content=post.content,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    author=post.user.username,
                )
                for post in posts
            ]

    async def get_post_by_id(self, post_id: UUID) -> PostOut | None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(PostModel)
                    .filter(PostModel.id == post_id)
                    .options(joinedload(PostModel.user))
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            post: PostModel | None = result.scalars().one_or_none()

            if post is None:
                return None

            return PostOut(
                id=post.id,
                title=post.title,
                categories=post.categories,
                content=post.content,
                created_at=post.created_at,
                updated_at=post.updated_at,
                author=post.user.username,
            )

    async def get_posts_by_user_id(self, user_id: UUID) -> list[PostOut]:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(PostModel)
                    .options(joinedload(PostModel.user))
                    .filter(PostModel.user_id == user_id)
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            posts: list[PostModel] = result.scalars().all()

            return [
                PostOut(
                    id=post.id,
                    title=post.title,
                    categories=post.categories,
                    content=post.content,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    author=post.user.username,
                )
                for post in posts
            ]

    async def update_post(self, post_id: UUID, fields: dict) -> None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(PostModel).filter(PostModel.id == post_id)
                )

                if update_post := result.scalars().one_or_none():
                    for k, v in fields:
                        setattr(update_post, k, v)

                    await session.flush()
                    await session.commit()
                    return
                raise NoResultFound("post_id")
            except OperationalError:
                await self.db.rollback()
                raise DatabaseError
            except IntegrityError:
                await self.db.rollback()
                raise UnableUpdateEntity
            except Exception:
                await self.db.rollback()
                raise GenericError
