import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.application.dtos.document import DocumentUpdateInput
from app.application.use_cases.document.update_document import UpdateDocumentUseCase
from app.domain.entities.document import Document, DocumentClassification, DocumentStatus, DocumentVisibility
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.services.rbac_service import RBACService


def make_document(*, document_id: int = 101, department_id: int = 1) -> Document:
    return Document(
        id=document_id,
        title="Engineering Plan",
        description="Quarterly department plan",
        store_bucket="docs",
        store_object_key="documents/engineering-plan.pdf",
        path_filename="engineering-plan.pdf",
        size_byte=2048,
        status=DocumentStatus.UPLOADED,
        uploaded_by=200,
        visibility_scope=DocumentVisibility.DEPARTMENT,
        allowed_role_names=set(),
        allowed_departments={department_id},
        class_document=DocumentClassification.INTERNAL,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_actor(*, role_name: str = "employee", department_id: int | None = 1, is_active: bool = True, permissions: set[str] | None = None) -> User:
    return User(
        id=10,
        employee_code="EMP010",
        email=f"{role_name}@company.vn",
        full_name=f"{role_name.title()} User",
        role_name=role_name,
        department_id=department_id,
        is_active=is_active,
        permissions={"update_document"} if permissions is None else permissions,
    )


@pytest.mark.asyncio
async def test_update_document_inactive_actor_denied():
    document_repo = AsyncMock()
    rbac_service = RBACService()
    actor = make_actor(is_active=False)
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101, payload=DocumentUpdateInput(title="New"))

    document_repo.find_by_id.assert_not_awaited()
    document_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_document_missing_permission_denied():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = make_document()
    rbac_service = RBACService()
    actor = make_actor(permissions=set())
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101, payload=DocumentUpdateInput(title="New"))

    document_repo.find_by_id.assert_not_awaited()
    document_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_document_not_found():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = None
    rbac_service = RBACService()
    actor = make_actor()
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    with pytest.raises(ResourceNotFound, match="Document 404 not found"):
        await use_case.execute(actor=actor, document_id=404, payload=DocumentUpdateInput(title="New"))

    document_repo.find_by_id.assert_awaited_once_with(404)
    document_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_document_cross_department_employee_denied():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = make_document(department_id=2)
    rbac_service = RBACService()
    actor = make_actor(role_name="employee", department_id=1)
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101, payload=DocumentUpdateInput(title="New"))

    document_repo.find_by_id.assert_awaited_once_with(101)
    document_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_document_title_only_success():
    document_repo = AsyncMock()
    document = make_document()
    updated_document = make_document()
    updated_document.title = "Updated Engineering Plan"
    document_repo.find_by_id.return_value = document
    document_repo.update.return_value = updated_document
    rbac_service = RBACService()
    actor = make_actor()
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    result = await use_case.execute(actor=actor, document_id=101, payload=DocumentUpdateInput(title="Updated Engineering Plan"))

    document_repo.update.assert_awaited_once_with(101, {"title": "Updated Engineering Plan"})
    assert result.title == "Updated Engineering Plan"


@pytest.mark.asyncio
async def test_update_document_all_fields_success():
    document_repo = AsyncMock()
    document = make_document()
    updated_document = make_document()
    updated_document.title = "Updated Title"
    updated_document.description = "Updated Description"
    updated_document.status = DocumentStatus.INDEXED
    document_repo.find_by_id.return_value = document
    document_repo.update.return_value = updated_document
    rbac_service = RBACService()
    actor = make_actor()
    use_case = UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)

    payload = DocumentUpdateInput(
        title="Updated Title",
        description="Updated Description",
        status=DocumentStatus.INDEXED,
    )
    result = await use_case.execute(actor=actor, document_id=101, payload=payload)

    document_repo.update.assert_awaited_once_with(
        101,
        {
            "title": "Updated Title",
            "description": "Updated Description",
            "status": DocumentStatus.INDEXED,
        },
    )
    assert result.title == "Updated Title"
    assert result.description == "Updated Description"
    assert result.status == DocumentStatus.INDEXED
