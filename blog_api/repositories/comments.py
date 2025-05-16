from uuid import UUID
from blog_api.contrib.errors import NoResultFound, NothingToUpdate
from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.posts import PostsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from blog_api.models.comments import CommentModel
from blog_api.models.users import UserModel
from blog_api.models.posts import PostModel
from blog_api.contrib.errors import (
    DatabaseError,
    GenericError,
    UnableCreateEntity,
    UnableDeleteEntity,
)
from blog_api.schemas.comments import CommentOut
from blog_api.schemas.posts import PostOut


class CommentsRepository(BaseRepository):
    def __init__(
        self,
        db: AsyncSession,
        post_repository: PostsRepository,
    ):
        super().__init__(db)
        self.post_repository = post_repository

    async def create_comment(self, comment: CommentModel) -> None:
        post: PostOut | None = await self.post_repository.get_post_by_id(
            comment.post_id
        )

        if not post:
            raise NoResultFound("post_id")

        try:
            self.db.add(comment)
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

    async def get_comments(self) -> list[CommentOut]:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(CommentModel).options(
                        joinedload(CommentModel.post), joinedload(CommentModel.user)
                    )
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            comments: list[CommentModel] = result.scalars().all()
            return [
                CommentOut(
                    id=comment.id,
                    content=comment.content,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    post_title=comment.post.title,
                    author=comment.user.username,
                )
                for comment in comments
            ]

    async def get_comment_by_id(self, id: UUID) -> CommentOut | None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(CommentModel)
                    .options(
                        joinedload(CommentModel.post), joinedload(CommentModel.user)
                    )
                    .filter(CommentModel.id == id)
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            comment: CommentModel = result.scalars().one_or_none()

            if comment is None:
                return comment

            return CommentOut(
                id=comment.id,
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                post_title=comment.post.title,
                author=comment.user.username,
            )

    async def get_comments_by_user_id(self, user_id: UUID) -> list[CommentOut]:
        async with self.db as session:
            user: UserModel | None = await self.user_reposiotry.get_user_by_id(user_id)

            if user is None:
                raise NoResultFound("user_id")

            try:
                result = await session.execute(
                    select(CommentModel)
                    .options(
                        joinedload(CommentModel.post), joinedload(CommentModel.user)
                    )
                    .filter(CommentModel.user_id == user_id)
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            comments: list[CommentModel] = result.scalars().all()
            return [
                CommentOut(
                    id=comment.id,
                    content=comment.content,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    post_title=comment.post.title,
                    author=comment.user.username,
                )
                for comment in comments
            ]

    async def get_comments_by_post_id(self, post_id: UUID) -> list[CommentOut]:
        async with self.db as session:
            user: PostModel | None = await self.post_repository.get_post_by_id(post_id)

            if user is None:
                raise NoResultFound("post_id")

            try:
                result = await session.execute(
                    select(CommentModel)
                    .options(
                        joinedload(CommentModel.post), joinedload(CommentModel.user)
                    )
                    .filter(CommentModel.post_id == post_id)
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            comments: list[CommentModel] = result.scalars().all()
            return [
                CommentOut(
                    id=comment.id,
                    content=comment.content,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    post_title=comment.post.title,
                    author=comment.user.username,
                )
                for comment in comments
            ]

    async def update_comment(self, comment_id: UUID, content: str) -> None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(CommentModel).filter(CommentModel.id == comment_id)
                )

                if update_post := result.scalars().one_or_none():
                    if update_post.content == content:
                        raise NothingToUpdate
                    update_post.content = content

                    await session.flush()
                    await session.commit()
                    return
                raise NoResultFound("comment_id")
            except OperationalError:
                await self.db.rollback()
                raise DatabaseError
            except Exception:
                await self.db.rollback()
                raise GenericError

    async def delete_comment(self, comment_id: UUID) -> None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(CommentModel).filter(CommentModel.id == comment_id)
                )

                if delete_comment := result.scalars().one_or_none():
                    await session.delete(delete_comment)
                    await session.commit()
                    return
                raise NoResultFound("comment_id")
            except OperationalError:
                await session.rollback()
                raise DatabaseError
            except IntegrityError:
                await session.rollback()
                raise UnableDeleteEntity
            except Exception:
                await session.rollback()
                raise GenericError
