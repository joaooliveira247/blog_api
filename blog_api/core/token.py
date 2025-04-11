from datetime import datetime, timedelta
from typing import Any

import jwt
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
