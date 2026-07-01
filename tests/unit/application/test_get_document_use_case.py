import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.application.use_cases.document.get_document import GetDocumentByIdUseCase
from app.domain.entities.document import Document, DocumentClassification, DocumentStatus, DocumentVisibility
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound


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


def make_actor(*, role_name: str = "employee", department_id: int | None = 1, is_active: bool = True) -> User:
    return User(
        id=10,
        employee_code="EMP010",
        email=f"{role_name}@company.vn",
        full_name=f"{role_name.title()} User",
        role_name=role_name,
        department_id=department_id,
        is_active=is_active,
    )


@pytest.mark.asyncio
async def test_get_document_by_id_inactive_actor_denied():
    document_repo = AsyncMock()
    actor = make_actor(is_active=False)
    use_case = GetDocumentByIdUseCase(document_repo=document_repo)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101)

    document_repo.find_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_document_by_id_document_not_found():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = None
    actor = make_actor()
    use_case = GetDocumentByIdUseCase(document_repo=document_repo)

    with pytest.raises(ResourceNotFound, match="Document 404 not found"):
        await use_case.execute(actor=actor, document_id=404)

    document_repo.find_by_id.assert_awaited_once_with(404)


@pytest.mark.asyncio
async def test_get_document_by_id_cross_department_employee_denied():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = make_document(department_id=2)
    actor = make_actor(role_name="employee", department_id=1)
    use_case = GetDocumentByIdUseCase(document_repo=document_repo)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101)

    document_repo.find_by_id.assert_awaited_once_with(101)


@pytest.mark.asyncio
async def test_get_document_by_id_same_department_employee_allowed():
    document_repo = AsyncMock()
    document = make_document(department_id=1)
    document_repo.find_by_id.return_value = document
    actor = make_actor(role_name="employee", department_id=1)
    use_case = GetDocumentByIdUseCase(document_repo=document_repo)

    result = await use_case.execute(actor=actor, document_id=101)

    assert result.id == document.id
    assert result.title == document.title
    assert result.department_id == 1
    assert result.allowed_departments == [1]
    document_repo.find_by_id.assert_awaited_once_with(101)


@pytest.mark.asyncio
async def test_get_document_by_id_admin_can_access_any_document():
    document_repo = AsyncMock()
    document = make_document(department_id=99)
    document_repo.find_by_id.return_value = document
    actor = make_actor(role_name="admin", department_id=None)
    use_case = GetDocumentByIdUseCase(document_repo=document_repo)

    result = await use_case.execute(actor=actor, document_id=101)

    assert result.id == document.id
    assert result.allowed_departments == [99]
    assert result.classification == document.class_document
    document_repo.find_by_id.assert_awaited_once_with(101)
