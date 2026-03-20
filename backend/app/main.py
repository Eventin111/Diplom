from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base, engine
from app.core.redis_client import close_redis_client
from app.core.schema_compat import ensure_schema_compatibility
from app.api.routes import api_router
from app.core.errors import setup_exception_handlers
from app import models  # noqa: F401
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.hashing import hash_password
from app.models.feed import FeedItem
from app.models.user import User


DEMO_FEED_CAPTIONS = [
    "Классический костюм и рубашка для офиса #офисныйстиль #деловойкостюм",
    "Подборка вечерних платьев для особого случая #вечернийобраз #платье",
    "Спортивная коллекция для активного отдыха #спорт #стиль #тренировки",
    "Капсула для города: обувь и базовые вещи #повседневка #городскойстиль",
    "Верхняя одежда на осень: пальто и куртки #пальто #классика #осень",
    "Бохо-образы и легкие ткани для теплого сезона #бохо #свободныйстиль #творчество",
]


async def seed_demo_feed() -> None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.email == "demo-feed@swipelt.local")
        )
        demo_user = result.scalar_one_or_none()

        if demo_user is None:
            demo_user = User(
                email="demo-feed@swipelt.local",
                username="demo_feed",
                hashed_password=hash_password("DemoFeed123"),
            )
            session.add(demo_user)
            await session.flush()

        existing_ids = set(
            (
                await session.execute(
                    select(FeedItem.id).where(FeedItem.id.in_(range(1, len(DEMO_FEED_CAPTIONS) + 1)))
                )
            ).scalars()
        )

        for index, caption in enumerate(DEMO_FEED_CAPTIONS, start=1):
            if index in existing_ids:
                continue
            session.add(
                FeedItem(
                    id=index,
                    user_id=demo_user.id,
                    caption=caption,
                )
            )

        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_schema_compatibility(engine)
    await seed_demo_feed()
    try:
        yield
    finally:
        await close_redis_client()


app = FastAPI(title="SwipeIt Backend (MVP)", lifespan=lifespan)

# Настройка обработчиков исключений
setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
