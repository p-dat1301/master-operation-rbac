import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.application.dtos.document import DocumentCreateInput
from app.application.use_cases.document.create_document import CreateDocumentUsecase
from app.domain.entities.document import Document, DocumentStatus, DocumentVisibility, DocumentClassification
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, BusinessRuleViolation

@pytest.mark.asyncio
async def test_create_document_success():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    rbac_service = MagicMock()

    storage_service.bucket_name = "test-bucket"
    storage_service.upload_file.return_value = "documents/test-uuid/sample.pdf"

    actor = User(
        id=1, employee_code="EMP001", email="admin@company.vn", full_name="Admin User",
        role_name="admin", department_id=None, is_active=True
    )

    created_entity = Document(
        id=123,
        title="Báo cáo quý 1",
        description="Báo cáo tài chính",
        store_bucket="test-bucket",
        store_object_key="documents/test-uuid/sample.pdf",
        path_filename="sample.pdf",
        size_byte=1000,
        status=DocumentStatus.UPLOADED,
        uploaded_by=1,
        visibility_scope=DocumentVisibility.PUBLIC,
        allowed_role_names=set(),
        allowed_departments=set(),
        class_document=DocumentClassification.INTERNAL,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    document_repo.create.return_value = created_entity

    use_case = CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service
    )

    input_data = DocumentCreateInput(
        title="Báo cáo quý 1",
        description="Báo cáo tài chính",
        visibility_scope=DocumentVisibility.PUBLIC,
        allowed_role_names=[],
        allowed_departments=[],
        class_document=DocumentClassification.INTERNAL
    )

    result = await use_case.execute(
        actor=actor,
        data=input_data,
        file_bytes=b"sample content",
        filename="sample.pdf",
        mime_type="application/pdf"
    )

    assert result.id == 123
    assert result.status == DocumentStatus.UPLOADED
    assert result.store_bucket == "test-bucket"
    storage_service.upload_file.assert_called_once()
    document_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_document_forbidden_role():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    rbac_service = MagicMock()
    rbac_service.require_permission.side_effect = PermissionDenied("Lacks upload_document permission")

    actor = User(
        id=3, employee_code="EMP003", email="employee@company.vn", full_name="Employee User",
        role_name="employee", department_id=1, is_active=True
    )

    use_case = CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service
    )

    input_data = DocumentCreateInput(
        title="Báo cáo quý 1",
        visibility_scope=DocumentVisibility.PUBLIC,
        class_document=DocumentClassification.INTERNAL
    )

    with pytest.raises(PermissionDenied):
        await use_case.execute(
            actor=actor,
            data=input_data,
            file_bytes=b"content",
            filename="sample.pdf",
            mime_type="application/pdf"
        )


@pytest.mark.asyncio
async def test_create_document_missing_roles_for_role_scope():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    rbac_service = MagicMock()

    actor = User(
        id=2, employee_code="EMP002", email="manager@company.vn", full_name="Manager User",
        role_name="manager", department_id=1, is_active=True
    )

    use_case = CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service
    )

    # visibility_scope=ROLE but allowed_role_names is empty
    input_data = DocumentCreateInput(
        title="Báo cáo mật",
        visibility_scope=DocumentVisibility.ROLE,
        allowed_role_names=[],
        class_document=DocumentClassification.CONFIDENTIAL
    )

    with pytest.raises(BusinessRuleViolation):
        await use_case.execute(
            actor=actor,
            data=input_data,
            file_bytes=b"content",
            filename="sample.pdf",
            mime_type="application/pdf"
        )


@pytest.mark.asyncio
async def test_create_document_missing_departments_for_department_scope():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    rbac_service = MagicMock()

    actor = User(
        id=2, employee_code="EMP002", email="manager@company.vn", full_name="Manager User",
        role_name="manager", department_id=1, is_active=True
    )

    use_case = CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service
    )

    # visibility_scope=DEPARTMENT but allowed_departments is empty
    input_data = DocumentCreateInput(
        title="Báo cáo bộ phận",
        visibility_scope=DocumentVisibility.DEPARTMENT,
        allowed_departments=[],
        class_document=DocumentClassification.INTERNAL
    )

    with pytest.raises(BusinessRuleViolation):
        await use_case.execute(
            actor=actor,
            data=input_data,
            file_bytes=b"content",
            filename="sample.pdf",
            mime_type="application/pdf"
        )


@pytest.mark.asyncio
async def test_create_document_rollback_on_db_error():
    document_repo = AsyncMock()
    storage_service = MagicMock()
    rbac_service = MagicMock()

    storage_service.bucket_name = "test-bucket"
    storage_service.upload_file.return_value = "documents/test-uuid/sample.pdf"
    
    # DB creation error
    document_repo.create.side_effect = Exception("DB Connection Error")

    actor = User(
        id=2, employee_code="EMP002", email="manager@company.vn", full_name="Manager User",
        role_name="manager", department_id=1, is_active=True
    )

    use_case = CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service
    )

    input_data = DocumentCreateInput(
        title="Báo cáo",
        visibility_scope=DocumentVisibility.PUBLIC,
        class_document=DocumentClassification.INTERNAL
    )

    with pytest.raises(Exception, match="DB Connection Error"):
        await use_case.execute(
            actor=actor,
            data=input_data,
            file_bytes=b"content",
            filename="sample.pdf",
            mime_type="application/pdf"
        )

    # Verify storage_service.delete_file was called to clean up the orphaned file
    storage_service.delete_file.assert_called_once()
