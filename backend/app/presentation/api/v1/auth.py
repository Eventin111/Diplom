from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.auth.security import create_token, get_current_user
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.repositories.user_repo import UserRepository
from app.presentation.api.schemas.user import ProfileStatsResponse, Token, UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    user_repo = UserRepository()

    # Проверяем, не существует ли уже пользователь с таким email или username
    existing_user = await user_repo.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    existing_user = await user_repo.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким username уже существует"
        )

    # Создаем пользователя
    user = await user_repo.create(db, obj_in=user_data)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Аутентификация пользователя"""
    user_repo = UserRepository()

    # Используем username как email (для совместимости со Swagger UI)
    user = await user_repo.authenticate(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token(sub=user.id, ttl_min=60)

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate, current_user: UserResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Обновить профиль текущего пользователя"""
    user_repo = UserRepository()

    if user_data.email and user_data.email != current_user.email:
        existing_by_email = await user_repo.get_by_email(db, user_data.email)
        if existing_by_email and existing_by_email.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует"
            )

    if user_data.username and user_data.username != current_user.username:
        existing_by_username = await user_repo.get_by_username(db, user_data.username)
        if existing_by_username and existing_by_username.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким username уже существует"
            )

    updated_user = await user_repo.update(db, db_obj=current_user, obj_in=user_data)
    return updated_user


@router.get("/me/stats", response_model=ProfileStatsResponse)
async def get_me_stats(current_user: UserResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Получить статистику текущего пользователя для профиля."""
    user_repo = UserRepository()
    payload = await user_repo.get_with_stats(db, user_id=current_user.id)
    if not payload:
        return ProfileStatsResponse()
    return ProfileStatsResponse(**payload["stats"])
