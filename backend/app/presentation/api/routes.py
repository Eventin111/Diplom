from fastapi import APIRouter

from app.presentation.api.v1 import auth, feed, garments, health, media, tryon

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(garments.router, prefix="/garments", tags=["garments"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(tryon.router, prefix="/tryon", tags=["tryon"])
