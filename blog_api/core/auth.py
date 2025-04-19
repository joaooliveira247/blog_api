from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.repositories.users import UsersRepository
from blog_api.models.users import UserModel
from blog_api.contrib.errors import InvalidResource
from blog_api.core.security import check_password


async def authenticate(
    db: AsyncSession,
    email: EmailStr,
    passwd: str,
) -> UserModel:
    user_repository = UsersRepository(db)

    user = await user_repository.get_user_by_query(UserModel(email=email))

    if not user:
        raise InvalidResource("email")

    if not check_password(passwd, user.password):
        raise InvalidResource("password")

    return user
