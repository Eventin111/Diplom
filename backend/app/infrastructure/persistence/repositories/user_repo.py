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
        from app.infrastructure.persistence.models.likes import Like

        # Базовые данные пользователя
        user = await self.get(db, user_id)
        if not user:
            return None

        # Статистика постов
        posts_count_result = await db.execute(select(func.count(FeedItem.id)).where(FeedItem.user_id == user_id))
        posts_count = posts_count_result.scalar()

        # Статистика лайков
        likes_count_result = await db.execute(select(func.count(Like.id)).where(Like.user_id == user_id))
        likes_count = likes_count_result.scalar()

        return {"user": user, "stats": {"posts_count": posts_count or 0, "likes_count": likes_count or 0}}
