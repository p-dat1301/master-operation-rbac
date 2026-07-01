from __future__ import annotations

from app.application.dtos.document import DocumentDetailOutput, DocumentUpdateInput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.documents_repository import DocumentRepository
from app.domain.services.document_access_policy import evaluate_document_access
from app.domain.services.rbac_service import RBACService


class UpdateDocumentUseCase:
    """Use case cập nhật metadata document với kiểm tra RBAC + access policy."""

    def __init__(self, document_repo: DocumentRepository, rbac_service: RBACService) -> None:
        self.document_repo = document_repo
        self.rbac_service = rbac_service

    async def execute(
        self,
        actor: User,
        document_id: int,
        payload: DocumentUpdateInput,
    ) -> DocumentDetailOutput:
        if not actor.is_active:
            raise PermissionDenied("Inactive users cannot update documents")

        self.rbac_service.require_permission(actor, "update_document")

        document = await self.document_repo.find_by_id(document_id)
        if document is None:
            raise ResourceNotFound(f"Document {document_id} not found")

        allowed = evaluate_document_access(document, actor, departments=None)
        if not allowed:
            raise PermissionDenied("You do not have permission to update this document")

        update_data = {k: v for k, v in payload.model_dump(exclude_none=True).items() if v is not None}
        updated_document = await self.document_repo.update(document_id, update_data)

        if updated_document is None:
            raise ResourceNotFound(f"Document {document_id} not found")

        return DocumentDetailOutput.from_entity(updated_document)
