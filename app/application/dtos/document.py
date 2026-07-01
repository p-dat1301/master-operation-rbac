from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel

from app.domain.entities.document import Document, DocumentStatus, DocumentVisibility, DocumentClassification


class DocumentOutput(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    store_bucket: str
    store_object_key: str
    path_filename: str
    size_byte: int
    status: DocumentStatus
    uploaded_by: int
    visibility_scope: DocumentVisibility
    allowed_role_names: List[str] # from to repository, this is a list of role names that are allowed to access the document
    allowed_departments: List[int]
    class_document: DocumentClassification
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, document: Document) -> DocumentOutput:
        return cls(
            id=document.id,
            title=document.title,
            description=document.description,
            store_bucket=document.store_bucket,
            store_object_key=document.store_object_key,
            path_filename=document.path_filename,
            size_byte=document.size_byte,
            status=document.status,
            uploaded_by=document.uploaded_by,
            visibility_scope=document.visibility_scope,
            allowed_role_names=list(document.allowed_role_names),
            allowed_departments=list(document.allowed_departments),
            class_document=document.class_document,
            created_at=document.created_at.astimezone(timezone.utc) if document.created_at else None,
            updated_at=document.updated_at.astimezone(timezone.utc) if document.updated_at else None,
        )


class DocumentListOutput(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: DocumentStatus
    visibility_scope: DocumentVisibility
    department_id: Optional[int] = None
    classification: DocumentClassification
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, document: Document) -> DocumentListOutput:
        return cls(
            id=document.id,
            title=document.title,
            description=document.description,
            status=document.status,
            visibility_scope=document.visibility_scope,
            department_id=next(iter(document.allowed_departments), None),
            classification=document.class_document,
            created_at=document.created_at.astimezone(timezone.utc) if document.created_at else None,
            updated_at=document.updated_at.astimezone(timezone.utc) if document.updated_at else None,
        )


class DocumentDetailOutput(DocumentListOutput):
    store_bucket: str
    store_object_key: str
    path_filename: str
    size_byte: int
    uploaded_by: int
    allowed_role_names: List[str]
    allowed_departments: List[int]

    @classmethod
    def from_entity(cls, document: Document) -> DocumentDetailOutput:
        return cls(
            id=document.id,
            title=document.title,
            description=document.description,
            status=document.status,
            visibility_scope=document.visibility_scope,
            department_id=next(iter(document.allowed_departments), None),
            classification=document.class_document,
            created_at=document.created_at.astimezone(timezone.utc) if document.created_at else None,
            updated_at=document.updated_at.astimezone(timezone.utc) if document.updated_at else None,
            store_bucket=document.store_bucket,
            store_object_key=document.store_object_key,
            path_filename=document.path_filename,
            size_byte=document.size_byte,
            uploaded_by=document.uploaded_by,
            allowed_role_names=list(document.allowed_role_names),
            allowed_departments=list(document.allowed_departments),
        )


class DocumentUpdateInput(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None


class DocumentSearchParams(BaseModel):
    q: Optional[str] = None


class DocumentCreateInput(BaseModel):
    title: str
    description: Optional[str] = None
    visibility_scope: DocumentVisibility
    allowed_role_names: List[str] = []
    allowed_departments: List[int] = []
    class_document: DocumentClassification