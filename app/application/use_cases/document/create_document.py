from __future__ import annotations

import io
import uuid

from app.domain.entities.document import Document, DocumentVisibility, DocumentClassification, DocumentStatus
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, BusinessRuleViolation
from app.domain.repositories.documents_repository import DocumentRepository
from app.application.dtos.document import DocumentCreateInput, DocumentOutput
from app.infrastructure.storage.minio_storage import MinioStorageService
from app.domain.services.rbac_service import RBACService


class CreateDocumentUsecase:
    """Use case tạo document và tải file gốc lên hệ thống lưu trữ MinIO."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        storage_service: MinioStorageService,
        rbac_service: RBACService,
    ) -> None:
        self.document_repo = document_repo
        self.storage_service = storage_service
        self.rbac_service = rbac_service

    async def execute(
        self,
        actor: User,
        data: DocumentCreateInput,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentOutput:
        # 1. Kiểm tra quyền tải tài liệu
        self.rbac_service.require_permission(actor, "upload_document")

        # 2. Kiểm tra nghiệp vụ phạm vi quyền xem (Visibility Scope)
        if data.visibility_scope == DocumentVisibility.ROLE and not data.allowed_role_names:
            raise BusinessRuleViolation(
                "Phạm vi quyền xem theo Vai trò yêu cầu danh sách 'allowed_role_names' không được để trống."
            )
        if data.visibility_scope == DocumentVisibility.DEPARTMENT and not data.allowed_departments:
            raise BusinessRuleViolation(
                "Phạm vi quyền xem theo Phòng ban yêu cầu danh sách 'allowed_departments' không được để trống."
            )

        # 3. Upload file gốc vào MinIO
        unique_id = uuid.uuid4()
        object_key = f"documents/{unique_id}/{filename}"
        
        try:
            self.storage_service.upload_file(
                object_key=object_key,
                file_data=io.BytesIO(file_bytes),
                length=len(file_bytes),
                content_type=mime_type,
            )
        except Exception as exc:
            raise BusinessRuleViolation(f"Không thể tải file lên hệ thống lưu trữ: {exc}") from exc

        # 4. Khởi tạo Document Entity
        document_entity = Document(
            id=0,
            title=data.title,
            description=data.description,
            store_bucket=self.storage_service.bucket_name,
            store_object_key=object_key,
            path_filename=filename,
            size_byte=len(file_bytes),
            status=DocumentStatus.UPLOADED,
            uploaded_by=actor.id,
            visibility_scope=data.visibility_scope,
            allowed_role_names=set(data.allowed_role_names),
            allowed_departments=set(data.allowed_departments),
            class_document=data.class_document,
        )

        # 5. Lưu CSDL và rollback xóa file MinIO nếu DB lỗi
        try:
            created = await self.document_repo.create(document_entity)
        except Exception as db_exc:
            try:
                self.storage_service.delete_file(object_key)
            except Exception:
                pass
            raise db_exc

        return DocumentOutput.from_entity(created)

    async def excute(
        self,
        actor: User,
        data: DocumentCreateInput,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentOutput:
        """Bypass alias hỗ trợ lỗi chính tả từ giao diện gọi cũ."""
        return await self.execute(actor, data, file_bytes, filename, mime_type)
