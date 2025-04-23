from fastapi import APIRouter
from blog_api.controllers.users import users_controller
from blog_api.controllers.admin import admin_controller

api_router = APIRouter()
api_router.include_router(users_controller, prefix="/account")
api_router.include_router(admin_controller, prefix="/admin")
