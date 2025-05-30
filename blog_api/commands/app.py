from fastapi import FastAPI
from fastapi_pagination import add_pagination

from blog_api.commands.database import database_init_lifespan
from blog_api.core.config import get_settings
from blog_api.middlewares.user_agent import UserAgentMiddleware
from blog_api.urls import api_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=database_init_lifespan,
)
app.add_middleware(UserAgentMiddleware)
app.include_router(api_router)
add_pagination(app)
