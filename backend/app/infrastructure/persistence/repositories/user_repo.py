from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.user_dto import UserCreate, UserUpdate
from app.core.hashing import hash_password, verify_password
from app.infrastructure.persistence.models.user import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        hashed_password = hash_password(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_with_stats(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        from sqlalchemy import func, select

        from app.infrastructure.persistence.models.feed import FeedItem
        from app.infrastructure.persistence.models.follow import FollowRelation
        from app.infrastructure.persistence.models.likes import Like
        from app.infrastructure.persistence.models.tryon import TryOnSession
        from app.infrastructure.persistence.models.wardrobe import WardrobeItem

        # Базовые данные пользователя
        user = await self.get(db, user_id)
        if not user:
            return None

        # Статистика постов
        posts_count_result = await db.execute(select(func.count(FeedItem.id)).where(FeedItem.user_id == user_id))
        posts_count = posts_count_result.scalar()

        # Количество лайков, поставленных пользователем
        likes_count_result = await db.execute(select(func.count(Like.id)).where(Like.user_id == user_id))
        likes_count = likes_count_result.scalar()

        # Количество сессий примерки
        tryons_count_result = await db.execute(select(func.count(TryOnSession.id)).where(TryOnSession.user_id == user_id))
        tryons_count = tryons_count_result.scalar()

        # Количество сохраненных вещей в гардеробе
        wardrobe_count_result = await db.execute(select(func.count(WardrobeItem.id)).where(WardrobeItem.user_id == user_id))
        wardrobe_count = wardrobe_count_result.scalar()

        followers_count_result = await db.execute(
            select(func.count(FollowRelation.id)).where(FollowRelation.following_id == user_id)
        )
        followers_count = followers_count_result.scalar()

        following_count_result = await db.execute(
            select(func.count(FollowRelation.id)).where(FollowRelation.follower_id == user_id)
        )
        following_count = following_count_result.scalar()

        return {
            "user": user,
            "stats": {
                "posts_count": posts_count or 0,
                "likes_count": likes_count or 0,
                "tryons_count": tryons_count or 0,
                "wardrobe_count": wardrobe_count or 0,
                "followers_count": followers_count or 0,
                "following_count": following_count or 0,
            },
        }
