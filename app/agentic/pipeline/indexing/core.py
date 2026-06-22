"""Canonical indexing stage for agentic pipeline."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord, NormalizedDocument
from app.agentic.pipeline.indexing.index_status import IndexRecord, IndexStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentStorageAdapter(ABC):
    @abstractmethod
    async def get(self, document_id: str) -> DocumentRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, record: DocumentRecord) -> DocumentRecord:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, document_id: str) -> None:
        raise NotImplementedError


class ChunkStorageAdapter(ABC):
    @abstractmethod
    async def get_many_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_document(self, document_id: str) -> list[DocumentChunk]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_many(self, chunks: tuple[DocumentChunk, ...]) -> tuple[DocumentChunk, ...]:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_document(self, document_id: str) -> None:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class VectorStoreAdapter(ABC):
    @abstractmethod
    async def upsert(self, chunks: tuple[DocumentChunk, ...], embeddings: list[list[float]], metadata: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_document(self, document_id: str) -> None:
        raise NotImplementedError


class ElasticsearchSyncAdapter(ABC):
    @abstractmethod
    def ensure_index(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def bulk_index_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class IndexDocumentResult:
    document_record: DocumentRecord
    index_record: IndexRecord
    chunks: tuple[DocumentChunk, ...]
    status: IndexStatus


class EmbeddingPersistenceError(RuntimeError):
    """Raised when chunk embedding generation or vector persistence fails."""


class PgvectorBackfillAdapter(ABC):
    @abstractmethod
    async def list_chunks(self, *, limit: int, offset: int) -> tuple[DocumentChunk, ...]:
        raise NotImplementedError


class ElasticsearchSyncWarning(RuntimeError):
    """Warning wrapper for Elasticsearch derived-index synchronization failures."""


def build_elasticsearch_chunk_document(chunk: DocumentChunk) -> dict[str, Any]:
    metadata = dict(chunk.metadata)
    return {
        "text": chunk.text,
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "chunk_index": chunk.chunk_index,
        "token_count": chunk.token_count,
        "source_type": chunk.source_type,
        "mime_type": chunk.mime_type,
        "source_uri": metadata.get("source_uri"),
        "filename": metadata.get("filename"),
        "title": metadata.get("title"),
        "citation": {
            "page_number": chunk.citation.page_number,
            "section_path": chunk.citation.section_path,
            "block_anchor": chunk.citation.block_anchor,
        },
        "access_policy": {
            "classification": chunk.access_policy.classification.value,
            "visibility_scope": chunk.access_policy.visibility_scope.value,
            "allowed_roles": list(chunk.access_policy.allowed_roles),
            "department_id": chunk.access_policy.department_id,
            "owner_id": chunk.access_policy.owner_id,
            "policy_version": chunk.access_policy.policy_version,
        },
        "metadata": metadata,
        "created_at": metadata.get("created_at"),
        "indexed_at": metadata.get("indexed_at"),
    }


async def _run_sync(func: Any, /, *args: Any, **kwargs: Any) -> Any:
    return await asyncio.to_thread(func, *args, **kwargs)


async def sync_chunks_to_elasticsearch(
    chunks: tuple[DocumentChunk, ...],
    *,
    elasticsearch_sync: ElasticsearchSyncAdapter | None = None,
) -> None:
    if not chunks or not settings.RAG_USE_ELASTICSEARCH or elasticsearch_sync is None:
        return

    try:
        await _run_sync(elasticsearch_sync.ensure_index)
        await _run_sync(elasticsearch_sync.bulk_index_chunks, chunks)
    except Exception as exc:  # noqa: BLE001 - derived index failures must never fail ingestion
        logger.warning(
            "Elasticsearch chunk sync failed; continuing with pgvector as source of truth: %s",
            exc,
            extra={
                "document_ids": sorted({chunk.document_id for chunk in chunks}),
                "chunk_ids": [chunk.chunk_id for chunk in chunks],
                "error": str(exc),
            },
        )


async def reindex_chunks_to_elasticsearch(
    *,
    backfill_adapter: PgvectorBackfillAdapter,
    elasticsearch_sync: ElasticsearchSyncAdapter,
    batch_size: int = 200,
) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if not settings.RAG_USE_ELASTICSEARCH:
        return 0

    indexed_count = 0
    offset = 0
    await _run_sync(elasticsearch_sync.ensure_index)
    while True:
        chunks = await backfill_adapter.list_chunks(limit=batch_size, offset=offset)
        if not chunks:
            break
        await _run_sync(elasticsearch_sync.bulk_index_chunks, chunks)
        indexed_count += len(chunks)
        offset += len(chunks)
    return indexed_count


async def embed_and_persist_chunks(
    chunks: tuple[DocumentChunk, ...],
    *,
    embedding_provider: EmbeddingProvider,
    vector_store: VectorStoreAdapter,
    metadata: dict[str, Any],
    elasticsearch_sync: ElasticsearchSyncAdapter | None = None,
) -> list[list[float]]:
    """Generate embeddings for chunks and persist them through the vector store boundary."""
    if not chunks:
        return []

    try:
        embeddings = await embedding_provider.embed([chunk.text for chunk in chunks])
        await vector_store.upsert(chunks, embeddings, metadata)
    except Exception as exc:  # noqa: BLE001 - boundary converts provider/store failures into explicit indexing failure
        raise EmbeddingPersistenceError(str(exc)) from exc
    await sync_chunks_to_elasticsearch(chunks, elasticsearch_sync=elasticsearch_sync)
    return embeddings


def index_document(
    document: NormalizedDocument,
    chunks: tuple[DocumentChunk, ...],
    *,
    policy_version: str | None = None,
    index_version: str = "index-v1",
    embedding_error: str | None = None,
) -> IndexDocumentResult:
    record_status = "failed" if embedding_error else "indexed" if chunks else "parsed"
    token_count = sum(chunk.token_count or 0 for chunk in chunks)
    embedding_model = chunks[0].metadata.get("embedding_model", "unknown") if chunks else "unknown"
    record_metadata = {"normalized_version": document.normalized_version, "token_count": token_count}
    if embedding_error:
        record_metadata["embedding_error"] = embedding_error
    record = DocumentRecord(
        document_id=document.document_id,
        source=document.source,
        access_policy=document.access_policy,
        parser_name=document.parser_name,
        parser_version=document.parser_version,
        chunker_version=chunks[0].chunker_version if chunks else document.metadata.get("chunker_version"),
        title=document.title,
        status=record_status,
        metadata=record_metadata,
    )
    index_metadata = {"chunk_ids": [chunk.chunk_id for chunk in chunks]}
    if embedding_error:
        index_metadata["embedding_failed"] = "true"
    index_record = IndexRecord(
        document_id=document.document_id,
        chunk_id=chunks[0].chunk_id if chunks else None,
        parser_version=document.parser_version,
        normalized_version=document.normalized_version,
        chunker_version=chunks[0].chunker_version if chunks else document.metadata.get("chunker_version", "chunker-v1"),
        embedding_model=embedding_model,
        policy_version=policy_version or document.access_policy.policy_version,
        index_version=index_version,
        token_count=token_count,
        source_type=document.source.source_type.value,
        mime_type=document.source.mime_type,
        status=IndexStatus.FAILED if embedding_error else IndexStatus.INDEXED if chunks else IndexStatus.PENDING,
        failure_reason=embedding_error,
        metadata=index_metadata,
    )
    return IndexDocumentResult(document_record=record, index_record=index_record, chunks=chunks, status=index_record.status)
