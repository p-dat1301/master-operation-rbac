"""Unit tests for role-aware retrieval."""
from __future__ import annotations

import pytest

from app.agentic.contracts import (
    AccessPolicyMetadata,
    Classification,
    DocumentChunk,
    RetrievalCandidate,
    RetrievalRequest,
    SourceMetadata,
    SourceType,
    UserAccessContext,
    VisibilityScope,
)
from app.agentic.contracts.document import CitationMetadata
from langchain_core.documents import Document

from app.agentic.contracts.retrieval import RetrievalFilter
from app.agentic.pipeline.retrieval import RetrievalConfig, retrieve_evidence
from app.di.agentic import SessionScopedVectorRetrievalStore


class FakeRetrievalStore:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = {chunk.chunk_id: chunk for chunk in chunks}

    async def search(self, request: RetrievalRequest, retrieval_filter, *, top_k: int) -> list[RetrievalCandidate]:
        chunks = list(self._chunks.values())[:top_k]
        return [RetrievalCandidate(chunk=chunk, score=0.95 - idx * 0.01, rank=idx + 1) for idx, chunk in enumerate(chunks)]

    async def fetch_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return [self._chunks[chunk_id] for chunk_id in chunk_ids if chunk_id in self._chunks]

    async def fetch_by_document_ids(self, document_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return [chunk for chunk in self._chunks.values() if chunk.document_id in set(document_ids)]


class FakeLangChainRetriever:
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.queries: list[str] = []

    async def ainvoke(self, query: str) -> list[Document]:
        self.queries.append(query)
        return self.documents


def _source() -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri="/tmp/retrieval.pdf",
        filename="retrieval.pdf",
    )


def _chunk(
    *,
    chunk_id: str,
    document_id: str,
    policy: AccessPolicyMetadata,
    token_count: int = 100,
    citation: CitationMetadata | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=f"content for {chunk_id}",
        token_count=token_count,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type=SourceType.UPLOADED_FILE.value,
        mime_type="application/pdf",
        citation=citation or CitationMetadata(page_number=1),
        access_policy=policy,
        metadata={},
    )


def _document_from_chunk(chunk: DocumentChunk, *, score: float | None = None, source: str) -> Document:
    return Document(
        id=chunk.chunk_id,
        page_content=chunk.text,
        metadata={
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "score": score,
            "token_count": chunk.token_count,
            "chunk_index": chunk.chunk_index,
            "chunker_version": chunk.chunker_version,
            "source_type": chunk.source_type,
            "mime_type": chunk.mime_type,
            "citation": chunk.citation.model_dump(),
            "access_policy": chunk.access_policy.model_dump(),
            "metadata": {"retriever": source, **chunk.metadata},
            "created_at": chunk.created_at,
        },
    )


@pytest.mark.asyncio
async def test_retrieve_evidence_allows_authorized_chunk() -> None:
    chunk = _chunk(
        chunk_id="chunk-allow",
        document_id="doc-allow",
        policy=AccessPolicyMetadata(
            classification=Classification.INTERNAL,
            visibility_scope=VisibilityScope.DEPARTMENT,
            department_id=10,
        ),
    )
    store = FakeRetrievalStore([chunk])
    request = RetrievalRequest(query="leave policy", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user, config=RetrievalConfig(top_k=5, score_threshold=0.7, max_evidence_tokens=1000))

    assert result.status == "ok"
    assert result.reason_code == "ok"
    assert result.candidates[0].chunk.chunk_id == "chunk-allow"


@pytest.mark.asyncio
async def test_retrieve_evidence_denies_restricted_chunk_for_wrong_department() -> None:
    chunk = _chunk(
        chunk_id="chunk-deny",
        document_id="doc-deny",
        policy=AccessPolicyMetadata(
            classification=Classification.RESTRICTED,
            visibility_scope=VisibilityScope.DEPARTMENT,
            department_id=11,
        ),
    )
    store = FakeRetrievalStore([chunk])
    request = RetrievalRequest(query="salary policy", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user)

    assert result.status == "no_evidence"
    assert result.reason_code == "no_evidence"
    assert result.candidates == ()


@pytest.mark.asyncio
async def test_retrieve_evidence_rechecks_fetch_by_chunk_id() -> None:
    chunk = _chunk(
        chunk_id="chunk-secret",
        document_id="doc-secret",
        policy=AccessPolicyMetadata(
            classification=Classification.CONFIDENTIAL,
            visibility_scope=VisibilityScope.OWNER,
            owner_id=99,
        ),
    )
    store = FakeRetrievalStore([chunk])
    request = RetrievalRequest(query="follow up", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user, last_cited_chunk_ids=("chunk-secret",))

    assert result.status == "denied"
    assert result.reason_code == "denied"
    assert result.candidates == ()


@pytest.mark.asyncio
async def test_retrieve_evidence_enforces_budget_and_threshold() -> None:
    chunk_1 = _chunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
        token_count=90,
    )
    chunk_2 = _chunk(
        chunk_id="chunk-2",
        document_id="doc-2",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
        token_count=90,
    )
    store = FakeRetrievalStore([chunk_1, chunk_2])
    request = RetrievalRequest(query="global docs", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user, config=RetrievalConfig(top_k=5, score_threshold=0.9, max_evidence_tokens=100))

    assert result.status == "ok"
    assert len(result.candidates) == 1
    assert result.candidates[0].chunk.chunk_id == "chunk-1"


