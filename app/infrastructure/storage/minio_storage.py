from __future__ import annotations

import io
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.domain.exceptions import StorageError, StorageObjectNotFound

class MinioStorageService:
    def __init__ (self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try: 
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except Exception as exc:
            raise RuntimeError(f"Failed to ensure bucket exists: {exc}") from exc
        
    def upload_file(self, object_key: str, file_data: io.BytesIO, length: int, content_type: str) -> str:
        try:
            self.client.put_object(
                bucket_name = self.bucket_name,
                object_name = object_key,
                data = file_data,
                length = length,
                content_type = content_type
            )
            return object_key
        except Exception as exc:
            raise RuntimeError(f"Failed to upload file to MinIO: {exc}") from exc
        
    def delete_file(self, object_key: str) -> None:
        try:
            self.client.remove_object(self.bucket_name, object_key)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                return
            raise StorageError(f"Failed to delete file from MinIO: {exc}") from exc