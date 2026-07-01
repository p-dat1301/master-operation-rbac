from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.document import Document
from app.domain.repositories.documents_repository import DocumentRepository
from app.infrastructure.database.models.document_model import DocumentModel


class SQLAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _to_entity(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            title=model.title,
            description=model.description,
            store_bucket=model.store_bucket,
            store_object_key=model.store_object_key,
            path_filename=model.path_filename,
            size_byte=model.size_byte,
            status=model.status,
            created_at=self._as_utc(model.created_at),
            updated_at=self._as_utc(model.updated_at),
            uploaded_by=model.uploaded_by,
            visibility_scope=model.visibility_scope,
            allowed_role_names=set(model.allowed_role_names) if model.allowed_role_names else set(),
            allowed_departments=set(model.allowed_departments) if model.allowed_departments else set(),
            class_document=model.class_document,
        )

    async def create(self, document: Document) -> Document:
        model = DocumentModel(
            title=document.title,
            description=document.description,
            store_bucket=document.store_bucket,
            store_object_key=document.store_object_key,
            path_filename=document.path_filename,
            size_byte=document.size_byte,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            uploaded_by=document.uploaded_by,
            visibility_scope=document.visibility_scope,
            allowed_role_names=list(document.allowed_role_names),
            allowed_departments=list(document.allowed_departments),
            class_document=document.class_document,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, document_id: int) -> Optional[Document]:
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[Document]:
        result = await self._session.execute(select(DocumentModel))
        return [self._to_entity(model) for model in result.scalars().all()]

    def _department_filter(self, dept_ids: list[int]):
        return or_(*(DocumentModel.allowed_departments.contains([dept_id]) for dept_id in dept_ids))

    async def list_by_departments(self, dept_ids: list[int]) -> list[Document]:
        if not dept_ids:
            return []
        stmt = select(DocumentModel).where(self._department_filter(dept_ids))
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_by_owner(self, owner_id: int) -> list[Document]:
        stmt = select(DocumentModel).where(DocumentModel.uploaded_by == owner_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def search(self, keyword: str, dept_ids: list[int] | None = None) -> list[Document]:
        stmt = select(DocumentModel)
        if dept_ids is not None:
            if not dept_ids:
                return []
            stmt = stmt.where(self._department_filter(dept_ids))
        keyword_filter = or_(
            DocumentModel.title.ilike(f"%{keyword}%"),
            DocumentModel.description.ilike(f"%{keyword}%"),
        )
        stmt = stmt.where(keyword_filter)
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def update(self, document_id: int, data: dict) -> Document | None:
        model = await self._session.get(DocumentModel, document_id)
        if model is None:
            return None
        for field, value in data.items():
            if hasattr(model, field):
                setattr(model, field, value)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, document_id: int) -> Document | None:
        model = await self._session.get(DocumentModel, document_id)
        if model is None:
            return None
        entity = self._to_entity(model)
        await self._session.delete(model)
        await self._session.commit()
        return entity
