from datetime import datetime, timedelta
from typing import Any

import jwt
from blog_api.contrib.errors import GenericError, TokenError
from blog_api.models.users import UserModel
from blog_api.core.config import settings


def gen_jwt(life_time: float, user: UserModel) -> str:
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "exp": datetime.now() + timedelta(minutes=life_time),
        "iat": datetime.now(),
        "role": user.role,
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def verify_jwt(token: str) -> dict[str, Any] | None:
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        return decoded
    except jwt.ExpiredSignatureError as e:
        raise TokenError(e)
    except jwt.InvalidTokenError as e:
        raise TokenError(e)
    except Exception as e:
        raise GenericError(e)
