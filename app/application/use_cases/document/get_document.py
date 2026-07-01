from __future__ import annotations

from app.application.dtos.document import DocumentDetailOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.documents_repository import DocumentRepository
from app.domain.services.document_access_policy import evaluate_document_access


class GetDocumentByIdUseCase:
    """Use case lấy chi tiết document theo ID với kiểm tra access policy."""

    def __init__(self, document_repo: DocumentRepository) -> None:
        self.document_repo = document_repo

    async def execute(self, actor: User, document_id: int) -> DocumentDetailOutput:
        if not actor.is_active:
            raise PermissionDenied("Inactive users cannot view documents")

        document = await self.document_repo.find_by_id(document_id)
        if document is None:
            raise ResourceNotFound(f"Document {document_id} not found")

        allowed = evaluate_document_access(document, actor, departments=None)
        if not allowed:
            raise PermissionDenied("You do not have permission to view this document")

        return DocumentDetailOutput.from_entity(document)
