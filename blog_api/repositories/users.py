import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import select
from blog_api.models.users import UserModel
from blog_api.contrib import DatabaseError, UnableCreateEntity, GenericError


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
            raise GenericError

    async def get_users(self) -> list[UserModel]:
        async with self.db as session:
            try:
                result = await session.execute(select(UserModel))
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            users = result.scalars().all()
            return list(users)

    async def get_user_by_id(self, id: uuid.UUID) -> UserModel | None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(UserModel).filter(UserModel.id == id)
                )
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            user = result.scalars().one_or_none()
            return user
