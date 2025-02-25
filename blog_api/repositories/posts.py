from sqlalchemy.ext.asyncio import AsyncSession


class PostsRepository:
    def __init__(self, session: AsyncSession):
        self.db = session
