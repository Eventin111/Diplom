from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Асинхронный engine с asyncpg драйвером
engine = create_async_engine(
    str(settings.DB_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,  # Для разработки - показывает SQL запросы
    pool_pre_ping=True,
    future=True
)

# Асинхронная фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Асинхронная зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()