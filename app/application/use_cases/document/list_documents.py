from __future__ import annotations

from app.application.dtos.document import DocumentListOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.repositories.documents_repository import DocumentRepository
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


class ListDocumentsUseCase:
    """Use case liệt kê document theo scope của actor."""

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

    async def execute(self, actor: User) -> list[DocumentListOutput]:
        if not actor.is_active:
            raise PermissionDenied("Inactive actor cannot list documents.")

        scope = self.rbac_service.get_document_scope(actor)

        if scope == "all":
            documents = await self.document_repo.list_all()
        elif scope == "department" and actor.department_id is not None:
            all_depts = await self.dept_repo.find_all()
            dept_ids = self.dept_tree_service.get_dept_and_descendants(
                actor.department_id, all_depts
            )
            documents = await self.document_repo.list_by_departments(list(dept_ids))
        else:
            documents = await self.document_repo.list_by_owner(actor.id)

        return [DocumentListOutput.from_entity(document) for document in documents]
