from typing import Any, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.tryon import TryOnEventType
from app.infrastructure.persistence.models.tryon_event import TryOnEvent

from .base import BaseRepository


class TryOnEventRepository(BaseRepository[TryOnEvent]):
    def __init__(self):
        super().__init__(TryOnEvent)

    async def create_event(
        self,
        db: AsyncSession,
        *,
        session_id: int,
        event_type: TryOnEventType | str,
        attempt: Optional[int] = None,
        error_text: Optional[str] = None,
        details: Optional[str] = None,
    ) -> TryOnEvent:
        return await self.create(
            db,
            obj_in={
                "session_id": session_id,
                "event_type": event_type.value if isinstance(event_type, TryOnEventType) else str(event_type),
                "attempt": attempt,
                "error_text": error_text,
                "details": details,
            },
        )

    async def get_recent_events(self, db: AsyncSession, limit: int = 10) -> List[dict[str, Any]]:
        result = await db.execute(
            select(TryOnEvent).order_by(TryOnEvent.created_at.desc(), TryOnEvent.id.desc()).limit(limit)
        )
        events = result.scalars().all()
        return [
            {
                "id": event.id,
                "session_id": event.session_id,
                "event_type": event.event_type,
                "attempt": event.attempt,
                "error_text": event.error_text,
                "details": event.details,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ]

    async def delete_by_session_ids(self, db: AsyncSession, session_ids: list[int]) -> int:
        if not session_ids:
            return 0

        result = await db.execute(delete(TryOnEvent).where(TryOnEvent.session_id.in_(session_ids)))
        await db.commit()
        return int(result.rowcount or 0)
