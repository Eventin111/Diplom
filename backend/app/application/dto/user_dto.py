import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UsernameValidationMixin:
    @validator("username", check_fields=False)
    def username_alphanumeric(cls, value):
        if value and not re.match(r"^[a-zA-Z0-9_а-яА-ЯёЁ]+$", value):
            raise ValueError("Username may contain only letters (Latin/Cyrillic), numbers, and underscores")
        return value


class UserBase(UsernameValidationMixin, BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_а-яА-ЯёЁ]+$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

    @validator("password")
    def password_strength(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if value.isnumeric():
            raise ValueError("Password cannot contain only digits")
        return value


class UserUpdate(UsernameValidationMixin, BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_а-яА-ЯёЁ]+$")
    avatar_url: Optional[str] = None
