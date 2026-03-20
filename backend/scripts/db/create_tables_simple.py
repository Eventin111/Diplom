import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

async def create_tables():
    """Простое создание таблиц без Alembic"""
    from app.core.db import engine, Base
    from app.models.user import User
    from app.models.media import MediaAsset
    from app.models.garment import Garment
    from app.models.feed import FeedItem
    from app.models.likes import Like
    from app.models.tryon import TryOnSession
    
    print("🔄 Создание таблиц...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы успешно!")
        
        # Показываем созданные таблицы
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = result.scalars().all()
            print(f"\n📊 Созданные таблицы ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
                
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_tables())
