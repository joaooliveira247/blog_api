from fastapi import FastAPI
from fastapi_pagination import add_pagination
from blog_api.core.config import get_settings
from blog_api.urls import api_router

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)
add_pagination(app)
app.include_router(api_router)
