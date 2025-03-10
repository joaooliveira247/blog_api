from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.posts import PostsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.repositories.users import UsersRepository


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
