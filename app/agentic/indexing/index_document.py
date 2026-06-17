"""Indexing document orchestration and adapter protocols."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord, NormalizedDocument
from app.agentic.indexing.index_status import IndexRecord, IndexStatus


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


@dataclass(frozen=True)
class IndexDocumentResult:
    document_record: DocumentRecord
    index_record: IndexRecord
    chunks: tuple[DocumentChunk, ...]
    status: IndexStatus


def index_document(
    document: NormalizedDocument,
    chunks: tuple[DocumentChunk, ...],
    *,
    policy_version: str | None = None,
    index_version: str = "index-v1",
) -> IndexDocumentResult:
    record = DocumentRecord(
        document_id=document.document_id,
        source=document.source,
        access_policy=document.access_policy,
        parser_name=document.parser_name,
        parser_version=document.parser_version,
        chunker_version=chunks[0].chunker_version if chunks else document.metadata.get("chunker_version"),
        title=document.title,
        status="indexed" if chunks else "parsed",
        metadata={
            "normalized_version": document.normalized_version,
            "token_count": sum(chunk.token_count or 0 for chunk in chunks),
        },
    )
    index_record = IndexRecord(
        document_id=document.document_id,
        chunk_id=chunks[0].chunk_id if chunks else None,
        parser_version=document.parser_version,
        normalized_version=document.normalized_version,
        chunker_version=chunks[0].chunker_version if chunks else document.metadata.get("chunker_version", "chunker-v1"),
        embedding_model=chunks[0].metadata.get("embedding_model", "unknown") if chunks else "unknown",
        policy_version=policy_version or document.access_policy.policy_version,
        index_version=index_version,
        token_count=sum(chunk.token_count or 0 for chunk in chunks),
        source_type=document.source.source_type.value,
        mime_type=document.source.mime_type,
        status=IndexStatus.INDEXED if chunks else IndexStatus.PENDING,
        metadata={"chunk_ids": [chunk.chunk_id for chunk in chunks]},
    )
    return IndexDocumentResult(document_record=record, index_record=index_record, chunks=chunks, status=index_record.status)
