from fastapi import FastAPI
from blog_api.core.config import get_settings
from blog_api.urls import api_router

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router)
