from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.media import MediaAsset
from app.schemas.media import MediaCreate, MediaType
from app.core.s3 import s3_client
from app.core.config import settings
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class MediaRepository(BaseRepository[MediaAsset]):
    def __init__(self):
        super().__init__(MediaAsset)

    async def create(self, db: AsyncSession, *, obj_in: MediaCreate, owner_user_id: Optional[int] = None) -> MediaAsset:
        db_obj = MediaAsset(
            owner_user_id=owner_user_id,
            kind=obj_in.kind,
            storage_key=obj_in.storage_key,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_with_upload(
        self, 
        db: AsyncSession, 
        *, 
        file_content: bytes,
        file_key: str,
        kind: MediaType,
        owner_user_id: Optional[int] = None,
        content_type: str = "image/jpeg"
    ) -> MediaAsset:
        """Создает медиа запись (пробует загрузить в S3, если возможно)"""
        
        # Сначала создаем запись в БД
        media_data = MediaCreate(kind=kind, storage_key=file_key)
        media = await self.create(db, obj_in=media_data, owner_user_id=owner_user_id)
        
        # Затем пробуем загрузить в S3 (если доступен)
        try:
            # Проверяем, доступен ли S3 клиент
            if hasattr(s3_client, 'client') and s3_client.client is not None:
                public_url = await s3_client.upload_file(
                    file_content=file_content,
                    file_key=file_key,
                    content_type=content_type
                )
                logger.info(f"Файл загружен в S3: {file_key}")
            else:
                logger.warning("S3 клиент не доступен, создаем запись без S3")
        except Exception as e:
            logger.warning(f"Не удалось загрузить в S3: {e}. Создаем запись без S3")
            # Не падаем - медиа уже создано в БД
        
        return media

    async def get_by_owner(self, db: AsyncSession, owner_user_id: int, skip: int = 0, limit: int = 100) -> List[MediaAsset]:
        result = await db.execute(
            select(MediaAsset)
            .where(MediaAsset.owner_user_id == owner_user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_storage_key(self, db: AsyncSession, storage_key: str) -> Optional[MediaAsset]:
        result = await db.execute(
            select(MediaAsset).where(MediaAsset.storage_key == storage_key)
        )
        return result.scalar_one_or_none()

    async def update_dimensions(self, db: AsyncSession, media_id: int, width: int, height: int) -> MediaAsset:
        media = await self.get(db, media_id)
        if media:
            media.width = width
            media.height = height
            await db.commit()
            await db.refresh(media)
        return media