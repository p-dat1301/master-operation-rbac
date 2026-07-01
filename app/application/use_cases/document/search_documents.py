from __future__ import annotations

from app.application.dtos.document import DocumentListOutput, DocumentSearchParams
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.repositories.documents_repository import DocumentRepository
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


class SearchDocumentsUseCase:
    """Use case tìm kiếm document theo scope của actor."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        dept_repo: DepartmentRepository,
        rbac_service: RBACService,
        dept_tree_service: DepartmentTreeService,
    ) -> None:
        self.document_repo = document_repo
        self.dept_repo = dept_repo
        self.rbac_service = rbac_service
        self.dept_tree_service = dept_tree_service

    async def execute(
        self,
        actor: User,
        query: DocumentSearchParams,
    ) -> list[DocumentListOutput]:
        if not actor.is_active:
            raise PermissionDenied("Inactive actor cannot search documents.")

        keyword = query.q or ""
        scope = self.rbac_service.get_document_scope(actor)

        if scope == "all":
            documents = await self.document_repo.search(keyword, dept_ids=None)
        elif scope == "department" and actor.department_id is not None:
            all_depts = await self.dept_repo.find_all()
            dept_ids = self.dept_tree_service.get_dept_and_descendants(
                actor.department_id, all_depts
            )
            documents = await self.document_repo.search(keyword, list(dept_ids))
        else:
            dept_ids = [actor.department_id] if actor.department_id is not None else []
            documents = await self.document_repo.search(keyword, dept_ids)

        return [DocumentListOutput.from_entity(document) for document in documents]
