"""
Скрипт для проверки состояния базы данных.
Запустить: python check_db.py
"""

import asyncio
from sqlalchemy import text
from app.core.db import AsyncSessionLocal


async def check_tables():
    async with AsyncSessionLocal() as session:
        # Список всех таблиц
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = result.fetchall()
        
        print("📊 Таблицы в базе данных:")
        print("-" * 30)
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        print("\n📈 Количество записей:")
        print("-" * 30)
        
        # Проверяем основные таблицы (правильные названия)
        tables_to_check = ['users', 'garments', 'media_assets', 'likes', 'feed_items', 'tryon_sessions']
        
        for table in tables_to_check:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count}")
                await session.commit()
            except Exception as e:
                print(f"  {table}: таблица не существует")
                await session.rollback()
        
        # Пример данных из users
        print("\n👤 Пример пользователей:")
        print("-" * 30)
        try:
            result = await session.execute(text("SELECT id, email, username FROM users LIMIT 5"))
            users = result.fetchall()
            for user in users:
                print(f"  ID: {user[0]}, Email: {user[1]}, Username: {user[2]}")
        except Exception as e:
            print(f"  Ошибка: {e}")


async def main():
    print("=" * 40)
    print("Проверка базы данных SwipeIt")
    print("=" * 40)
    print()
    await check_tables()
    print()
    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(main())
