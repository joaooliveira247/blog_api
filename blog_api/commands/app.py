from fastapi import FastAPI
from fastapi_pagination import add_pagination
from blog_api.core.config import get_settings
from blog_api.urls import api_router
from blog_api.middlewares.user_agent import UserAgentMiddleware

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(UserAgentMiddleware)
app.include_router(api_router)
add_pagination(app)
