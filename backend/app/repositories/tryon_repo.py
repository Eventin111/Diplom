from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.tryon import TryOnSession
from app.schemas.tryon import TryOnSessionCreate, TryOnStatus
from .base import BaseRepository

class TryOnRepository(BaseRepository[TryOnSession]):
    def __init__(self):
        super().__init__(TryOnSession)

    async def create(self, db: AsyncSession, *, obj_in: TryOnSessionCreate, user_id: int) -> TryOnSession:
        db_obj = TryOnSession(
            user_id=user_id,
            avatar_media_id=obj_in.avatar_media_id,
            garment_id=obj_in.garment_id,
            status=TryOnStatus.QUEUED,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_sessions(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> List[TryOnSession]:
        result = await db.execute(
            select(TryOnSession)
            .where(TryOnSession.user_id == user_id)
            .order_by(TryOnSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_status(
        self, 
        db: AsyncSession, 
        session_id: int, 
        status: TryOnStatus,
        result_media_id: Optional[int] = None,
        error_text: Optional[str] = None
    ) -> TryOnSession:
        session = await self.get(db, session_id)
        if session:
            session.status = status
            if result_media_id:
                session.result_media_id = result_media_id
            if error_text:
                session.error_text = error_text
            await db.commit()
            await db.refresh(session)
        return session

    async def get_queued_sessions(self, db: AsyncSession, limit: int = 10) -> List[TryOnSession]:
        result = await db.execute(
            select(TryOnSession)
            .where(TryOnSession.status == TryOnStatus.QUEUED)
            .order_by(TryOnSession.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()