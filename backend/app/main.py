from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import setup_exception_handlers
from app.core.hashing import hash_password
from app.infrastructure.db.db import Base, engine
from app.infrastructure.db.schema_compat import ensure_schema_compatibility
from app.infrastructure.persistence import models  # noqa: F401
from app.infrastructure.persistence.models.feed import FeedItem
from app.infrastructure.persistence.models.user import User
from app.infrastructure.queue.redis_client import close_redis_client
from app.infrastructure.storage.s3 import s3_client
from app.presentation.api.routes import api_router


DEMO_FEED_CAPTIONS = [
    "Классический костюм и рубашка для офиса #офисныйстиль #деловойкостюм",
    "Подборка вечерних платьев для особого случая #вечернийобраз #платье",
    "Спортивная коллекция для активного отдыха #спорт #стиль #тренировки",
    "Капсула для города: обувь и базовые вещи #повседневка #городскойстиль",
    "Верхняя одежда на осень: пальто и куртки #пальто #классика #осень",
    "Бохо-образы и легкие ткани для теплого сезона #бохо #свободныйстиль #творчество",
]
DEMO_FEED_EMAIL = "demo-feed@swipelt.com"
DEMO_FEED_USERNAME = "demo_feed"
LEGACY_DEMO_FEED_EMAILS = ("demo-feed@swipelt.local",)


async def ensure_demo_user_exists() -> None:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == "test@mail.ru"))
        existing_user = result.scalar_one_or_none()
        if existing_user is not None:
            return

        session.add(
            User(
                email="test@mail.ru",
                username="testuser",
                hashed_password=hash_password("123123"),
            )
        )
        await session.commit()


async def seed_demo_feed() -> None:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(
                or_(
                    User.email == DEMO_FEED_EMAIL,
                    User.username == DEMO_FEED_USERNAME,
                )
            ).order_by(User.id.asc()).limit(1)
        )
        demo_user = result.scalar_one_or_none()

        if demo_user is None:
            legacy_result = await session.execute(
                select(User).where(User.email.in_(LEGACY_DEMO_FEED_EMAILS))
            )
            demo_user = legacy_result.scalar_one_or_none()
            if demo_user is not None:
                demo_user.email = DEMO_FEED_EMAIL
                await session.flush()

        if demo_user is None:
            demo_user = User(
                email=DEMO_FEED_EMAIL,
                username=DEMO_FEED_USERNAME,
                hashed_password=hash_password("DemoFeed123"),
            )
            session.add(demo_user)
            await session.flush()
        elif demo_user.email != DEMO_FEED_EMAIL:
            demo_user.email = DEMO_FEED_EMAIL
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
    # Warm up S3 client and ensure bucket exists on startup.
    _ = s3_client.client
    await ensure_demo_user_exists()
    await seed_demo_feed()
    try:
        yield
    finally:
        await close_redis_client()


app = FastAPI(title="SwipeIt Backend (MVP)", lifespan=lifespan)

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
