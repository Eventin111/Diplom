from typing import AsyncGenerator
from app.core.db import AsyncSession, get_db
from app.repositories import (
    UserRepository,
    MediaRepository,
    GarmentRepository,
    FeedRepository,
    LikeRepository,
    TryOnRepository,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Фабрики репозиториев
def get_user_repository() -> UserRepository:
    return UserRepository()

def get_media_repository() -> MediaRepository:
    return MediaRepository()

def get_garment_repository() -> GarmentRepository:
    return GarmentRepository()

def get_feed_repository() -> FeedRepository:
    return FeedRepository()

def get_like_repository() -> LikeRepository:
    return LikeRepository()

def get_tryon_repository() -> TryOnRepository:
    return TryOnRepository()