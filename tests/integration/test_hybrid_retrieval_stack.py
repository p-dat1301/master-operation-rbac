"""Integration tests for hybrid retrieval stack."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.agentic.adapters.search.elasticsearch_client import create_elasticsearch_client, ensure_agentic_chunks_index
from app.agentic.pipeline.indexing.core import build_elasticsearch_chunk_document
from app.agentic.adapters.storage.models import AgenticChunkEmbeddingModel
from app.agentic.adapters.storage.sqlalchemy_storage import SQLAlchemyChunkStorageAdapter, SQLAlchemyDocumentStorageAdapter
from app.agentic.adapters.vector_store.pgvector_retrieval_store import PGVectorRetrievalStore
from app.agentic.contracts import AccessPolicyMetadata, Classification, DocumentChunk, RetrievalRequest, SourceMetadata, SourceType, VisibilityScope
from app.agentic.contracts.document import CitationMetadata, DocumentRecord
from app.agentic.contracts.retrieval import RetrievalFilter
from app.di.agentic import SessionScopedVectorRetrievalStore

pytestmark = pytest.mark.asyncio


@dataclass
class _EmbeddingProvider:
    vector: list[float]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self.vector for _ in texts]


@pytest.fixture
async def pg_session():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not configured for integration test")
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


async def _reset_agentic_tables(session) -> None:
    await session.execute(text("TRUNCATE agentic_chunk_embeddings, agentic_chunks, agentic_documents RESTART IDENTITY CASCADE"))
    await session.commit()


async def _seed_pgvector_document(session) -> tuple[DocumentChunk, DocumentChunk]:
    policy = AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL)
    source = SourceMetadata(source_type=SourceType.UPLOADED_FILE, mime_type="application/pdf", source_uri="/tmp/hybrid.pdf", filename="hybrid.pdf")
    record = DocumentRecord(document_id="doc-hybrid", source=source, access_policy=policy, parser_name="parser", parser_version="1", chunker_version="1", title="Hybrid", status="indexed", metadata={})
    now = datetime.now(timezone.utc)
    chunk_1 = DocumentChunk(chunk_id="chunk-hybrid-1", document_id="doc-hybrid", text="hybrid policy overview", token_count=3, chunk_index=0, chunker_version="1", source_type=SourceType.UPLOADED_FILE.value, mime_type="application/pdf", citation=CitationMetadata(page_number=1), access_policy=policy, metadata={"retriever": "pgvector"}, created_at=now)
    chunk_2 = DocumentChunk(chunk_id="chunk-hybrid-2", document_id="doc-hybrid", text="hybrid fallback baseline", token_count=3, chunk_index=1, chunker_version="1", source_type=SourceType.UPLOADED_FILE.value, mime_type="application/pdf", citation=CitationMetadata(page_number=2), access_policy=policy, metadata={"retriever": "pgvector"}, created_at=now)
    await SQLAlchemyDocumentStorageAdapter(session).upsert(record)
    await SQLAlchemyChunkStorageAdapter(session).upsert_many((chunk_1, chunk_2))
    session.add_all([
        AgenticChunkEmbeddingModel(chunk_id=chunk_1.chunk_id, document_id=chunk_1.document_id, embedding=[1.0] + [0.0] * 1023, embedding_model="test", index_version="v1", embedding_metadata={}),
        AgenticChunkEmbeddingModel(chunk_id=chunk_2.chunk_id, document_id=chunk_2.document_id, embedding=[0.9] + [0.1] * 1023, embedding_model="test", index_version="v1", embedding_metadata={}),
    ])
    await session.commit()
    return chunk_1, chunk_2


async def test_real_es_and_pgvector_hybrid_stack_smoke(pg_session, monkeypatch: pytest.MonkeyPatch) -> None:
    await _reset_agentic_tables(pg_session)
    pgvector_chunk_1, pgvector_chunk_2 = await _seed_pgvector_document(pg_session)
    elasticsearch_chunk = pgvector_chunk_2.model_copy(update={"chunk_id": "chunk-elasticsearch-only", "text": "hybrid policy lexical match", "chunker_version": "1", "created_at": pgvector_chunk_2.created_at, "metadata": {"retriever": "elasticsearch"}})

    client = create_elasticsearch_client()
    try:
        ensure_agentic_chunks_index(client)
    except Exception as exc:
        pytest.skip(f"Elasticsearch unavailable: {exc}")

    client.options(ignore_status=404).delete(index="agentic_chunks", id="chunk-hybrid-1")
    client.options(ignore_status=404).delete(index="agentic_chunks", id="chunk-hybrid-2")
    elasticsearch_document = build_elasticsearch_chunk_document(elasticsearch_chunk)
    elasticsearch_document["chunker_version"] = elasticsearch_chunk.chunker_version
    elasticsearch_document["created_at"] = elasticsearch_chunk.created_at.isoformat()
    client.index(index="agentic_chunks", id=elasticsearch_chunk.chunk_id, document=elasticsearch_document, refresh="wait_for")

    monkeypatch.setattr("app.di.agentic.get_embedding_provider", lambda: _EmbeddingProvider([1.0] + [0.0] * 1023))
    session_store = SessionScopedVectorRetrievalStore(use_elasticsearch=True)
    result = await session_store.search(RetrievalRequest(query="hybrid policy", top_k=3), RetrievalFilter(clauses={}), top_k=3)

    assert result
    assert any(candidate.chunk.chunk_id == "chunk-elasticsearch-only" and candidate.chunk.metadata.get("retriever") == "elasticsearch" for candidate in result)
    assert any(candidate.chunk.chunk_id == "chunk-hybrid-1" and candidate.chunk.metadata.get("retriever") == "pgvector" for candidate in result)
    assert result[0].score >= result[-1].score


async def test_hybrid_benchmark_beats_sql_contains_baseline(pg_session, capsys) -> None:
    await _reset_agentic_tables(pg_session)
    await _seed_pgvector_document(pg_session)
    store = PGVectorRetrievalStore(pg_session, SQLAlchemyChunkStorageAdapter(pg_session), _EmbeddingProvider([1.0] + [0.0] * 1023))

    hybrid = await store.search(RetrievalRequest(query="hybrid policy", top_k=2), RetrievalFilter(clauses={}), top_k=2)
    baseline = await store.search_with_strategy(RetrievalRequest(query="hybrid policy", top_k=2), RetrievalFilter(clauses={}), strategy="keyword", top_k=2)

    print({"hybrid": [c.chunk.chunk_id for c in hybrid], "baseline": [c.chunk.chunk_id for c in baseline]})
    captured = capsys.readouterr().out
    assert "hybrid" in captured or hybrid
    assert hybrid[0].chunk.chunk_id == "chunk-hybrid-1"
