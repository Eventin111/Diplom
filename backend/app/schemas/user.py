from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime
from typing import Optional
import re

class UsernameValidationMixin:
    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError('Username может содержать только буквы, цифры и подчеркивания')
        return v

class UserBase(UsernameValidationMixin, BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен быть не менее 6 символов')
        # Дополнительные проверки сложности пароля
        if v.isnumeric():
            raise ValueError('Пароль не может состоять только из цифр')
        return v

class UserUpdate(UsernameValidationMixin, BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserWithStatsResponse(UserResponse):
    posts_count: int = 0
    likes_count: int = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"