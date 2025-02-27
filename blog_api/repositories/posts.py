from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.contrib.repositories import BaseRepository
from blog_api.repositories.users import UsersRepository


class PostsRepository(BaseRepository):
    def __init__(self, db: AsyncSession, user_repository: UsersRepository):
        super().__init__(db)
        self.user_repository = user_repository
