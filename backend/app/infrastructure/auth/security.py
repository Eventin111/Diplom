import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.db.db import get_db
from app.infrastructure.persistence.repositories.user_repo import UserRepository


oauth = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1}/auth/login")
oauth_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1}/auth/login", auto_error=False)


def create_token(sub: int, ttl_min: int) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": str(sub), "iat": now, "exp": now + ttl_min * 60},
        settings.SECRET_KEY,
        algorithm="HS256",
    )


async def get_user_by_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user


async def get_current_user(
    token: str = Depends(oauth),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_by_token(token=token, db=db)


async def get_optional_current_user(
    token: str | None = Depends(oauth_optional),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        return None

    try:
        return await get_user_by_token(token=token, db=db)
    except HTTPException:
        return None