@pytest.mark.asyncio
async def test_retrieve_evidence_uses_followup_documents_without_bypass() -> None:
    chunk = _chunk(
        chunk_id="chunk-doc",
        document_id="doc-follow",
        policy=AccessPolicyMetadata(
            classification=Classification.INTERNAL,
            visibility_scope=VisibilityScope.DEPARTMENT,
            department_id=10,
        ),
    )
    store = FakeRetrievalStore([chunk])
    request = RetrievalRequest(query="follow up", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user, last_cited_document_ids=("doc-follow",))

    assert result.status == "ok"
    assert result.candidates[0].chunk.document_id == "doc-follow"


@pytest.mark.asyncio
async def test_retrieve_evidence_excludes_chunk_without_citation_metadata() -> None:
    chunk = _chunk(
        chunk_id="chunk-no-citation",
        document_id="doc-no-citation",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
        citation=CitationMetadata(),
    )
    store = FakeRetrievalStore([chunk])
    request = RetrievalRequest(query="global docs", top_k=5)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    result = await retrieve_evidence(store, request, user)

    assert result.status == "no_evidence"
    assert result.candidates == ()


@pytest.mark.asyncio
async def test_session_scoped_vector_retrieval_store_dedups_and_preserves_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    allowed_chunk = _chunk(
        chunk_id="chunk-shared",
        document_id="doc-1",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
    )
    duplicate_doc = _document_from_chunk(allowed_chunk, score=1.0, source="elasticsearch")
    fake_docs = [duplicate_doc, _document_from_chunk(allowed_chunk, score=0.8, source="pgvector")]

    captured_ensemble_kwargs = {}

    class FakeEnsemble:
        async def ainvoke(self, query: str) -> list[Document]:
            assert query == "shared chunk"
            return fake_docs

    def build_fake_ensemble(**kwargs):
        captured_ensemble_kwargs.update(kwargs)
        return FakeEnsemble()

    monkeypatch.setattr("app.di.agentic.get_embedding_provider", lambda: object())
    monkeypatch.setattr("app.di.agentic.build_langchain_pgvector_retriever", lambda **kwargs: object())
    monkeypatch.setattr("app.di.agentic.build_agentic_elasticsearch_retriever", lambda **kwargs: object())
    monkeypatch.setattr("app.di.agentic.EnsembleRetriever", build_fake_ensemble)

    store = SessionScopedVectorRetrievalStore(use_elasticsearch=True, pgvector_weight=0.5, elasticsearch_weight=0.5)
    result = await store.search(
        RetrievalRequest(query="shared chunk", top_k=5),
        RetrievalFilter(clauses={"visibility_scope": "global"}),
        top_k=5,
    )

    assert captured_ensemble_kwargs["weights"] == [0.5, 0.5]
    assert len(captured_ensemble_kwargs["retrievers"]) == 2
    assert len(result) == 1
    assert result[0].chunk.chunk_id == "chunk-shared"
    assert result[0].chunk.citation.page_number == 1
    assert result[0].chunk.access_policy.classification == Classification.PUBLIC
    assert result[0].chunk.metadata["retriever"] == "elasticsearch"


@pytest.mark.asyncio
async def test_session_scoped_vector_retrieval_store_uses_ensemble_order_for_hybrid_ranking(monkeypatch: pytest.MonkeyPatch) -> None:
    lexical = _chunk(
        chunk_id="chunk-lexical",
        document_id="doc-lexical",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
    )
    semantic = _chunk(
        chunk_id="chunk-semantic",
        document_id="doc-semantic",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
    )
    fake_docs = [
        _document_from_chunk(lexical, score=0.9, source="elasticsearch"),
        _document_from_chunk(semantic, score=0.8, source="pgvector"),
    ]
    captured_queries: list[str] = []

    class FakeEnsemble:
        async def ainvoke(self, query: str) -> list[Document]:
            captured_queries.append(query)
            return fake_docs

    monkeypatch.setattr("app.di.agentic.get_embedding_provider", lambda: object())
    monkeypatch.setattr("app.di.agentic.build_langchain_pgvector_retriever", lambda **kwargs: object())
    monkeypatch.setattr("app.di.agentic.build_agentic_elasticsearch_retriever", lambda **kwargs: object())
    monkeypatch.setattr("app.di.agentic.EnsembleRetriever", lambda **kwargs: FakeEnsemble())

    store = SessionScopedVectorRetrievalStore(use_elasticsearch=True)
    result = await store.search(RetrievalRequest(query="lexical semantic", top_k=2), RetrievalFilter(clauses={}), top_k=2)

    assert captured_queries == ["lexical semantic"]
    assert [candidate.chunk.chunk_id for candidate in result] == ["chunk-lexical", "chunk-semantic"]
    assert [candidate.rank for candidate in result] == [1, 2]


@pytest.mark.asyncio
async def test_session_scoped_vector_retrieval_store_falls_back_to_vector_only(monkeypatch: pytest.MonkeyPatch) -> None:
    chunk = _chunk(
        chunk_id="chunk-vector",
        document_id="doc-vector",
        policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
    )
    fake_store = FakeRetrievalStore([chunk])

    class FakePGStore:
        async def search_with_strategy(self, request, retrieval_filter, *, strategy: str, top_k: int) -> list[RetrievalCandidate]:
            assert strategy == "vector"
            return await fake_store.search(request, retrieval_filter, top_k=top_k)

    monkeypatch.setattr("app.di.agentic.get_embedding_provider", lambda: object())
    monkeypatch.setattr("app.di.agentic.PGVectorRetrievalStore", lambda *args, **kwargs: FakePGStore())

    store = SessionScopedVectorRetrievalStore(use_elasticsearch=False)
    result = await store.search(RetrievalRequest(query="vector only", top_k=5), RetrievalFilter(), top_k=5)

    assert len(result) == 1
    assert result[0].chunk.chunk_id == "chunk-vector"
