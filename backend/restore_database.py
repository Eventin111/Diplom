import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

async def restore_database():
    """Восстановление только структуры базы данных (без тестовых данных)"""
    
    print("🗄️  ВОССТАНОВЛЕНИЕ СТРУКТУРЫ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # 1. Проверяем текущее состояние
    print("📊 Шаг 1: Проверка текущего состояния...")
    from check_db_status import main as check_status
    await check_status()
    
    # 2. Создаем таблицы (если их нет)
    print("\n🔄 Шаг 2: Создание таблиц (если отсутствуют)...")
    from create_tables_simple import create_tables
    await create_tables()
    
    # 3. Пропускаем создание тестовых данных (они уже есть)
    print("\n✅ Шаг 3: Тестовые данные уже существуют, пропускаем...")
    print("   test@example.com / test123")
    print("   SAPavlenko1@mail.ru / ваш_пароль")
    
    # 4. Финальная проверка
    print("\n✅ Шаг 4: Финальная проверка...")
    from check_existing_data import main as check_data
    await check_data()
    
    print("\n🎉 База данных готова к работе!")
    print("Теперь можно запускать сервер: uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(restore_database())