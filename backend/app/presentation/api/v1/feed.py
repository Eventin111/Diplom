from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.auth.security import get_current_user
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.repositories.feed_repo import FeedRepository
from app.infrastructure.persistence.repositories.like_repo import LikeRepository
from app.presentation.api.schemas.feed import FeedItemCreate, FeedItemResponse, FeedItemWithStats, FeedPagination
from app.presentation.api.schemas.social import LikeCreate, LikeResponse
from app.presentation.api.schemas.user import UserResponse

router = APIRouter()


@router.post("/", response_model=FeedItemResponse)
async def create_feed_item(
    feed_data: FeedItemCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать пост в ленте"""
    feed_repo = FeedRepository()
    feed_item = await feed_repo.create(db, obj_in=feed_data, user_id=current_user.id)
    return feed_item


@router.get("/", response_model=FeedPagination)
async def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить ленту постов"""
    feed_repo = FeedRepository()
    feed_with_stats = await feed_repo.get_feed_with_stats(db, current_user_id=current_user.id, skip=skip, limit=limit)

    items = []
    for item_data in feed_with_stats:
        items.append(
            FeedItemWithStats(
                **item_data["feed_item"].__dict__,
                likes_count=item_data["likes_count"],
                is_liked=item_data["is_liked"],
                comments_count=0,  # Пока нет комментариев
            )
        )

    return FeedPagination(
        items=items, next_cursor=str(skip + limit) if len(items) == limit else None, has_more=len(items) == limit
    )


@router.post("/{feed_item_id}/like", response_model=LikeResponse)
async def like_feed_item(
    feed_item_id: int, current_user: UserResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Лайкнуть пост"""
    like_repo = LikeRepository()
    like_data = LikeCreate(feed_item_id=feed_item_id)
    like = await like_repo.create(db, obj_in=like_data, user_id=current_user.id)
    return like


@router.get("/liked-ids")
async def get_liked_feed_item_ids(
    current_user: UserResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Получить id постов, которые текущий пользователь лайкнул."""
    like_repo = LikeRepository()
    likes = await like_repo.get_user_likes(db, user_id=current_user.id, limit=500)
    return {"items": [like.feed_item_id for like in likes]}


@router.delete("/{feed_item_id}/like")
async def unlike_feed_item(
    feed_item_id: int, current_user: UserResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Убрать лайк с поста"""
    like_repo = LikeRepository()
    success = await like_repo.delete_by_user_and_feed_item(db, user_id=current_user.id, feed_item_id=feed_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Лайк не найден")
    return {"message": "Лайк удален"}
