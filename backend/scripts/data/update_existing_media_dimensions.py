import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import AsyncSessionLocal
from app.repositories.media_repo import MediaRepository
from app.core.s3 import s3_client
from app.core.image_processor import ImageProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_existing_media():
    """Обновить размеры для существующих изображений без width/height"""
    async with AsyncSessionLocal() as db:
        media_repo = MediaRepository()
        
        # Получаем все медиа без размеров
        all_media = await media_repo.get_multi(db, skip=0, limit=1000)
        
        updated_count = 0
        
        for media in all_media:
            if media.kind == "image" and (media.width is None or media.height is None):
                try:
                    # Пытаемся скачать файл из S3 для определения размеров
                    if s3_client.client:
                        response = s3_client.client.get_object(
                            Bucket=s3_client.bucket_name,
                            Key=media.storage_key
                        )
                        image_data = response['Body'].read()
                        
                        dimensions = ImageProcessor.get_image_dimensions(image_data)
                        if dimensions:
                            width, height = dimensions
                            
                            media.width = width
                            media.height = height
                            await db.commit()
                            updated_count += 1
                            logger.info(f"Обновлено медиа {media.id}: {width}x{height}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при обновлении медиа {media.id}: {e}")
                    continue
        
        logger.info(f"Обновлено {updated_count} из {len(all_media)} медиа записей")

if __name__ == "__main__":
    asyncio.run(update_existing_media())
