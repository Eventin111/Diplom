import logging
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.media_dto import MediaCreate, MediaType
from app.core.config import settings
from app.core.image_processor import ImageProcessor
from app.infrastructure.persistence.models.media import MediaAsset
from app.infrastructure.storage.local_media import build_local_media_path
from app.infrastructure.storage.s3 import s3_client

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MediaRepository(BaseRepository[MediaAsset]):
    def __init__(self):
        super().__init__(MediaAsset)

    async def create(self, db: AsyncSession, *, obj_in: MediaCreate, owner_user_id: Optional[int] = None) -> MediaAsset:
        db_obj = MediaAsset(
            owner_user_id=owner_user_id,
            kind=obj_in.kind,
            storage_key=obj_in.storage_key,
            width=obj_in.width,  # Сохраняем ширину
            height=obj_in.height,  # Сохраняем высоту
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
        content_type: str = "image/jpeg",
    ) -> MediaAsset:
        """Создает медиа запись с загрузкой в S3 и определением размеров"""

        # Определяем размеры изображения если это картинка
        width = None
        height = None

        if kind == MediaType.IMAGE:
            dimensions = ImageProcessor.get_image_dimensions(file_content)
            if dimensions:
                width, height = dimensions
                logger.info(f"Определены размеры изображения: {width}x{height}")

        # Создаем медиа запись с размерами
        media_data = MediaCreate(kind=kind, storage_key=file_key, width=width, height=height)

        media = await self.create(db, obj_in=media_data, owner_user_id=owner_user_id)
        local_file_path = build_local_media_path(file_key)
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        local_file_path.write_bytes(file_content)

        # Затем пробуем загрузить в S3 (если доступен)
        try:
            if hasattr(s3_client, "client") and s3_client.client is not None:
                public_url = await s3_client.upload_file(
                    file_content=file_content, file_key=file_key, content_type=content_type
                )
                logger.info(f"Файл загружен в S3: {file_key}")
            else:
                logger.warning("S3 клиент не доступен, создаем запись без S3")
        except Exception as e:
            logger.warning(f"Не удалось загрузить в S3: {e}. Создаем запись без S3")

        return media

    # ... остальные методы остаются без изменений

    async def get_by_dimensions(
        self,
        db: AsyncSession,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> List[MediaAsset]:
        """Получить медиа по фильтрам размеров"""
        query = select(MediaAsset)

        conditions = []
        if min_width is not None:
            conditions.append(MediaAsset.width >= min_width)
        if min_height is not None:
            conditions.append(MediaAsset.height >= min_height)
        if max_width is not None:
            conditions.append(MediaAsset.width <= max_width)
        if max_height is not None:
            conditions.append(MediaAsset.height <= max_height)

        if conditions:
            query = query.where(*conditions)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_ids(self, db: AsyncSession, media_ids: list[int]) -> List[MediaAsset]:
        if not media_ids:
            return []

        result = await db.execute(select(MediaAsset).where(MediaAsset.id.in_(media_ids)))
        return result.scalars().all()

    async def get_by_owner(
        self,
        db: AsyncSession,
        owner_user_id: int,
        *,
        limit: int = 100,
    ) -> List[MediaAsset]:
        result = await db.execute(
            select(MediaAsset)
            .where(MediaAsset.owner_user_id == owner_user_id)
            .order_by(MediaAsset.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_many(self, db: AsyncSession, media_ids: list[int]) -> int:
        if not media_ids:
            return 0

        result = await db.execute(delete(MediaAsset).where(MediaAsset.id.in_(media_ids)))
        await db.commit()
        return int(result.rowcount or 0)

    def delete_storage(self, storage_key: str) -> dict[str, bool]:
        local_file_path = build_local_media_path(storage_key)
        local_deleted = False
        if local_file_path.exists():
            local_file_path.unlink()
            local_deleted = True

        s3_deleted = s3_client.delete_file(storage_key)
        return {
            "local_deleted": local_deleted,
            "s3_deleted": s3_deleted,
        }
