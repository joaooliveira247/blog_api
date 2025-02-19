from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from blog_api.models.users import UserModel
from blog_api.contrib import DatabaseError, UnableCreateEntity


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create(self, user: UserModel):
        try:
            self.db.add(user)
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
            raise
