from sqlalchemy.ext.asyncio import AsyncSession


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.db = session
