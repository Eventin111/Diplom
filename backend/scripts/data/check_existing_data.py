import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent))

async def main():
    from app.core.db import engine
    
    try:
        async with engine.connect() as conn:
            print("🔍 Проверяем существующие данные в базе...")
            
            # Проверяем пользователей
            result = await conn.execute(text("SELECT COUNT(*) as count FROM users"))
            user_count = result.scalar()
            print(f"👥 Количество пользователей: {user_count}")
            
            result = await conn.execute(text("SELECT id, username, email FROM users"))
            users = result.all()
            for user in users:
                print(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}")
            
            # Проверяем медиа
            result = await conn.execute(text("SELECT COUNT(*) as count FROM media_assets"))
            media_count = result.scalar()
            print(f"\n🖼️ Количество медиа: {media_count}")
            
            result = await conn.execute(text("SELECT id, storage_key, kind FROM media_assets"))
            media = result.all()
            for item in media:
                print(f"   - ID: {item.id}, Key: {item.storage_key}, Type: {item.kind}")
            
            # Проверяем одежду
            result = await conn.execute(text("SELECT COUNT(*) as count FROM garments"))
            garment_count = result.scalar()
            print(f"\n👕 Количество одежды: {garment_count}")
            
            result = await conn.execute(text("SELECT id, title, brand FROM garments"))
            garments = result.all()
            for garment in garments:
                print(f"   - ID: {garment.id}, Title: {garment.title}, Brand: {garment.brand}")
            
            # Проверяем посты
            result = await conn.execute(text("SELECT COUNT(*) as count FROM feed_items"))
            post_count = result.scalar()
            print(f"\n📝 Количество постов: {post_count}")
            
            result = await conn.execute(text("SELECT id, user_id, caption FROM feed_items"))
            posts = result.all()
            for post in posts:
                print(f"   - ID: {post.id}, User ID: {post.user_id}, Caption: {post.caption}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
