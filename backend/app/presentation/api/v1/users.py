from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.auth.security import get_current_user, get_optional_current_user
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.models.comment import Comment
from app.infrastructure.persistence.models.feed import FeedItem
from app.infrastructure.persistence.models.follow import FollowRelation
from app.infrastructure.persistence.models.likes import Like
from app.infrastructure.persistence.repositories.feed_repo import FeedRepository
from app.infrastructure.persistence.repositories.follow_repo import FollowRepository
from app.infrastructure.persistence.repositories.user_repo import UserRepository
from app.presentation.api.schemas.public_profile import (
    PublicPostItem,
    PublicProfileResponse,
    PublicRelationListResponse,
    PublicRelationUserItem,
)
from app.presentation.api.schemas.user import UserResponse

router = APIRouter()


def _build_media_file_url(media_id: int | None) -> str | None:
    if media_id is None:
        return None
    return f"{settings.API_V1}/media/{media_id}/file"


@router.get("/{username}/profile", response_model=PublicProfileResponse)
async def get_public_profile(
    username: str,
    limit: int = 24,
    current_user: UserResponse | None = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository()
    feed_repo = FeedRepository()

    user = await user_repo.get_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    stats_payload = await user_repo.get_with_stats(db, user.id)
    stats = stats_payload["stats"] if stats_payload else {"posts_count": 0, "likes_count": 0, "wardrobe_count": 0}
    likes_total_result = await db.execute(
        select(func.count(Like.id)).join(FeedItem, FeedItem.id == Like.feed_item_id).where(FeedItem.user_id == user.id)
    )
    likes_total = int(likes_total_result.scalar() or 0)

    feed_items = await feed_repo.get_user_feed(db, user_id=user.id, skip=0, limit=max(1, min(limit, 100)))
    feed_ids = [item.id for item in feed_items]
    likes_map: dict[int, int] = {}
    comments_map: dict[int, int] = {}
    if feed_ids:
        likes_rows = await db.execute(
            select(Like.feed_item_id, func.count(Like.id))
            .where(Like.feed_item_id.in_(feed_ids))
            .group_by(Like.feed_item_id)
        )
        likes_map = {int(feed_id): int(count or 0) for feed_id, count in likes_rows.all()}
        comments_rows = await db.execute(
            select(Comment.feed_item_id, func.count(Comment.id))
            .where(Comment.feed_item_id.in_(feed_ids))
            .group_by(Comment.feed_item_id)
        )
        comments_map = {int(feed_id): int(count or 0) for feed_id, count in comments_rows.all()}

    posts: list[PublicPostItem] = []
    for item in feed_items:
        media_id = item.garment.media_id if item.garment else None
        metadata = item.garment.garment_metadata if item.garment else {}
        image_url = _build_media_file_url(media_id) or (metadata or {}).get("image_url")
        hashtags_raw = (metadata or {}).get("hashtags") if isinstance(metadata, dict) else []
        hashtags = [str(tag).strip().lstrip("#") for tag in (hashtags_raw or []) if str(tag).strip()]
        posts.append(
            PublicPostItem(
                feed_item_id=item.id,
                caption=item.caption,
                image_url=image_url,
                likes_count=likes_map.get(item.id, 0),
                comments_count=comments_map.get(item.id, 0),
                created_at=item.created_at,
                source_post_id=(metadata or {}).get("source_post_id"),
                source_type=(metadata or {}).get("source_type"),
                hashtags=hashtags,
            )
        )

    follow_repo = FollowRepository()
    is_following = False
    if current_user and current_user.id != user.id:
        is_following = await follow_repo.is_following(db, follower_id=current_user.id, following_id=user.id)

    return PublicProfileResponse(
        user_id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        status=user.status,
        posts_count=int(stats.get("posts_count", 0) or 0),
        likes_count=likes_total,
        wardrobe_count=int(stats.get("wardrobe_count", 0) or 0),
        followers_count=int(stats.get("followers_count", 0) or 0),
        following_count=int(stats.get("following_count", 0) or 0),
        is_following=is_following,
        posts=posts,
    )


@router.post("/{username}/follow")
async def follow_user(
    username: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository()
    follow_repo = FollowRepository()
    target = await user_repo.get_by_username(db, username=username)
    if target is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на самого себя")

    await follow_repo.follow(db, follower_id=current_user.id, following_id=target.id)
    return {"success": True}


@router.delete("/{username}/follow")
async def unfollow_user(
    username: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository()
    follow_repo = FollowRepository()
    target = await user_repo.get_by_username(db, username=username)
    if target is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя отписаться от самого себя")

    await follow_repo.unfollow(db, follower_id=current_user.id, following_id=target.id)
    return {"success": True}


@router.get("/{username}/following", response_model=PublicRelationListResponse)
async def get_user_following(
    username: str,
    skip: int = 0,
    limit: int = 60,
    current_user: UserResponse | None = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository()
    follow_repo = FollowRepository()

    target = await user_repo.get_by_username(db, username=username)
    if target is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    following_users, total = await follow_repo.list_following_users(
        db,
        user_id=target.id,
        skip=max(0, skip),
        limit=max(1, min(limit, 500)),
    )

    following_ids = [int(item.id) for item in following_users]
    followed_by_current: set[int] = set()
    if current_user and following_ids:
        followed_rows = await db.execute(
            select(FollowRelation.following_id).where(
                FollowRelation.follower_id == current_user.id,
                FollowRelation.following_id.in_(following_ids),
            )
        )
        followed_by_current = {int(user_id) for (user_id,) in followed_rows.all()}

    items = [
        PublicRelationUserItem(
            user_id=int(item.id),
            username=str(item.username),
            avatar_url=item.avatar_url,
            is_following=int(item.id) in followed_by_current,
        )
        for item in following_users
    ]
    return PublicRelationListResponse(items=items, total=total)
