from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.entities.document import DocumentClassification, DocumentStatus, DocumentVisibility
from app.infrastructure.database.models.document_model import DocumentModel
from app.infrastructure.database.repositories.sqlalchemy_documents_repo import SQLAlchemyDocumentRepository


def _model(**kwargs) -> DocumentModel:
    model = DocumentModel(
        title=kwargs.pop("title", "Budget Plan"),
        description=kwargs.pop("description", "Dept 10 budget"),
        store_bucket=kwargs.pop("store_bucket", "bucket"),
        store_object_key=kwargs.pop("store_object_key", "docs/doc-a.pdf"),
        path_filename=kwargs.pop("path_filename", "doc-a.pdf"),
        size_byte=kwargs.pop("size_byte", 100),
        status=kwargs.pop("status", DocumentStatus.UPLOADED),
        uploaded_by=kwargs.pop("uploaded_by", 11),
        visibility_scope=kwargs.pop("visibility_scope", DocumentVisibility.DEPARTMENT),
        allowed_role_names=kwargs.pop("allowed_role_names", ["manager"]),
        allowed_departments=kwargs.pop("allowed_departments", [10]),
        class_document=kwargs.pop("class_document", DocumentClassification.INTERNAL),
    )
    model.id = kwargs.pop("id", 1)
    model.created_at = kwargs.pop("created_at", datetime.now(timezone.utc))
    model.updated_at = kwargs.pop("updated_at", datetime.now(timezone.utc))
    return model


def _execute_result(models: list[DocumentModel]):
    scalars = MagicMock()
    scalars.all.return_value = models
    scalars.first.return_value = models[0] if models else None
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


@pytest.mark.asyncio
async def test_document_repository_list_and_search_queries_use_database_filters():
    session = AsyncMock()
    session.execute.side_effect = [
        _execute_result([_model(id=1), _model(id=2, title="Security Policy", allowed_departments=[20])]),
        _execute_result([_model(id=1)]),
        _execute_result([_model(id=1), _model(id=3, title="Owner Memo")]),
        _execute_result([_model(id=1)]),
    ]
    repo = SQLAlchemyDocumentRepository(session)

    all_docs = await repo.list_all()
    dept_docs = await repo.list_by_departments([10])
    owner_docs = await repo.list_by_owner(11)
    search_docs = await repo.search("budget", dept_ids=[10])

    assert len(all_docs) == 2
    assert [doc.id for doc in dept_docs] == [1]
    assert [doc.id for doc in owner_docs] == [1, 3]
    assert [doc.id for doc in search_docs] == [1]

    dept_statement = str(session.execute.await_args_list[1].args[0])
    owner_statement = str(session.execute.await_args_list[2].args[0])
    search_statement = str(session.execute.await_args_list[3].args[0])

    assert "documents.allowed_departments" in dept_statement
    assert "documents.uploaded_by" in owner_statement
    assert "documents.allowed_departments" in search_statement
    assert "lower(documents.title) LIKE lower" in search_statement
    assert "lower(documents.description) LIKE lower" in search_statement
    assert search_statement.index("documents.allowed_departments") < search_statement.index("lower(documents.title)")


@pytest.mark.asyncio
async def test_document_repository_update_handles_partial_data():
    session = AsyncMock()
    model = _model(id=9, title="Old title", description="Old desc")
    session.get.return_value = model
    repo = SQLAlchemyDocumentRepository(session)

    updated = await repo.update(9, {"title": "New title"})

    assert updated is not None
    assert updated.id == 9
    assert updated.title == "New title"
    assert updated.description == "Old desc"
    session.get.assert_awaited_once_with(DocumentModel, 9)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(model)


@pytest.mark.asyncio
async def test_document_repository_delete_returns_deleted_entity_for_storage_cleanup():
    session = AsyncMock()
    model = _model(id=8, store_bucket="cleanup-bucket", store_object_key="cleanup/key.pdf")
    session.get.return_value = model
    repo = SQLAlchemyDocumentRepository(session)

    deleted = await repo.delete(8)

    assert deleted is not None
    assert deleted.id == 8
    assert deleted.store_bucket == "cleanup-bucket"
    assert deleted.store_object_key == "cleanup/key.pdf"
    session.get.assert_awaited_once_with(DocumentModel, 8)
    session.delete.assert_awaited_once_with(model)
    session.commit.assert_awaited_once()
