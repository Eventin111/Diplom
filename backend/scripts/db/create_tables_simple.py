import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


async def create_tables():
    """Create database tables without Alembic."""
    from app.infrastructure.db.db import Base, engine
    from app.infrastructure.persistence.models.feed import FeedItem
    from app.infrastructure.persistence.models.garment import Garment
    from app.infrastructure.persistence.models.likes import Like
    from app.infrastructure.persistence.models.media import MediaAsset
    from app.infrastructure.persistence.models.tryon import TryOnSession
    from app.infrastructure.persistence.models.user import User

    print("Creating tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

        async with engine.connect() as conn:
            from sqlalchemy import text

            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = result.scalars().all()
            print(f"\nCreated tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")

    except Exception as exc:
        print(f"Failed to create tables: {exc}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_tables())
