from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.document.delete_document import DeleteDocumentUseCase
from app.domain.entities.document import Document, DocumentClassification, DocumentStatus, DocumentVisibility
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound, StorageError, StorageObjectNotFound
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


def make_actor(
    *,
    role_name: str = "employee",
    department_id: int | None = 1,
    is_active: bool = True,
    permissions: set[str] | None = None,
) -> User:
    return User(
        id=10,
        employee_code="EMP010",
        email=f"{role_name}@company.vn",
        full_name=f"{role_name.title()} User",
        role_name=role_name,
        department_id=department_id,
        is_active=is_active,
        permissions=permissions or set(),
    )


def make_use_case(
    *,
    document_repo: AsyncMock | None = None,
    storage_service: MagicMock | None = None,
    rbac_service: RBACService | None = None,
) -> DeleteDocumentUseCase:
    return DeleteDocumentUseCase(
        document_repo=document_repo or AsyncMock(),
        storage_service=storage_service or MagicMock(),
        rbac_service=rbac_service or RBACService(),
    )


@pytest.mark.asyncio
async def test_delete_document_inactive_actor_denied():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    actor = make_actor(is_active=False, permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101)

    document_repo.find_by_id.assert_not_awaited()
    document_repo.delete.assert_not_awaited()
    storage_service.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_without_permission_denied():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    actor = make_actor(permissions=set())
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    with pytest.raises(PermissionDenied, match="delete_document"):
        await use_case.execute(actor=actor, document_id=101)

    document_repo.find_by_id.assert_not_awaited()
    document_repo.delete.assert_not_awaited()
    storage_service.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_not_found_raises_resource_not_found():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = None
    storage_service = MagicMock()
    actor = make_actor(permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    with pytest.raises(ResourceNotFound, match="Document 404 not found"):
        await use_case.execute(actor=actor, document_id=404)

    document_repo.find_by_id.assert_awaited_once_with(404)
    document_repo.delete.assert_not_awaited()
    storage_service.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_access_policy_denied():
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = make_document(department_id=2)
    storage_service = MagicMock()
    actor = make_actor(role_name="employee", department_id=1, permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, document_id=101)

    document_repo.find_by_id.assert_awaited_once_with(101)
    document_repo.delete.assert_not_awaited()
    storage_service.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_success_deletes_minio_object_and_repository_row():
    document = make_document(department_id=1)
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = document
    document_repo.delete.return_value = document
    storage_service = MagicMock()
    actor = make_actor(role_name="employee", department_id=1, permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    result = await use_case.execute(actor=actor, document_id=101)

    assert result.id == document.id
    assert result.title == document.title
    assert result.store_object_key == document.store_object_key
    assert result.allowed_departments == [1]
    storage_service.delete_file.assert_called_once_with("documents/engineering-plan.pdf")
    document_repo.delete.assert_awaited_once_with(101)


@pytest.mark.asyncio
async def test_delete_document_success_when_minio_object_already_missing():
    document = make_document(department_id=1)
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = document
    document_repo.delete.return_value = document
    storage_service = MagicMock()
    storage_service.delete_file.side_effect = StorageObjectNotFound("object not found")
    actor = make_actor(role_name="employee", department_id=1, permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    result = await use_case.execute(actor=actor, document_id=101)

    assert result.id == document.id
    assert result.store_object_key == document.store_object_key
    storage_service.delete_file.assert_called_once_with("documents/engineering-plan.pdf")
    document_repo.delete.assert_awaited_once_with(101)


@pytest.mark.asyncio
async def test_delete_document_propagates_real_storage_failure():
    document = make_document(department_id=1)
    document_repo = AsyncMock()
    document_repo.find_by_id.return_value = document
    storage_service = MagicMock()
    storage_service.delete_file.side_effect = StorageError("MinIO connection refused")
    actor = make_actor(role_name="employee", department_id=1, permissions={"delete_document"})
    use_case = make_use_case(document_repo=document_repo, storage_service=storage_service)

    with pytest.raises(StorageError, match="MinIO connection refused"):
        await use_case.execute(actor=actor, document_id=101)

    storage_service.delete_file.assert_called_once_with("documents/engineering-plan.pdf")
    document_repo.delete.assert_not_awaited()
