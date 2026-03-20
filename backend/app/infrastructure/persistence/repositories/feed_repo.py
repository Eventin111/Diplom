from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.infrastructure.persistence.models.feed import FeedItem
from app.infrastructure.persistence.models.media import MediaAsset
from app.application.dto.feed_dto import FeedItemCreate
from .base import BaseRepository

class FeedRepository(BaseRepository[FeedItem]):
    def __init__(self):
        super().__init__(FeedItem)

    async def create(self, db: AsyncSession, *, obj_in: FeedItemCreate, user_id: int) -> FeedItem:
        db_obj = FeedItem(
            user_id=user_id,
            garment_id=obj_in.garment_id,
            caption=obj_in.caption,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Связываем медиа с постом (если есть)
        if obj_in.media_ids:
            await self._link_media_to_feed_item(db, db_obj.id, obj_in.media_ids)
        
        return db_obj

    async def _link_media_to_feed_item(self, db: AsyncSession, feed_item_id: int, media_ids: List[int]):
        """Связывает медиа с постом через промежуточную таблицу"""
        # В реальном проекте это должно быть в отдельной модели
        # Сейчас создадим простую связь через поле в медиа (для MVP)
        for media_id in media_ids:
            result = await db.execute(
                select(MediaAsset).where(MediaAsset.id == media_id)
            )
            media = result.scalar_one_or_none()
            if media:
                # В MVP просто обновляем owner_user_id для связи
                # В production нужно создать отдельную таблицу feed_media
                pass
        
        await db.commit()

    async def get_with_media(self, db: AsyncSession, feed_item_id: int) -> Optional[FeedItem]:
        result = await db.execute(
            select(FeedItem)
            .options(
                selectinload(FeedItem.garment),
                selectinload(FeedItem.user)
            )
            .where(FeedItem.id == feed_item_id)
        )
        return result.scalar_one_or_none()

    async def get_user_feed(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> List[FeedItem]:
        result = await db.execute(
            select(FeedItem)
            .options(
                selectinload(FeedItem.garment),
                selectinload(FeedItem.user)
            )
            .where(FeedItem.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_global_feed(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> List[FeedItem]:
        result = await db.execute(
            select(FeedItem)
            .options(
                selectinload(FeedItem.garment),
                selectinload(FeedItem.user)
            )
            .order_by(FeedItem.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_feed_with_stats(self, db: AsyncSession, current_user_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[dict]:
        from app.infrastructure.persistence.models.likes import Like
        
        # Получаем посты
        feed_items = await self.get_global_feed(db, skip, limit)
        
        if not feed_items:
            return []
        
        # Собираем ID постов для статистики
        feed_item_ids = [item.id for item in feed_items]
        
        # Запрос количества лайков для каждого поста
        likes_count_query = (
            select(Like.feed_item_id, func.count(Like.id).label('likes_count'))
            .where(Like.feed_item_id.in_(feed_item_ids))
            .group_by(Like.feed_item_id)
            .subquery()
        )
        
        # Формируем результат
        result = []
        for item in feed_items:
            item_data = {
                "feed_item": item,
                "likes_count": 0,
                "is_liked": False
            }
            
            # В реальном проекте нужно добавить подсчет лайков
            # и проверку лайка текущего пользователя
            
            result.append(item_data)
        
        return result
