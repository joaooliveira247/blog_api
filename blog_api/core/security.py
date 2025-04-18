from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from blog_api.core.config import get_settings

settings = get_settings()

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH}/account/sign-in")


def gen_hash(passwd: str) -> str:
    if not isinstance(passwd, str):
        raise ValueError("password must be a string")
    return pwd_context.hash(passwd)


def check_password(passwd: str, hash_passwd: str) -> bool:
    try:
        return pwd_context.verify(passwd, hash_passwd)
    except UnknownHashError:
        return False
    except Exception:
        return False
