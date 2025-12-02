from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.likes import Like
from app.schemas.social import LikeCreate
from .base import BaseRepository

class LikeRepository(BaseRepository[Like]):
    def __init__(self):
        super().__init__(Like)

    async def create(self, db: AsyncSession, *, obj_in: LikeCreate, user_id: int) -> Like:
        # Проверяем, не лайкнул ли уже
        existing_like = await self.get_by_user_and_feed_item(db, user_id=user_id, feed_item_id=obj_in.feed_item_id)
        if existing_like:
            return existing_like
            
        db_obj = Like(
            user_id=user_id,
            feed_item_id=obj_in.feed_item_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user_and_feed_item(self, db: AsyncSession, user_id: int, feed_item_id: int) -> Optional[Like]:
        result = await db.execute(
            select(Like).where(
                Like.user_id == user_id,
                Like.feed_item_id == feed_item_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_likes(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> List[Like]:
        result = await db.execute(
            select(Like)
            .where(Like.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_feed_item_likes(self, db: AsyncSession, feed_item_id: int, skip: int = 0, limit: int = 50) -> List[Like]:
        result = await db.execute(
            select(Like)
            .where(Like.feed_item_id == feed_item_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_feed_item_likes(self, db: AsyncSession, feed_item_id: int) -> int:
        result = await db.execute(
            select(Like).where(Like.feed_item_id == feed_item_id)
        )
        likes = result.scalars().all()
        return len(likes)

    async def delete_by_user_and_feed_item(self, db: AsyncSession, user_id: int, feed_item_id: int) -> bool:
        result = await db.execute(
            delete(Like).where(
                Like.user_id == user_id,
                Like.feed_item_id == feed_item_id
            )
        )
        await db.commit()
        return result.rowcount > 0

    async def toggle_like(self, db: AsyncSession, user_id: int, feed_item_id: int) -> tuple[bool, Optional[Like]]:
        """Переключает лайк: если есть - убирает, если нет - ставит"""
        existing_like = await self.get_by_user_and_feed_item(db, user_id, feed_item_id)
        if existing_like:
            await db.delete(existing_like)
            await db.commit()
            return False, None
        else:
            like = Like(user_id=user_id, feed_item_id=feed_item_id)
            db.add(like)
            await db.commit()
            await db.refresh(like)
            return True, like