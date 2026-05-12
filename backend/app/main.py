from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import setup_exception_handlers
from app.core.hashing import hash_password
from app.infrastructure.db.db import Base, engine
from app.infrastructure.db.schema_compat import ensure_schema_compatibility
from app.infrastructure.persistence.models import comment, comment_like, feed, follow, garment, likes, media, tryon, tryon_event, user, wardrobe
from app.infrastructure.persistence.models.feed import FeedItem
from app.infrastructure.persistence.models.garment import Garment
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
MODEL_MODULES = (comment, comment_like, feed, follow, garment, likes, media, tryon, tryon_event, user, wardrobe)
DEMO_CREATOR_PROFILES = [
    {
        "email": "alex.style@swipelt.com",
        "username": "alex_style",
        "caption": "Брендовый образ: классика и офисный стиль",
        "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
    {
        "email": "mari.fashion@swipelt.com",
        "username": "mari_fashion",
        "caption": "Вечерняя коллекция, собранная из примерки",
        "image_url": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
    {
        "email": "ivan.sport@swipelt.com",
        "username": "ivan_sport",
        "caption": "Спортивный лук для города",
        "image_url": "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
    {
        "email": "elena.chic@swipelt.com",
        "username": "elena_chic",
        "caption": "Капсула для города: обувь и базовые вещи",
        "image_url": "https://images.unsplash.com/photo-1463100099107-aa0980c362e6?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
    {
        "email": "dima.classic@swipelt.com",
        "username": "dima_classic",
        "caption": "Верхняя одежда на осень",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
    {
        "email": "anna.boho@swipelt.com",
        "username": "anna_boho",
        "caption": "Бохо-образы для теплого сезона",
        "image_url": "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "look_image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=900&q=85&fm=jpg",
        "garment_image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=900&q=85&fm=jpg",
    },
]


async def _sync_id_sequence(session: AsyncSession, table_name: str) -> None:
    """Align SERIAL sequence with current max(id) to avoid duplicate key inserts."""
    await session.execute(
        text(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', 'id'),
                COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                true
            )
            """
        )
    )


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
        await _sync_id_sequence(session, "feed_items")

        result = await session.execute(
            select(User)
            .where(
                or_(
                    User.email == DEMO_FEED_EMAIL,
                    User.username == DEMO_FEED_USERNAME,
                )
            )
            .order_by(User.id.asc())
            .limit(1)
        )
        demo_user = result.scalar_one_or_none()

        if demo_user is None:
            legacy_result = await session.execute(select(User).where(User.email.in_(LEGACY_DEMO_FEED_EMAILS)))
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

        existing_captions = set(
            (
                await session.execute(
                    select(FeedItem.caption).where(
                        FeedItem.user_id == demo_user.id,
                        FeedItem.caption.in_(DEMO_FEED_CAPTIONS),
                    )
                )
            ).scalars()
        )

        for caption in DEMO_FEED_CAPTIONS:
            if caption in existing_captions:
                continue
            session.add(
                FeedItem(
                    user_id=demo_user.id,
                    caption=caption,
                )
            )

        await session.flush()
        await _sync_id_sequence(session, "feed_items")
        await session.commit()


async def seed_demo_creator_profiles() -> None:
    async with AsyncSession(engine) as session:
        await _sync_id_sequence(session, "users")
        await _sync_id_sequence(session, "garments")
        await _sync_id_sequence(session, "feed_items")

        for profile in DEMO_CREATOR_PROFILES:
            gallery_urls = []
            for key in ("image_url", "look_image_url", "garment_image_url"):
                value = str(profile.get(key) or "").strip()
                if value and value not in gallery_urls:
                    gallery_urls.append(value)
            desired_metadata = {
                "source": "seed_demo_creator",
                "image_url": profile["image_url"],
                "gallery_urls": gallery_urls,
                "category": "creator",
            }
            if profile.get("look_image_url"):
                desired_metadata["avatar_image_url"] = profile["look_image_url"]
            if profile.get("garment_image_url"):
                desired_metadata["cloth_image_url"] = profile["garment_image_url"]

            user_result = await session.execute(select(User).where(User.username == profile["username"]).limit(1))
            creator = user_result.scalar_one_or_none()
            if creator is None:
                creator = User(
                    email=profile["email"],
                    username=profile["username"],
                    hashed_password=hash_password("DemoFeed123"),
                )
                session.add(creator)
                await session.flush()

            garment_result = await session.execute(
                select(Garment)
                .where(
                    Garment.title == f"Demo look by {profile['username']}",
                    Garment.brand == "Swipelt Creator",
                )
                .limit(1)
            )
            garment_item = garment_result.scalar_one_or_none()
            if garment_item is None:
                garment_item = Garment(
                    title=f"Demo look by {profile['username']}",
                    brand="Swipelt Creator",
                    media_id=None,
                    garment_metadata=desired_metadata,
                )
                session.add(garment_item)
                await session.flush()
            else:
                # Keep demo brand posts in sync on each startup so feed cards always
                # have the expected 2-3 images from metadata gallery urls.
                garment_item.garment_metadata = desired_metadata
                garment_item.title = f"Demo look by {profile['username']}"
                garment_item.brand = "Swipelt Creator"
                session.add(garment_item)

            feed_result = await session.execute(
                select(FeedItem)
                .where(
                    FeedItem.user_id == creator.id,
                    FeedItem.garment_id == garment_item.id,
                )
                .limit(1)
            )
            feed_item = feed_result.scalar_one_or_none()
            if feed_item is None:
                session.add(
                    FeedItem(
                        user_id=creator.id,
                        garment_id=garment_item.id,
                        caption=profile["caption"],
                    )
                )
            elif feed_item.caption != profile["caption"]:
                feed_item.caption = profile["caption"]
                session.add(feed_item)

        await session.flush()
        await _sync_id_sequence(session, "users")
        await _sync_id_sequence(session, "garments")
        await _sync_id_sequence(session, "feed_items")
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
    await seed_demo_creator_profiles()
    try:
        yield
    finally:
        await close_redis_client()


app = FastAPI(title="SwipeIt", lifespan=lifespan)

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
