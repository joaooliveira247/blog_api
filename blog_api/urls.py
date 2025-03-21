from fastapi import APIRouter
from blog_api.controllers.users import users_controller

api_router = APIRouter()
api_router.include_router(users_controller, prefix="/users")
