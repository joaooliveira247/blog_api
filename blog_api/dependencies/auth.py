from fastapi.security import OAuth2PasswordBearer
from blog_api.core.config import get_settings


settings = get_settings()

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH}/account/sign-in")
