import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent))

async def main():
    from app.core.db import engine
    
    try:
        async with engine.begin() as conn:
            print("🧹 Полная очистка базы данных...")
            
            # Отключаем ограничения внешних ключей
            await conn.execute(text("SET session_replication_role = 'replica'"))
            
            # Удаляем все данные из таблиц (в правильном порядке)
            tables = [
                "likes", "tryon_sessions", "feed_items", 
                "garments", "media_assets", "users"
            ]
            
            for table in tables:
                await conn.execute(text(f"DELETE FROM {table}"))
                print(f"✅ Очищена таблица: {table}")
            
            # Сбрасываем sequences (автоинкрементные счётчики)
            sequences = [
                "users_id_seq", "media_assets_id_seq", "garments_id_seq",
                "feed_items_id_seq", "likes_id_seq", "tryon_sessions_id_seq"
            ]
            
            for sequence in sequences:
                try:
                    await conn.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                    print(f"✅ Сброшен sequence: {sequence}")
                except Exception as e:
                    print(f"⚠️ Не удалось сбросить {sequence}: {e}")
            
            # Включаем обратно ограничения внешних ключей
            await conn.execute(text("SET session_replication_role = 'origin'"))
            
            await conn.commit()
            
        print("🎉 База данных полностью очищена и сброшена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())