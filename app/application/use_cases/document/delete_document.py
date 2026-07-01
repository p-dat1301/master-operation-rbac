from __future__ import annotations

import logging

from app.application.dtos.document import DocumentDetailOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound, StorageObjectNotFound
from app.domain.repositories.documents_repository import DocumentRepository
from app.domain.services.document_access_policy import evaluate_document_access
from app.domain.services.rbac_service import RBACService
from app.infrastructure.storage.minio_storage import MinioStorageService

logger = logging.getLogger(__name__)


class DeleteDocumentUseCase:
    """Use case xóa cứng document với cleanup object storage."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        storage_service: MinioStorageService,
        rbac_service: RBACService,
    ) -> None:
        self.document_repo = document_repo
        self.storage_service = storage_service
        self.rbac_service = rbac_service

    async def execute(self, actor: User, document_id: int) -> DocumentDetailOutput:
        if not actor.is_active:
            raise PermissionDenied("Inactive users cannot delete documents")

        self.rbac_service.require_permission(actor, "delete_document")

        document = await self.document_repo.find_by_id(document_id)
        if document is None:
            raise ResourceNotFound(f"Document {document_id} not found")

        allowed = evaluate_document_access(document, actor, departments=None)
        if not allowed:
            raise PermissionDenied("You do not have permission to delete this document")

        try:
            self.storage_service.delete_file(document.store_object_key)
        except StorageObjectNotFound as exc:
            logger.warning("Ignoring MinIO delete error for document %s: %s", document_id, exc)

        deleted_document = await self.document_repo.delete(document_id)
        if deleted_document is None:
            raise ResourceNotFound(f"Document {document_id} not found")

        return DocumentDetailOutput.from_entity(deleted_document)
