from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.application.dto.user_dto import UserBase, UserCreate, UserUpdate

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithStatsResponse",
    "ProfileStatsResponse",
    "UserLogin",
    "Token",
]


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserWithStatsResponse(UserResponse):
    posts_count: int = 0
    likes_count: int = 0


class ProfileStatsResponse(BaseModel):
    tryons_count: int = 0
    likes_count: int = 0
    posts_count: int = 0
    wardrobe_count: int = 0
    followers_count: int = 0
    following_count: int = 0


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
