import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


async def main():
    from app.infrastructure.db.db import AsyncSessionLocal
    from app.infrastructure.persistence.repositories.feed_repo import FeedRepository
    from app.infrastructure.persistence.repositories.garment_repo import GarmentRepository
    from app.infrastructure.persistence.repositories.media_repo import MediaRepository
    from app.infrastructure.persistence.repositories.user_repo import UserRepository
    from app.application.dto.media_dto import MediaCreate, MediaType
    from app.presentation.api.schemas.feed import FeedItemCreate
    from app.presentation.api.schemas.garment import GarmentCreate
    from app.presentation.api.schemas.user import UserCreate

    print("Creating test data without S3...")

    async with AsyncSessionLocal() as db:
        try:
            user_repo = UserRepository()
            user = await user_repo.create(
                db,
                obj_in=UserCreate(
                    email="test@example.com",
                    username="testuser",
                    password="test123",
                ),
            )
            print(f"Created user: {user.username} (ID: {user.id})")

            media_repo = MediaRepository()
            media = await media_repo.create(
                db,
                obj_in=MediaCreate(
                    kind=MediaType.IMAGE,
                    storage_key="test/avatar.jpg",
                ),
                owner_user_id=user.id,
            )
            print(f"Created media: {media.storage_key} (ID: {media.id})")

            garment_repo = GarmentRepository()
            garment = await garment_repo.create(
                db,
                obj_in=GarmentCreate(
                    title="Test T-Shirt",
                    brand="TestBrand",
                    media_id=media.id,
                ),
            )
            print(f"Created garment: {garment.title} (ID: {garment.id})")

            feed_repo = FeedRepository()
            feed_item = await feed_repo.create(
                db,
                obj_in=FeedItemCreate(
                    caption="My first SwipeIt post!",
                    garment_id=garment.id,
                    media_ids=[media.id],
                ),
                user_id=user.id,
            )
            print(f"Created feed item: {feed_item.caption} (ID: {feed_item.id})")

            await db.commit()
            print("\nTest data created successfully.")

        except Exception as exc:
            await db.rollback()
            print(f"Failed to create test data: {exc}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
