"""Tests for SQLAlchemy-backed agentic storage adapters."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.agentic.adapters.storage.sqlalchemy_storage import SQLAlchemyChunkStorageAdapter, SQLAlchemyDocumentStorageAdapter
from app.agentic.adapters.vector_store.pgvector_store import PGVectorStoreAdapter
from app.agentic.contracts.access_policy import AccessPolicyMetadata, Classification, VisibilityScope
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import CitationMetadata, DocumentRecord


class _SessionStub:
    def __init__(self) -> None:
        self.executed = []
        self.flushed = False
        self.deleted = []

    async def execute(self, stmt):
        self.executed.append(stmt)
        return AsyncMock()

    async def flush(self):
        self.flushed = True


@pytest.mark.asyncio
async def test_sqlalchemy_document_and_chunk_adapters_round_trip() -> None:
    session = _SessionStub()
    doc_adapter = SQLAlchemyDocumentStorageAdapter(session)
    chunk_adapter = SQLAlchemyChunkStorageAdapter(session)

    access_policy = AccessPolicyMetadata(classification=Classification.INTERNAL, visibility_scope=VisibilityScope.GLOBAL)
    record = DocumentRecord(
        document_id="doc-1",
        source={"source_type": "uploaded_file", "mime_type": "application/pdf", "source_uri": "/tmp/doc.pdf"},
        access_policy=access_policy,
        parser_name="pdf",
        parser_version="1",
        chunker_version="chunker-v1",
        title="Doc",
        status="indexed",
        metadata={"k": "v"},
    )
    saved = await doc_adapter.upsert(record)
    assert saved.document_id == "doc-1"
    assert session.flushed is True

    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="hello",
        token_count=5,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=CitationMetadata(),
        access_policy=access_policy,
        metadata={"chunk": True},
        created_at=datetime.now(timezone.utc),
    )
    saved_chunks = await chunk_adapter.upsert_many((chunk,))
    assert saved_chunks == (chunk,)
    await chunk_adapter.delete_by_document("doc-1")
    assert session.flushed is True


@pytest.mark.asyncio
async def test_pgvector_store_adapter_validates_embedding_dimensions() -> None:
    session = _SessionStub()
    adapter = PGVectorStoreAdapter(session)
    access_policy = AccessPolicyMetadata(classification=Classification.INTERNAL, visibility_scope=VisibilityScope.GLOBAL)
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="hello",
        token_count=5,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=CitationMetadata(),
        access_policy=access_policy,
        metadata={},
        created_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="embedding dimension mismatch"):
        await adapter.upsert((chunk,), [[0.1, 0.2]], {"embedding_model": "test", "index_version": "index-v1"})
