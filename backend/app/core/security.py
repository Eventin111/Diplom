import time
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db

oauth = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1}/auth/login")

def create_token(sub: int, ttl_min: int) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": str(sub), "iat": now, "exp": now + ttl_min * 60},
        settings.SECRET_KEY,
        algorithm="HS256"
    )

async def get_current_user(
    token: str = Depends(oauth),
    db: AsyncSession = Depends(get_db)
):
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
    
    from app.repositories.user_repo import UserRepository
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user