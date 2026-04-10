from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.tryon_session_dto import TryOnSessionCreate
from app.domain.enums.tryon import TryOnStatus
from app.infrastructure.persistence.models.tryon import TryOnSession

from .base import BaseRepository

_UNSET = object()


class TryOnRepository(BaseRepository[TryOnSession]):
    def __init__(self):
        super().__init__(TryOnSession)

    async def create(self, db: AsyncSession, *, obj_in: TryOnSessionCreate, user_id: int) -> TryOnSession:
        db_obj = TryOnSession(
            user_id=user_id,
            avatar_media_id=obj_in.avatar_media_id,
            cloth_media_id=obj_in.cloth_media_id,
            garment_id=obj_in.garment_id,
            status=TryOnStatus.QUEUED,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_sessions(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[TryOnSession]:
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
        result_media_id: Optional[int] | object = _UNSET,
        error_text: Optional[str] | object = _UNSET,
    ) -> TryOnSession:
        session = await self.get(db, session_id)
        if session:
            session.status = status
            if result_media_id is not _UNSET:
                session.result_media_id = result_media_id
            if error_text is not _UNSET:
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

    async def get_status_counts(self, db: AsyncSession) -> dict[str, int]:
        result = await db.execute(
            select(TryOnSession.status, func.count(TryOnSession.id)).group_by(TryOnSession.status)
        )
        counts = {status.value: 0 for status in TryOnStatus}
        for status_value, count in result.all():
            normalized_status = status_value.value if isinstance(status_value, TryOnStatus) else str(status_value)
            counts[normalized_status] = int(count)
        return counts

    async def get_recent_failures(self, db: AsyncSession, limit: int = 5) -> List[dict[str, Any]]:
        result = await db.execute(
            select(TryOnSession)
            .where(TryOnSession.status == TryOnStatus.FAILED)
            .order_by(TryOnSession.updated_at.desc(), TryOnSession.created_at.desc())
            .limit(limit)
        )
        sessions = result.scalars().all()
        return [
            {
                "session_id": session.id,
                "user_id": session.user_id,
                "error_text": session.error_text,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            }
            for session in sessions
        ]

    async def get_stale_processing_sessions(self, db: AsyncSession, older_than: datetime) -> List[TryOnSession]:
        result = await db.execute(
            select(TryOnSession)
            .where(TryOnSession.status == TryOnStatus.PROCESSING)
            .where(
                or_(
                    TryOnSession.updated_at <= older_than,
                    (TryOnSession.updated_at.is_(None) & (TryOnSession.created_at <= older_than)),
                )
            )
            .order_by(TryOnSession.created_at.asc())
        )
        return result.scalars().all()

    async def get_cleanup_candidates(
        self,
        db: AsyncSession,
        *,
        older_than: datetime,
        limit: int,
    ) -> List[TryOnSession]:
        result = await db.execute(
            select(TryOnSession)
            .where(TryOnSession.status.in_([TryOnStatus.COMPLETED, TryOnStatus.FAILED, TryOnStatus.CANCELED]))
            .where(
                or_(
                    TryOnSession.updated_at <= older_than,
                    (TryOnSession.updated_at.is_(None) & (TryOnSession.created_at <= older_than)),
                )
            )
            .order_by(TryOnSession.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_many(self, db: AsyncSession, session_ids: list[int]) -> int:
        if not session_ids:
            return 0

        result = await db.execute(delete(TryOnSession).where(TryOnSession.id.in_(session_ids)))
        await db.commit()
        return int(result.rowcount or 0)
