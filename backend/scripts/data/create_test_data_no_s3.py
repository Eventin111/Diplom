import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

async def main():
    from app.core.db import AsyncSessionLocal
    from app.repositories.user_repo import UserRepository
    from app.repositories.media_repo import MediaRepository
    from app.repositories.garment_repo import GarmentRepository
    from app.repositories.feed_repo import FeedRepository
    from app.schemas.user import UserCreate
    from app.schemas.media import MediaCreate, MediaType
    from app.schemas.garment import GarmentCreate
    from app.schemas.feed import FeedItemCreate
    
    print("Создание тестовых данных (без S3)...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Создаем тестового пользователя
            user_repo = UserRepository()
            user_data = UserCreate(
                email="test@example.com",
                username="testuser",
                password="test123"
            )
            user = await user_repo.create(db, obj_in=user_data)
            print(f"✅ Создан пользователь: {user.username} (ID: {user.id})")
            
            # Создаем тестовые медиа (без S3 загрузки)
            media_repo = MediaRepository()
            media_data = MediaCreate(
                kind=MediaType.IMAGE,
                storage_key="test/avatar.jpg"  # Просто запись в БД, без S3
            )
            media = await media_repo.create(db, obj_in=media_data, owner_user_id=user.id)
            print(f"✅ Создано медиа: {media.storage_key} (ID: {media.id})")
            
            # Создаем тестовую одежду
            garment_repo = GarmentRepository()
            garment_data = GarmentCreate(
                title="Тестовая футболка",
                brand="TestBrand",
                media_id=media.id
            )
            garment = await garment_repo.create(db, obj_in=garment_data)
            print(f"✅ Создана одежда: {garment.title} (ID: {garment.id})")
            
            # Создаем тестовый пост
            feed_repo = FeedRepository()
            feed_data = FeedItemCreate(
                caption="Мой первый пост в SwipeIt!",
                garment_id=garment.id,
                media_ids=[media.id]
            )
            feed_item = await feed_repo.create(db, obj_in=feed_data, user_id=user.id)
            print(f"✅ Создан пост: {feed_item.caption} (ID: {feed_item.id})")
            
            await db.commit()
            print("\n🎉 Тестовые данные успешно созданы (без S3)!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Ошибка создания тестовых данных: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
