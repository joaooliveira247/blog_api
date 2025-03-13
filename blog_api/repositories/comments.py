from blog_api.contrib.errors import NoResultFound
from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.posts import PostsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from blog_api.repositories.users import UsersRepository
from blog_api.models.comments import CommentModel
from blog_api.models.users import UserModel
from blog_api.models.posts import PostModel
from blog_api.contrib.errors import DatabaseError, GenericError, UnableCreateEntity
from blog_api.schemas.comments import CommentOut


class CommentsRepository(BaseRepository):
    def __init__(
        self,
        db: AsyncSession,
        post_repository: PostsRepository,
        user_repository: UsersRepository,
    ):
        super().__init__(db)
        self.post_repository = post_repository
        self.user_reposiotry = user_repository

    async def create_comment(self, comment: CommentModel) -> None:
        user: UserModel | None = await self.user_reposiotry.get_user_by_id(
            comment.user_id
        )

        if not user:
            raise NoResultFound("user_id")

        post: PostModel | None = await self.post_repository.get_post_by_id(
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
