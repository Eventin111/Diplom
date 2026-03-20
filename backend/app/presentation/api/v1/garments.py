from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.auth.security import get_current_user
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.repositories.garment_repo import GarmentRepository
from app.presentation.api.schemas.garment import GarmentCreate, GarmentResponse, GarmentUpdate
from app.presentation.api.schemas.user import UserResponse

router = APIRouter()

@router.post("/", response_model=GarmentResponse)
async def create_garment(
    garment_data: GarmentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую одежду"""
    print(f"📦 Received garment data: {garment_data.dict()}")
    print(f"👤 Current user: {current_user.id}")
    
    garment_repo = GarmentRepository()
    garment = await garment_repo.create(db, obj_in=garment_data)
    
    print(f"✅ Created garment: {garment.id}")
    return garment

@router.get("/{garment_id}", response_model=GarmentResponse)
async def get_garment(
    garment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию об одежде"""
    garment_repo = GarmentRepository()
    garment = await garment_repo.get(db, garment_id)
    if not garment:
        raise HTTPException(status_code=404, detail="Одежда не найдена")
    return garment

@router.get("/", response_model=list[GarmentResponse])
async def get_garments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список одежды"""
    garment_repo = GarmentRepository()
    garments = await garment_repo.get_multi(db, skip=skip, limit=limit)
    return garments
