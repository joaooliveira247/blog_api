from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import select
from blog_api.models.users import UserModel
from blog_api.contrib.errors import (
    DatabaseError,
    UnableCreateEntity,
    GenericError,
    UnableUpdateEntity,
    NoResultFound,
)


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_user(self, user: UserModel):
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
        finally:
            await self.db.close()

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

    async def get_user_by_id(self, id: UUID) -> UserModel | None:
        async with self.db as session:
            try:
                result = await session.execute(
                    select(UserModel).filter(UserModel.id == id)
                )

                user = result.scalars().one_or_none()
                return user

            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

    async def get_user_by_query(self, query: UserModel) -> UserModel | None:
        async with self.db as session:
            statement = select(UserModel)

            if query.email:
                statement.filter(UserModel.email == query.email)
            if query.username:
                statement.filter(UserModel.username == query.username)

            try:
                result = await session.execute(statement)
            except OperationalError:
                raise DatabaseError
            except Exception:
                raise GenericError

            user = result.scalars().one_or_none()
            return user

    async def update_user_password(self, user_id: UUID, new_password: str) -> None:
        with self.db as session:
            try:
                result = await session.execute(
                    select(UserModel).filter(UserModel.id == user_id)
                )

                if update_user := result.scalars().one_or_none():
                    update_user.password = new_password

                    await self.db.flush()
                    await self.db.commit()
                    return

                session.rollback()
                raise NoResultFound

            except OperationalError:
                await self.db.rollback()
                raise DatabaseError
            except IntegrityError:
                await self.db.rollback()
                raise UnableUpdateEntity
            except Exception:
                await self.db.rollback()
                raise GenericError

    async def update_user_role(self, user_id, role: str) -> None:
        with self.db as session:
            try:
                result = await session.execute(
                    select(UserModel).filter(UserModel.id == user_id)
                )

                if update_user := result.scalars().one_or_none():
                    update_user.role = role

                    await session.flush()
                    await session.commit()
                    return

                session.rollback()
                raise NoResultFound

            except OperationalError:
                await session.rollback()
                raise DatabaseError
            except IntegrityError:
                await session.rollback()
                raise UnableUpdateEntity
            except Exception:
                await session.rollback()
                raise GenericError

    async def delete_user(self, user_id) -> None:
        with self.db as session:
            try:
                result = await session.execute(
                    select(UserModel).filter(UserModel.id == user_id)
                )

                if delete_user := result.scalars().one_or_none():
                    await session.delete(delete_user)
                    await session.commit()
                    return

                session.rollback()
                raise NoResultFound

            except OperationalError:
                await session.rollback()
                raise DatabaseError
            except IntegrityError:
                await session.rollback()
                raise UnableUpdateEntity
            except Exception:
                await session.rollback()
                raise GenericError
