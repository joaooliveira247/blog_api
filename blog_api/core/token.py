from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, ExpiredSignatureError, exceptions
from blog_api.contrib.errors import GenericError, TokenError
from blog_api.models.users import UserModel
from blog_api.core.config import get_settings

settings = get_settings()


def gen_jwt(life_time: float, user: UserModel) -> str:
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=life_time),
        "iat": datetime.now(timezone.utc),
        "role": user.role,
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def verify_jwt(token: str) -> dict[str, Any] | None:
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        return decoded
    except ExpiredSignatureError as e:
        raise TokenError(e)
    except exceptions.JWTError as e:
        raise TokenError(e)
    except Exception as e:
        raise GenericError(e)
