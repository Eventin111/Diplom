from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.application.dto.wardrobe_dto import WardrobeItemCreate
from app.infrastructure.persistence.models.garment import Garment
from app.infrastructure.persistence.models.wardrobe import WardrobeItem

from .base import BaseRepository


class WardrobeRepository(BaseRepository[WardrobeItem]):
    def __init__(self):
        super().__init__(WardrobeItem)

    async def create(self, db: AsyncSession, *, obj_in: WardrobeItemCreate, user_id: int) -> WardrobeItem:
        existing = await self.get_by_user_and_garment(db, user_id=user_id, garment_id=obj_in.garment_id)
        if existing:
            return existing

        db_obj = WardrobeItem(user_id=user_id, garment_id=obj_in.garment_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user_and_garment(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        garment_id: int,
    ) -> Optional[WardrobeItem]:
        result = await db.execute(
            select(WardrobeItem).where(WardrobeItem.user_id == user_id, WardrobeItem.garment_id == garment_id)
        )
        return result.scalar_one_or_none()

    async def get_user_items(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[WardrobeItem]:
        result = await db.execute(
            select(WardrobeItem)
            .options(joinedload(WardrobeItem.garment).joinedload(Garment.media))
            .where(WardrobeItem.user_id == user_id)
            .order_by(WardrobeItem.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_by_user_and_garment(self, db: AsyncSession, *, user_id: int, garment_id: int) -> bool:
        result = await db.execute(
            delete(WardrobeItem).where(WardrobeItem.user_id == user_id, WardrobeItem.garment_id == garment_id)
        )
        await db.commit()
        return bool(result.rowcount)
