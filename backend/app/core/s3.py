from app.infrastructure.storage import s3 as _s3_impl

S3Client = _s3_impl.S3Client
s3_client = _s3_impl.s3_client
boto3 = _s3_impl.boto3
settings = _s3_impl.settings

__all__ = ["S3Client", "s3_client", "boto3", "settings"]
