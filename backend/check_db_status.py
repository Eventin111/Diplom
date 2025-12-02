import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

async def main():
    from app.core.db import engine
    from sqlalchemy import text
    
    try:
        async with engine.connect() as conn:
            print("🔍 Проверяем состояние базы данных...")
            
            # Проверяем существующие таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.scalars().all()
            
            print(f"📊 Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
            
            # Проверяем данные в каждой таблице
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.scalar()
                print(f"   {table}: {count} записей")
                
            if not tables:
                print("❌ База данных ПУСТАЯ! Нужно применить миграции.")
            else:
                print("✅ База данных содержит таблицы")
                
    except Exception as e:
        print(f"❌ Ошибка подключения к базе: {e}")

if __name__ == "__main__":
    asyncio.run(main())