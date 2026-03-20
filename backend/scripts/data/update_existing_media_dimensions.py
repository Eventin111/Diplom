import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.image_processor import ImageProcessor
from app.infrastructure.db.db import AsyncSessionLocal
from app.infrastructure.persistence.repositories.media_repo import MediaRepository
from app.infrastructure.storage.s3 import s3_client


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_existing_media():
    """Update missing width and height for stored images."""
    async with AsyncSessionLocal() as db:
        media_repo = MediaRepository()
        all_media = await media_repo.get_multi(db, skip=0, limit=1000)
        updated_count = 0

        for media in all_media:
            if media.kind == "image" and (media.width is None or media.height is None):
                try:
                    if s3_client.client:
                        response = s3_client.client.get_object(
                            Bucket=s3_client.bucket_name,
                            Key=media.storage_key,
                        )
                        image_data = response["Body"].read()
                        dimensions = ImageProcessor.get_image_dimensions(image_data)
                        if dimensions:
                            width, height = dimensions
                            media.width = width
                            media.height = height
                            await db.commit()
                            updated_count += 1
                            logger.info("Updated media %s: %sx%s", media.id, width, height)
                except Exception as exc:
                    logger.error("Failed to update media %s: %s", media.id, exc)
                    continue

        logger.info("Updated %s of %s media records", updated_count, len(all_media))


if __name__ == "__main__":
    asyncio.run(update_existing_media())
