from __future__ import annotations

from pathlib import Path

from config.settings import get_settings


class S3Storage:
    """S3-compatible object storage (AWS S3, Cloudflare R2, MinIO, GCS S3 API)."""

    name = "s3"

    def __init__(self) -> None:
        self.settings = get_settings()

    def configured(self) -> bool:
        s = self.settings
        return bool(s.storage_bucket and s.storage_access_key and s.storage_secret_key)

    def _client(self):
        import boto3

        s = self.settings
        kwargs: dict = {
            "service_name": "s3",
            "aws_access_key_id": s.storage_access_key,
            "aws_secret_access_key": s.storage_secret_key,
            "region_name": s.storage_region or "auto",
        }
        if s.storage_endpoint:
            kwargs["endpoint_url"] = s.storage_endpoint
        return boto3.client(**kwargs)

    def put_file(self, key: str, path: str, content_type: str = "application/octet-stream") -> str:
        if not self.configured():
            raise RuntimeError("S3/R2 storage yapılandırılmamış (STORAGE_BUCKET / keys)")
        client = self._client()
        extra = {"ContentType": content_type}
        client.upload_file(path, self.settings.storage_bucket, key, ExtraArgs=extra)
        return self.public_url(key)

    def public_url(self, key: str) -> str:
        s = self.settings
        if s.storage_public_base_url:
            return f"{s.storage_public_base_url.rstrip('/')}/{key}"
        if s.storage_endpoint:
            return f"{s.storage_endpoint.rstrip('/')}/{s.storage_bucket}/{key}"
        region = s.storage_region or "us-east-1"
        return f"https://{s.storage_bucket}.s3.{region}.amazonaws.com/{key}"
