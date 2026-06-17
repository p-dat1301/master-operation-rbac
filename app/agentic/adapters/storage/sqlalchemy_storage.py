"""SQLAlchemy-backed storage adapters for agentic RAG documents and chunks."""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import CitationMetadata, DocumentRecord
from app.agentic.contracts.source import SourceMetadata
from app.agentic.indexing.index_document import ChunkStorageAdapter, DocumentStorageAdapter
from app.infrastructure.database.models.agentic_chunk_model import AgenticChunkModel
from app.infrastructure.database.models.agentic_document_model import AgenticDocumentModel


class SQLAlchemyDocumentStorageAdapter(DocumentStorageAdapter):
    """Persist document-level indexing metadata with async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, document_id: str) -> DocumentRecord | None:
        model = await self._session.get(AgenticDocumentModel, document_id)
        return _document_to_record(model) if model else None

    async def upsert(self, record: DocumentRecord) -> DocumentRecord:
        values = _document_values(record)
        stmt = insert(AgenticDocumentModel.__table__).values(**values)
        update_values = {key: stmt.excluded[key] for key in values if key != "document_id"}
        await self._session.execute(stmt.on_conflict_do_update(index_elements=["document_id"], set_=update_values))
        await self._session.flush()
        return record

    async def delete(self, document_id: str) -> None:
        await self._session.execute(delete(AgenticDocumentModel).where(AgenticDocumentModel.document_id == document_id))
        await self._session.flush()


class SQLAlchemyChunkStorageAdapter(ChunkStorageAdapter):
    """Persist retry-safe chunk records with async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_document(self, document_id: str) -> list[DocumentChunk]:
        stmt = select(AgenticChunkModel).where(AgenticChunkModel.document_id == document_id).order_by(AgenticChunkModel.chunk_index)
        result = await self._session.execute(stmt)
        return [_chunk_to_record(model) for model in result.scalars().all()]

    async def upsert_many(self, chunks: tuple[DocumentChunk, ...]) -> tuple[DocumentChunk, ...]:
        if not chunks:
            return chunks
        values = [_chunk_values(chunk) for chunk in chunks]
        stmt = insert(AgenticChunkModel.__table__).values(values)
        update_values = {key: stmt.excluded[key] for key in values[0] if key != "chunk_id"}
        await self._session.execute(stmt.on_conflict_do_update(index_elements=["chunk_id"], set_=update_values))
        await self._session.flush()
        return chunks

    async def delete_by_document(self, document_id: str) -> None:
        await self._session.execute(delete(AgenticChunkModel).where(AgenticChunkModel.document_id == document_id))
        await self._session.flush()


def _document_values(record: DocumentRecord) -> dict[str, object]:
    return {
        "document_id": record.document_id,
        "source": record.source.model_dump(mode="json"),
        "access_policy": record.access_policy.model_dump(mode="json"),
        "parser_name": record.parser_name,
        "parser_version": record.parser_version,
        "chunker_version": record.chunker_version,
        "title": record.title,
        "status": record.status,
        "metadata": record.metadata,
    }


def _document_to_record(model: AgenticDocumentModel) -> DocumentRecord:
    return DocumentRecord(
        document_id=model.document_id,
        source=SourceMetadata.model_validate(model.source),
        access_policy=AccessPolicyMetadata.model_validate(model.access_policy),
        parser_name=model.parser_name,
        parser_version=model.parser_version,
        chunker_version=model.chunker_version,
        title=model.title,
        status=model.status,
        metadata=model.document_metadata,
    )


def _chunk_values(chunk: DocumentChunk) -> dict[str, object]:
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "text": chunk.text,
        "token_count": chunk.token_count,
        "chunk_index": chunk.chunk_index,
        "chunker_version": chunk.chunker_version,
        "source_type": chunk.source_type,
        "mime_type": chunk.mime_type,
        "citation": chunk.citation.model_dump(mode="json"),
        "access_policy": chunk.access_policy.model_dump(mode="json"),
        "metadata": chunk.metadata,
        "created_at": chunk.created_at,
    }


def _chunk_to_record(model: AgenticChunkModel) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=model.chunk_id,
        document_id=model.document_id,
        text=model.text,
        token_count=model.token_count,
        chunk_index=model.chunk_index,
        chunker_version=model.chunker_version,
        source_type=model.source_type,
        mime_type=model.mime_type,
        citation=CitationMetadata.model_validate(model.citation),
        access_policy=AccessPolicyMetadata.model_validate(model.access_policy),
        metadata=model.chunk_metadata,
        created_at=model.created_at,
    )
