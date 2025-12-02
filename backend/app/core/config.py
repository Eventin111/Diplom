from pydantic import BaseSettings, AnyUrl
from typing import List, Optional
import os

class Settings(BaseSettings):
    API_V1: str = "/api/v1"
    SECRET_KEY: str
    DB_URL: AnyUrl

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str 
    S3_BUCKET_NAME: str = "swipeit-media"
    S3_REGION: str = "us-east-1"
    S3_SECURE: bool = False  # True для HTTPS
    # URL для доступа к файлам (может отличаться от endpoint)
    S3_PUBLIC_URL: Optional[str] = None

    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Для async БД
    DB_ASYNC_URL: AnyUrl | None = None
    
    @property
    def async_database_url(self) -> str:
        """Генерирует async URL из обычного"""
        if self.DB_ASYNC_URL:
            return str(self.DB_ASYNC_URL)
        return str(self.DB_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def s3_public_url(self) -> str:
        return self.S3_PUBLIC_URL or self.S3_ENDPOINT

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
        env_file_encoding = "utf-8"

settings = Settings()