import boto3
import json
from botocore.exceptions import ClientError
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class S3Client:
    def __init__(self):
        self._client = None
        self._initialized = False
        self.bucket_name = settings.S3_BUCKET_NAME
        # НЕ инициализируем автоматически - только по запросу

    @property
    def client(self):
        """Ленивое получение клиента S3"""
        if self._client is None and not self._initialized:
            self._initialize_client()
        return self._client

    def _initialize_client(self):
        """Попытка инициализации клиента"""
        try:
            self._client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                verify=settings.S3_SECURE
            )
            self._ensure_bucket_exists()
            self._initialized = True
            logger.info("✅ S3 клиент успешно инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ S3 клиент не инициализирован: {e}")
            self._initialized = True  # Помечаем как попытку сделанную
            self._client = None

    def _ensure_bucket_exists(self):
        """Проверка bucket (только если клиент доступен)"""
        if not self._client:
            return
            
        try:
            self._client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ Bucket {self.bucket_name} существует")
        except ClientError:
            try:
                self._client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"✅ Bucket {self.bucket_name} создан")
            except ClientError as e:
                logger.warning(f"⚠️ Не удалось создать bucket: {e}")
        finally:
            self._ensure_public_read_policy()

    def _ensure_public_read_policy(self):
        if not self._client:
            return

        if not hasattr(self._client, "put_bucket_policy"):
            logger.info("ℹ️ Клиент S3 не поддерживает put_bucket_policy, пропускаем настройку policy")
            return

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                }
            ],
        }

        try:
            self._client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(policy),
            )
            logger.info(f"✅ Public-read policy применена для bucket {self.bucket_name}")
        except ClientError as e:
            logger.warning(f"⚠️ Не удалось применить public-read policy: {e}")

    async def upload_file(self, file_content: bytes, file_key: str, content_type: str = "application/octet-stream") -> str:
        """Загрузка файла в S3 (с проверкой доступности)"""
        if not self.client:
            raise Exception("S3 клиент не доступен. Проверьте настройки MinIO.")
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            public_base_url = getattr(settings, "S3_PUBLIC_URL", None) or getattr(settings, "s3_public_url")
            public_url = f"{public_base_url}/{self.bucket_name}/{file_key}"
            logger.info(f"✅ Файл загружен: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла: {e}")
            raise Exception(f"Ошибка загрузки в S3: {e}")

    def get_file(self, file_key: str) -> tuple[bytes, str]:
        """Получить файл из S3/MinIO."""
        if not self.client:
            raise Exception("S3 клиент не доступен. Проверьте настройки MinIO.")

        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            content_type = response.get("ContentType") or "application/octet-stream"
            return response["Body"].read(), content_type
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            raise Exception(f"Ошибка чтения из S3: {e}")

    # ... остальные методы

s3_client = S3Client()
