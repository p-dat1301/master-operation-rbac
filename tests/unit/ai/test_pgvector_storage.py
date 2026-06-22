"""Tests for SQLAlchemy-backed agentic storage adapters."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.agentic.adapters.storage.local_storage import LocalChunkStorageAdapter
from app.agentic.adapters.storage.sqlalchemy_storage import SQLAlchemyChunkStorageAdapter, SQLAlchemyDocumentStorageAdapter
from app.agentic.adapters.vector_store.pgvector_retrieval_store import (
    LangChainPGVectorRetriever,
    PGVectorRetrievalStore,
    build_langchain_pgvector_retriever,
    document_to_chunk,
    document_to_retrieval_candidate,
    map_pgvector_row_to_document,
)
from app.agentic.adapters.vector_store.pgvector_store import PGVectorStoreAdapter
from app.agentic.contracts.access_policy import AccessPolicyMetadata, Classification, VisibilityScope
from app.agentic.contracts.chunk import DocumentChunk, RetrievalRequest
from app.agentic.contracts.document import CitationMetadata, DocumentRecord
from app.agentic.contracts.retrieval import RetrievalFilter


class _ScalarResultStub:
    def __init__(self, rows) -> None:
        self._rows = rows

    def all(self):
        return self._rows


class _ResultStub:
    def __init__(self, rows) -> None:
        self._rows = rows

    def scalars(self):
        return _ScalarResultStub(self._rows)

    def all(self):
        return self._rows


class _SessionStub:
    def __init__(self, rows=None) -> None:
        self.executed = []
        self.flushed = False
        self.deleted = []
        self.rows = rows or []
        self.last_stmt = None

    async def execute(self, stmt):
        self.last_stmt = stmt
        self.executed.append(stmt)
        if self.rows and isinstance(self.rows[0], list):
            rows = self.rows.pop(0)
        else:
            rows = self.rows
        return _ResultStub(rows)

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


@pytest.mark.asyncio
async def test_chunk_storage_fetch_many_by_chunk_ids_preserves_input_order() -> None:
    session = _SessionStub()
    adapter = SQLAlchemyChunkStorageAdapter(session)
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
        citation=CitationMetadata(page_number=1),
        access_policy=access_policy,
        metadata={},
        created_at=datetime.now(timezone.utc),
    )
    session.rows = [SimpleNamespace(**{
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
        "chunk_metadata": chunk.metadata,
        "created_at": chunk.created_at,
    })]

    result = await adapter.get_many_by_chunk_ids(("chunk-1",))

    assert result[0].chunk_id == "chunk-1"


@pytest.mark.asyncio
async def test_pgvector_retrieval_store_returns_vector_candidates_only() -> None:
    access_policy = AccessPolicyMetadata(classification=Classification.INTERNAL, visibility_scope=VisibilityScope.GLOBAL)
    chunk_1 = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="hello",
        token_count=5,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=CitationMetadata(page_number=1),
        access_policy=access_policy,
        metadata={"source_id": "doc-1"},
        created_at=datetime.now(timezone.utc),
    )
    chunk_2 = DocumentChunk(
        chunk_id="chunk-2",
        document_id="doc-2",
        text="hello second",
        token_count=5,
        chunk_index=1,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=CitationMetadata(page_number=4),
        access_policy=access_policy,
        metadata={"source_id": "doc-2"},
        created_at=datetime.now(timezone.utc),
    )
    embedding_rows = [
        SimpleNamespace(
            chunk_id="chunk-2",
            document_id="doc-2",
            text=chunk_2.text,
            token_count=chunk_2.token_count,
            chunk_index=chunk_2.chunk_index,
            chunker_version=chunk_2.chunker_version,
            source_type=chunk_2.source_type,
            mime_type=chunk_2.mime_type,
            citation=chunk_2.citation.model_dump(mode="json"),
            access_policy=chunk_2.access_policy.model_dump(mode="json"),
            chunk_metadata=chunk_2.metadata,
            created_at=chunk_2.created_at,
            distance=0.02,
            score=0.98,
        ),
        SimpleNamespace(
            chunk_id="chunk-1",
            document_id="doc-1",
            text=chunk_1.text,
            token_count=chunk_1.token_count,
            chunk_index=chunk_1.chunk_index,
            chunker_version=chunk_1.chunker_version,
            source_type=chunk_1.source_type,
            mime_type=chunk_1.mime_type,
            citation=chunk_1.citation.model_dump(mode="json"),
            access_policy=chunk_1.access_policy.model_dump(mode="json"),
            chunk_metadata=chunk_1.metadata,
            created_at=chunk_1.created_at,
            distance=0.05,
            score=0.95,
        ),
    ]
    session = _SessionStub(rows=[embedding_rows])
    chunk_store = LocalChunkStorageAdapter()
    await chunk_store.upsert_many((chunk_1, chunk_2))

    class _EmbeddingProvider:
        async def embed(self, texts):
            return [[0.1] * 1024]

    store = PGVectorRetrievalStore(session, chunk_store, _EmbeddingProvider())
    result = await store.search(RetrievalRequest(query="hello", top_k=2), RetrievalFilter(clauses={}), top_k=2)

    assert [candidate.chunk.chunk_id for candidate in result] == ["chunk-2", "chunk-1"]
    assert [candidate.rank for candidate in result] == [1, 2]
    assert result[1].score == pytest.approx(0.95)
    assert result[0].score == pytest.approx(0.98)
    assert result[0].chunk.citation.page_number == 4
    assert result[0].chunk.metadata["source_id"] == "doc-2"


@pytest.mark.asyncio
async def test_pgvector_retrieval_store_falls_back_to_empty_when_vector_search_returns_empty() -> None:
    session = _SessionStub(rows=[[]])
    chunk_store = LocalChunkStorageAdapter()

    class _EmptyEmbeddingProvider:
        async def embed(self, texts):
            return [[0.1] * 1024]

    store = PGVectorRetrievalStore(session, chunk_store, _EmptyEmbeddingProvider())
    result = await store.search(RetrievalRequest(query="vector empty fallback", top_k=3), RetrievalFilter(clauses={}), top_k=3)

    assert result == []


@pytest.mark.asyncio
async def test_pgvector_retrieval_store_returns_empty_when_embedding_fails() -> None:
    session = _SessionStub(rows=[])
    chunk_store = LocalChunkStorageAdapter()

    class _FailingEmbeddingProvider:
        async def embed(self, texts):
            raise RuntimeError("vector unavailable")

    store = PGVectorRetrievalStore(session, chunk_store, _FailingEmbeddingProvider())
    result = await store.search(RetrievalRequest(query="hybrid fallback", top_k=5), RetrievalFilter(clauses={}), top_k=5)

    assert result == []


@pytest.mark.asyncio
async def test_langchain_pgvector_retriever_returns_documents_with_project_metadata() -> None:
    access_policy = AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL)
    citation = CitationMetadata(page_number=9, section_path=("Semantic",), block_anchor="block-semantic")
    row = SimpleNamespace(
        chunk_id="chunk-semantic",
        document_id="doc-semantic",
        text="semantic pgvector retrieval",
        token_count=7,
        chunk_index=2,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=citation.model_dump(mode="json"),
        access_policy=access_policy.model_dump(mode="json"),
        chunk_metadata={"source_id": "doc-semantic", "citation_label": "p.9"},
        created_at=datetime.now(timezone.utc),
        score=0.91,
    )
    session = _SessionStub(rows=[[row]])

    class _EmbeddingProvider:
        async def embed(self, texts):
            return [[0.1] * 1024]

    retriever = build_langchain_pgvector_retriever(
        session_factory=lambda: _AsyncSessionContext(session),
        embedding_provider=_EmbeddingProvider(),
        top_k=1,
    )

    documents = await retriever.ainvoke("semantic retrieval")

    assert isinstance(retriever, LangChainPGVectorRetriever)
    assert len(documents) == 1
    assert documents[0].id == "chunk-semantic"
    assert documents[0].page_content == "semantic pgvector retrieval"
    assert documents[0].metadata["chunk_id"] == "chunk-semantic"
    assert documents[0].metadata["document_id"] == "doc-semantic"
    assert documents[0].metadata["citation"] == citation.model_dump(mode="json")
    assert documents[0].metadata["access_policy"] == access_policy.model_dump(mode="json")
    assert documents[0].metadata["metadata"] == {"source_id": "doc-semantic", "citation_label": "p.9"}


@pytest.mark.asyncio
async def test_pgvector_retrieval_store_vector_strategy_uses_langchain_documents_as_candidates() -> None:
    access_policy = AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL)
    citation = CitationMetadata(page_number=10)
    row = SimpleNamespace(
        chunk_id="chunk-candidate",
        document_id="doc-candidate",
        text="candidate conversion",
        token_count=6,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=citation.model_dump(mode="json"),
        access_policy=access_policy.model_dump(mode="json"),
        chunk_metadata={"source_id": "doc-candidate"},
        created_at=datetime.now(timezone.utc),
        score=0.88,
    )
    session = _SessionStub(rows=[[row]])
    chunk_store = LocalChunkStorageAdapter()

    class _EmbeddingProvider:
        async def embed(self, texts):
            return [[0.1] * 1024]

    store = PGVectorRetrievalStore(session, chunk_store, _EmbeddingProvider())
    result = await store.search_with_strategy(RetrievalRequest(query="candidate", top_k=1), RetrievalFilter(clauses={}), strategy="vector", top_k=1)

    assert len(result) == 1
    assert result[0].chunk.chunk_id == "chunk-candidate"
    assert result[0].chunk.citation.page_number == 10
    assert result[0].chunk.access_policy.visibility_scope == VisibilityScope.GLOBAL
    assert result[0].chunk.metadata == {"source_id": "doc-candidate"}
    assert result[0].score == pytest.approx(0.88)


def test_pgvector_document_conversion_preserves_citation_and_access_policy_metadata() -> None:
    access_policy = AccessPolicyMetadata(classification=Classification.INTERNAL, visibility_scope=VisibilityScope.GLOBAL)
    citation = CitationMetadata(page_number=11, block_anchor="anchor")
    document = map_pgvector_row_to_document(SimpleNamespace(
        chunk_id="chunk-doc",
        document_id="doc-doc",
        text="doc conversion",
        token_count=4,
        chunk_index=1,
        chunker_version="chunker-v1",
        source_type="uploaded_file",
        mime_type="application/pdf",
        citation=citation.model_dump(mode="json"),
        access_policy=access_policy.model_dump(mode="json"),
        chunk_metadata={"k": "v"},
        created_at=datetime.now(timezone.utc),
        score=0.77,
    ))

    chunk = document_to_chunk(document)
    candidate = document_to_retrieval_candidate(document, rank=3)

    assert chunk.chunk_id == "chunk-doc"
    assert chunk.citation.block_anchor == "anchor"
    assert chunk.access_policy.classification == Classification.INTERNAL
    assert chunk.metadata == {"k": "v"}
    assert candidate.chunk.chunk_id == "chunk-doc"
    assert candidate.rank == 3
    assert candidate.score == pytest.approx(0.77)


class _AsyncSessionContext:
    def __init__(self, session) -> None:
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return None
