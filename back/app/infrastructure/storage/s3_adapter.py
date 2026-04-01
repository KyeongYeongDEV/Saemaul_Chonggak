import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class S3Adapter:
    """AWS S3 파일 업로드 Adapter."""

    def __init__(self):
        self._client = None
        try:
            import boto3
            from app.core.config import settings
            self._client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self._bucket = settings.AWS_S3_BUCKET
            self._region = settings.AWS_REGION
        except Exception:
            logger.warning("S3 not configured — file upload disabled.")

    async def upload(self, file_bytes: bytes, content_type: str, ext: str) -> str:
        """파일 업로드 후 URL 반환."""
        if self._client is None:
            return f"https://placeholder.example.com/{uuid.uuid4()}.{ext}"
        key = f"uploads/{uuid.uuid4()}.{ext}"
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=file_bytes, ContentType=content_type
        )
        return f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{key}"
