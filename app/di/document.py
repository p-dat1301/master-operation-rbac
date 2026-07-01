from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.document.create_document import CreateDocumentUsecase
from app.application.use_cases.document.delete_document import DeleteDocumentUseCase
from app.application.use_cases.document.get_document import GetDocumentByIdUseCase
from app.application.use_cases.document.list_documents import ListDocumentsUseCase
from app.application.use_cases.document.search_documents import SearchDocumentsUseCase
from app.application.use_cases.document.update_document import UpdateDocumentUseCase
from app.domain.services.rbac_service import RBACService
from app.infrastructure.storage.minio_storage import MinioStorageService

from app.infrastructure.database.repositories.sqlalchemy_documents_repo import SQLAlchemyDocumentRepository


def provide_create_document(db: AsyncSession) -> CreateDocumentUsecase:
    document_repo = SQLAlchemyDocumentRepository(db)
    storage_service = MinioStorageService()
    rbac_service = RBACService()
    return CreateDocumentUsecase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service,
    )


def provide_list_documents(db: AsyncSession) -> ListDocumentsUseCase:
    from app.domain.services.department_tree import DepartmentTreeService
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    document_repo = SQLAlchemyDocumentRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac_service = RBACService()
    dept_tree_service = DepartmentTreeService()
    return ListDocumentsUseCase(
        document_repo=document_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )


def provide_get_document_by_id(db: AsyncSession) -> GetDocumentByIdUseCase:
    document_repo = SQLAlchemyDocumentRepository(db)
    return GetDocumentByIdUseCase(document_repo=document_repo)


def provide_search_documents(db: AsyncSession) -> SearchDocumentsUseCase:
    from app.domain.services.department_tree import DepartmentTreeService
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    document_repo = SQLAlchemyDocumentRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac_service = RBACService()
    dept_tree_service = DepartmentTreeService()
    return SearchDocumentsUseCase(
        document_repo=document_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )


def provide_update_document(db: AsyncSession) -> UpdateDocumentUseCase:
    document_repo = SQLAlchemyDocumentRepository(db)
    rbac_service = RBACService()
    return UpdateDocumentUseCase(document_repo=document_repo, rbac_service=rbac_service)


def provide_delete_document(db: AsyncSession) -> DeleteDocumentUseCase:
    document_repo = SQLAlchemyDocumentRepository(db)
    storage_service = MinioStorageService()
    rbac_service = RBACService()
    return DeleteDocumentUseCase(
        document_repo=document_repo,
        storage_service=storage_service,
        rbac_service=rbac_service,
    )
