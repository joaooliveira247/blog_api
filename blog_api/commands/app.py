from fastapi import FastAPI
from blog_api.core.config import settings
from blog_api.urls import api_router

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router)
