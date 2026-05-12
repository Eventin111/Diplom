from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models.follow import FollowRelation
from app.infrastructure.persistence.models.user import User

from .base import BaseRepository


class FollowRepository(BaseRepository[FollowRelation]):
    def __init__(self):
        super().__init__(FollowRelation)

    async def is_following(self, db: AsyncSession, *, follower_id: int, following_id: int) -> bool:
        result = await db.execute(
            select(FollowRelation.id).where(
                FollowRelation.follower_id == follower_id,
                FollowRelation.following_id == following_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def follow(self, db: AsyncSession, *, follower_id: int, following_id: int) -> FollowRelation | None:
        if follower_id == following_id:
            return None

        result = await db.execute(
            select(FollowRelation).where(
                FollowRelation.follower_id == follower_id,
                FollowRelation.following_id == following_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        follow = FollowRelation(follower_id=follower_id, following_id=following_id)
        db.add(follow)
        await db.commit()
        await db.refresh(follow)
        return follow

    async def unfollow(self, db: AsyncSession, *, follower_id: int, following_id: int) -> bool:
        result = await db.execute(
            delete(FollowRelation).where(
                FollowRelation.follower_id == follower_id,
                FollowRelation.following_id == following_id,
            )
        )
        await db.commit()
        return bool(result.rowcount)

    async def get_followers_count(self, db: AsyncSession, *, user_id: int) -> int:
        result = await db.execute(select(func.count(FollowRelation.id)).where(FollowRelation.following_id == user_id))
        return int(result.scalar() or 0)

    async def get_following_count(self, db: AsyncSession, *, user_id: int) -> int:
        result = await db.execute(select(func.count(FollowRelation.id)).where(FollowRelation.follower_id == user_id))
        return int(result.scalar() or 0)

    async def list_following_users(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 30,
    ) -> tuple[list[User], int]:
        total_result = await db.execute(
            select(func.count(FollowRelation.id)).where(FollowRelation.follower_id == user_id)
        )
        total = int(total_result.scalar() or 0)

        rows = await db.execute(
            select(User)
            .join(FollowRelation, FollowRelation.following_id == User.id)
            .where(FollowRelation.follower_id == user_id)
            .order_by(FollowRelation.created_at.desc(), FollowRelation.id.desc())
            .offset(max(0, skip))
            .limit(max(1, min(limit, 500)))
        )
        return rows.scalars().all(), total

    async def list_followers_users(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 30,
    ) -> tuple[list[User], int]:
        total_result = await db.execute(
            select(func.count(FollowRelation.id)).where(FollowRelation.following_id == user_id)
        )
        total = int(total_result.scalar() or 0)

        rows = await db.execute(
            select(User)
            .join(FollowRelation, FollowRelation.follower_id == User.id)
            .where(FollowRelation.following_id == user_id)
            .order_by(FollowRelation.created_at.desc(), FollowRelation.id.desc())
            .offset(max(0, skip))
            .limit(max(1, min(limit, 500)))
        )
        return rows.scalars().all(), total
