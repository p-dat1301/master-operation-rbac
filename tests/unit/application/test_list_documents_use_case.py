import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.document.list_documents import ListDocumentsUseCase
from app.domain.entities.department import Department
from app.domain.entities.document import Document, DocumentClassification, DocumentStatus, DocumentVisibility
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


def make_actor(role_name: str, *, is_active: bool = True, department_id: int | None = 1, user_id: int = 1) -> User:
    return User(
        id=user_id,
        employee_code=f"EMP{user_id:03d}",
        email=f"user{user_id}@company.vn",
        full_name=f"User {user_id}",
        role_name=role_name,
        department_id=department_id,
        is_active=is_active,
        permissions={"read_document"},
    )


def make_document(document_id: int, *, department_id: int, uploaded_by: int) -> Document:
    now = datetime.now(timezone.utc)
    return Document(
        id=document_id,
        title=f"Doc {document_id}",
        description=f"Document {document_id}",
        store_bucket="bucket",
        store_object_key=f"documents/{document_id}.pdf",
        path_filename=f"doc-{document_id}.pdf",
        size_byte=123,
        status=DocumentStatus.UPLOADED,
        uploaded_by=uploaded_by,
        visibility_scope=DocumentVisibility.DEPARTMENT,
        allowed_role_names=set(),
        allowed_departments={department_id},
        class_document=DocumentClassification.INTERNAL,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_list_documents_inactive_actor_denied():
    document_repo = AsyncMock()
    dept_repo = AsyncMock()
    rbac_service = MagicMock(spec=RBACService)
    dept_tree_service = DepartmentTreeService()
    use_case = ListDocumentsUseCase(document_repo, dept_repo, rbac_service, dept_tree_service)

    actor = make_actor("employee", is_active=False)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor)


@pytest.mark.asyncio
async def test_list_documents_admin_all():
    document_repo = AsyncMock()
    dept_repo = AsyncMock()
    rbac_service = MagicMock(spec=RBACService)
    rbac_service.get_document_scope.return_value = "all"
    dept_tree_service = DepartmentTreeService()
    use_case = ListDocumentsUseCase(document_repo, dept_repo, rbac_service, dept_tree_service)

    docs = [make_document(1, department_id=1, uploaded_by=10), make_document(2, department_id=2, uploaded_by=11)]
    document_repo.list_all.return_value = docs
    actor = make_actor("admin", department_id=None, user_id=100)

    result = await use_case.execute(actor)

    document_repo.list_all.assert_awaited_once()
    dept_repo.find_all.assert_not_awaited()
    document_repo.list_by_departments.assert_not_awaited()
    document_repo.list_by_owner.assert_not_awaited()
    assert [item.id for item in result] == [1, 2]


@pytest.mark.asyncio
async def test_list_documents_manager_department_and_descendants():
    document_repo = AsyncMock()
    dept_repo = AsyncMock()
    rbac_service = MagicMock(spec=RBACService)
    rbac_service.get_document_scope.return_value = "department"
    dept_tree_service = DepartmentTreeService()
    use_case = ListDocumentsUseCase(document_repo, dept_repo, rbac_service, dept_tree_service)

    dept_repo.find_all.return_value = [
        Department(id=1, name="Engineering", level=1, parent_id=None),
        Department(id=2, name="Platform", level=2, parent_id=1),
        Department(id=3, name="QA", level=3, parent_id=2),
    ]
    document_repo.list_by_departments.return_value = [make_document(3, department_id=2, uploaded_by=22)]
    actor = make_actor("manager", department_id=1, user_id=200)

    result = await use_case.execute(actor)

    dept_repo.find_all.assert_awaited_once()
    document_repo.list_by_departments.assert_awaited_once_with([1, 2, 3])
    document_repo.list_all.assert_not_awaited()
    document_repo.list_by_owner.assert_not_awaited()
    assert [item.id for item in result] == [3]


@pytest.mark.asyncio
async def test_list_documents_employee_own_only():
    document_repo = AsyncMock()
    dept_repo = AsyncMock()
    rbac_service = MagicMock(spec=RBACService)
    rbac_service.get_document_scope.return_value = "self"
    dept_tree_service = DepartmentTreeService()
    use_case = ListDocumentsUseCase(document_repo, dept_repo, rbac_service, dept_tree_service)

    document_repo.list_by_owner.return_value = [make_document(4, department_id=1, uploaded_by=300)]
    actor = make_actor("employee", department_id=1, user_id=300)

    result = await use_case.execute(actor)

    document_repo.list_by_owner.assert_awaited_once_with(300)
    document_repo.list_all.assert_not_awaited()
    document_repo.list_by_departments.assert_not_awaited()
    dept_repo.find_all.assert_not_awaited()
    assert [item.id for item in result] == [4]
