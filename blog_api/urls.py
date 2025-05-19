from fastapi import APIRouter

from blog_api.controllers.admin import admin_controller
from blog_api.controllers.comments import comments_controller
from blog_api.controllers.posts import posts_controller
from blog_api.controllers.users import users_controller

api_router = APIRouter()
api_router.include_router(users_controller, prefix="/account")
api_router.include_router(admin_controller, prefix="/admin")
api_router.include_router(posts_controller, prefix="/posts")
api_router.include_router(comments_controller, prefix="/comments")
