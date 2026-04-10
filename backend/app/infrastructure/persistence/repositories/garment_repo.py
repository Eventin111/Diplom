from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.garment_dto import GarmentCreate, GarmentUpdate
from app.infrastructure.persistence.models.garment import Garment

from .base import BaseRepository


class GarmentRepository(BaseRepository[Garment]):
    def __init__(self):
        super().__init__(Garment)

    async def create(self, db: AsyncSession, *, obj_in: GarmentCreate) -> Garment:
        db_obj = Garment(
            title=obj_in.title,
            brand=obj_in.brand,
            media_id=obj_in.media_id,
            garment_metadata=obj_in.garment_metadata,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Garment, obj_in: GarmentUpdate) -> Garment:
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:  # Обновляем только если значение не None
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def search(self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 50) -> List[Garment]:
        result = await db.execute(
            select(Garment)
            .where(Garment.title.ilike(f"%{query}%") | Garment.brand.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_brand(self, db: AsyncSession, brand: str, skip: int = 0, limit: int = 50) -> List[Garment]:
        result = await db.execute(select(Garment).where(Garment.brand == brand).offset(skip).limit(limit))
        return result.scalars().all()
