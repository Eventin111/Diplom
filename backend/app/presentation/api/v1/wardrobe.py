from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.garment_dto import GarmentCreate
from app.application.dto.wardrobe_dto import WardrobeItemCreate
from app.core.config import settings
from app.infrastructure.auth.security import get_current_user
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.repositories.garment_repo import GarmentRepository
from app.infrastructure.persistence.repositories.wardrobe_repo import WardrobeRepository
from app.presentation.api.schemas.user import UserResponse
from app.presentation.api.schemas.wardrobe import (
    WardrobeItemResponse,
    WardrobeListResponse,
    WardrobeSaveFromPost,
)

router = APIRouter()


def _build_media_file_url(media_id: int | None) -> str | None:
    if media_id is None:
        return None
    return f"{settings.API_V1}/media/{media_id}/file"


def _serialize_wardrobe_item(item) -> WardrobeItemResponse:
    garment = item.garment
    metadata = garment.garment_metadata or {}
    image_url = _build_media_file_url(garment.media_id) or metadata.get("image_url")
    return WardrobeItemResponse(
        id=item.id,
        user_id=item.user_id,
        garment_id=item.garment_id,
        created_at=item.created_at,
        garment={
            "id": garment.id,
            "title": garment.title,
            "brand": garment.brand,
            "media_id": garment.media_id,
            "image_url": image_url,
            "category": metadata.get("category"),
            "price": metadata.get("price"),
            "source_post_id": metadata.get("post_id"),
            "created_at": garment.created_at,
        },
    )


@router.get("/", response_model=WardrobeListResponse)
async def get_wardrobe(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wardrobe_repo = WardrobeRepository()
    items = await wardrobe_repo.get_user_items(db, user_id=current_user.id, skip=skip, limit=limit)
    return WardrobeListResponse(items=[_serialize_wardrobe_item(item) for item in items])


@router.get("/garment-ids")
async def get_saved_garment_ids(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wardrobe_repo = WardrobeRepository()
    items = await wardrobe_repo.get_user_items(db, user_id=current_user.id, skip=0, limit=2000)
    return {"items": [item.garment_id for item in items]}


@router.post("/", response_model=WardrobeItemResponse)
async def add_wardrobe_item(
    payload: WardrobeSaveFromPost,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    garment_repo = GarmentRepository()
    wardrobe_repo = WardrobeRepository()

    if payload.post_id:
        existing_items = await wardrobe_repo.get_user_items(db, user_id=current_user.id, skip=0, limit=2000)
        for item in existing_items:
            metadata = item.garment.garment_metadata or {}
            if int(metadata.get("post_id") or 0) == int(payload.post_id):
                return _serialize_wardrobe_item(item)

    garment = await garment_repo.create(
        db,
        obj_in=GarmentCreate(
            title=payload.title,
            brand=payload.brand,
            media_id=None,
            garment_metadata={
                "image_url": payload.image_url,
                "category": payload.category,
                "price": payload.price,
                "post_id": payload.post_id,
            },
        ),
    )
    item = await wardrobe_repo.create(db, obj_in=WardrobeItemCreate(garment_id=garment.id), user_id=current_user.id)
    return _serialize_wardrobe_item(item)


@router.post("/{garment_id}", response_model=WardrobeItemResponse)
async def save_existing_garment_to_wardrobe(
    garment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    garment_repo = GarmentRepository()
    wardrobe_repo = WardrobeRepository()
    garment = await garment_repo.get(db, garment_id)
    if garment is None:
        raise HTTPException(status_code=404, detail="Одежда не найдена")

    item = await wardrobe_repo.create(db, obj_in=WardrobeItemCreate(garment_id=garment_id), user_id=current_user.id)
    return _serialize_wardrobe_item(item)


@router.delete("/{garment_id}")
async def remove_wardrobe_item(
    garment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wardrobe_repo = WardrobeRepository()
    deleted = await wardrobe_repo.delete_by_user_and_garment(db, user_id=current_user.id, garment_id=garment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Вещь не найдена в гардеробе")
    return {"message": "Вещь удалена из гардероба"}
