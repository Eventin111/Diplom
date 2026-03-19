import json
import logging

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        self._client = None
        self._initialized = False
        self.bucket_name = settings.S3_BUCKET_NAME

    @property
    def client(self):
        if self._client is None and not self._initialized:
            self._initialize_client()
        return self._client

    def _initialize_client(self):
        try:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                verify=settings.S3_SECURE,
            )
            self._ensure_bucket_exists()
            self._initialized = True
            logger.info("S3 client initialized")
        except Exception as exc:
            logger.warning("S3 client is unavailable: %s", exc)
            self._initialized = True
            self._client = None

    def _ensure_bucket_exists(self):
        if not self._client:
            return

        try:
            self._client.head_bucket(Bucket=self.bucket_name)
            logger.info("Bucket %s exists", self.bucket_name)
        except ClientError:
            try:
                self._client.create_bucket(Bucket=self.bucket_name)
                logger.info("Bucket %s created", self.bucket_name)
            except ClientError as exc:
                logger.warning("Failed to create bucket %s: %s", self.bucket_name, exc)
        finally:
            self._ensure_public_read_policy()

    def _ensure_public_read_policy(self):
        if not self._client or not hasattr(self._client, "put_bucket_policy"):
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
            self._client.put_bucket_policy(Bucket=self.bucket_name, Policy=json.dumps(policy))
            logger.info("Public read policy applied to bucket %s", self.bucket_name)
        except ClientError as exc:
            logger.warning("Failed to apply bucket policy: %s", exc)

    async def upload_file(
        self,
        file_content: bytes,
        file_key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        if not self.client:
            raise Exception("S3 client is unavailable")

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ACL="public-read",
            )
            public_base_url = getattr(settings, "S3_PUBLIC_URL", None) or getattr(settings, "s3_public_url")
            public_url = f"{public_base_url}/{self.bucket_name}/{file_key}"
            logger.info("Uploaded file: %s", public_url)
            return public_url
        except Exception as exc:
            logger.error("Failed to upload file %s: %s", file_key, exc)
            raise Exception(f"S3 upload failed: {exc}")

    def get_file(self, file_key: str) -> tuple[bytes, str]:
        if not self.client:
            raise Exception("S3 client is unavailable")

        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            content_type = response.get("ContentType") or "application/octet-stream"
            return response["Body"].read(), content_type
        except Exception as exc:
            logger.error("Failed to read file %s: %s", file_key, exc)
            raise Exception(f"S3 read failed: {exc}")

    def delete_file(self, file_key: str) -> bool:
        if not self.client:
            return False

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except Exception as exc:
            logger.warning("Failed to delete file %s: %s", file_key, exc)
            return False


s3_client = S3Client()
