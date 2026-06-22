"""Retrieval vector store adapter for agentic RAG."""
from __future__ import annotations

from typing import Any, Mapping, Protocol

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, PrivateAttr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agentic.adapters.storage.models import AgenticChunkEmbeddingModel, AgenticChunkModel
from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.document import CitationMetadata
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalRequest
from app.agentic.contracts.retrieval import RetrievalFilter
from app.agentic.pipeline.indexing import EmbeddingProvider
from app.agentic.pipeline.retrieval.core import RetrievalStore
from app.core.config import settings

try:  # pragma: no cover - optional dependency path
    from langchain_postgres import PGEngine
except ImportError:  # pragma: no cover
    PGEngine = Any  # type: ignore[misc, assignment]


class _EmbeddingSearchSessionFactory(Protocol):
    def __call__(self) -> AsyncSession: ...


class LangChainPGVectorRetriever(BaseRetriever):
    """LangChain retriever over the existing agentic pgvector tables.

    This is the Task 5 bridge for EnsembleRetriever: it returns LangChain
    Documents while preserving the project's chunk/citation/access metadata.
    Access filtering intentionally stays in ``retrieve_evidence`` after these
    documents are converted back into RetrievalCandidate objects.
    """

    top_k: int = 5
    _session_factory: _EmbeddingSearchSessionFactory = PrivateAttr()
    _embedding_provider: EmbeddingProvider = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        *,
        session_factory: _EmbeddingSearchSessionFactory,
        embedding_provider: EmbeddingProvider,
        top_k: int = 5,
    ) -> None:
        super().__init__(top_k=top_k)
        self._session_factory = session_factory
        self._embedding_provider = embedding_provider

    async def _aget_relevant_documents(self, query: str, *, run_manager: Any = None) -> list[Document]:
        query_embedding = await _embed_query(self._embedding_provider, query)
        async with self._session_factory() as session:
            rows = await _select_embedding_rows(session, query_embedding, top_k=self.top_k)
        return [map_pgvector_row_to_document(row) for row in rows]

    def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> list[Document]:
        raise NotImplementedError("LangChainPGVectorRetriever is async-only; use ainvoke/aget_relevant_documents")


def create_langchain_pgvector_engine(*, database_url: str | None = None) -> Any:
    """Create a langchain-postgres PGEngine from the existing DB URL."""
    _require_langchain_postgres_dependencies()
    return PGEngine.from_connection_string(url=database_url or settings.DATABASE_URL)


def build_langchain_pgvector_retriever(
    *,
    session_factory: async_sessionmaker | _EmbeddingSearchSessionFactory,
    embedding_provider: EmbeddingProvider,
    top_k: int = 5,
) -> LangChainPGVectorRetriever:
    """Build the LangChain semantic retriever backed by existing pgvector data."""
    return LangChainPGVectorRetriever(
        session_factory=session_factory,
        embedding_provider=embedding_provider,
        top_k=top_k,
    )


def document_to_retrieval_candidate(document: Document, *, score: float | None = None, rank: int = 1) -> RetrievalCandidate:
    """Convert a LangChain Document from this retriever back to project evidence."""
    return RetrievalCandidate(
        chunk=document_to_chunk(document),
        score=float(score if score is not None else document.metadata.get("score", 1.0)),
        rank=rank,
    )


def document_to_chunk(document: Document) -> DocumentChunk:
    metadata = dict(document.metadata)
    return DocumentChunk(
        chunk_id=str(metadata["chunk_id"]),
        document_id=str(metadata["document_id"]),
        text=document.page_content,
        token_count=metadata.get("token_count"),
        chunk_index=int(metadata.get("chunk_index", 0)),
        chunker_version=str(metadata.get("chunker_version", "")),
        source_type=str(metadata.get("source_type", "")),
        mime_type=str(metadata.get("mime_type", "")),
        citation=CitationMetadata.model_validate(metadata.get("citation") or {}),
        access_policy=AccessPolicyMetadata.model_validate(metadata.get("access_policy") or {}),
        metadata=dict(metadata.get("metadata") or {}),
        created_at=metadata.get("created_at"),
    )


def map_pgvector_row_to_document(row: Mapping[str, Any] | Any) -> Document:
    """Map existing agentic chunk/embedding rows into LangChain Documents."""
    row_dict = _row_to_dict(row)
    metadata = {
        "chunk_id": row_dict["chunk_id"],
        "document_id": row_dict["document_id"],
        "score": row_dict.get("score"),
        "token_count": row_dict.get("token_count"),
        "chunk_index": row_dict.get("chunk_index"),
        "chunker_version": row_dict.get("chunker_version"),
        "source_type": row_dict.get("source_type"),
        "mime_type": row_dict.get("mime_type"),
        "citation": row_dict.get("citation") or {},
        "access_policy": row_dict.get("access_policy") or {},
        "metadata": row_dict.get("chunk_metadata") or {},
        "created_at": row_dict.get("created_at"),
    }
    return Document(id=str(row_dict["chunk_id"]), page_content=str(row_dict.get("text") or ""), metadata=metadata)


class PGVectorRetrievalStore(RetrievalStore):
    def __init__(self, session: AsyncSession, chunk_store, embedding_provider: EmbeddingProvider) -> None:
        self._session = session
        self._chunk_store = chunk_store
        self._embedding_provider = embedding_provider
        self._langchain_retriever = build_langchain_pgvector_retriever(
            session_factory=_SingleSessionFactory(session),
            embedding_provider=embedding_provider,
        )

    async def search(
        self,
        request: RetrievalRequest,
        retrieval_filter: RetrievalFilter,
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        return await self.search_with_strategy(
            request,
            retrieval_filter,
            strategy="hybrid",
            top_k=top_k,
        )

    async def search_with_strategy(
        self,
        request: RetrievalRequest,
        retrieval_filter: RetrievalFilter,
        *,
        strategy: str,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        if strategy == "vector":
            return await self._vector_search(request, top_k=top_k)
        if strategy == "keyword":
            return await self._vector_only_fallback(request, top_k=top_k)
        if strategy != "hybrid":
            raise ValueError(f"Unsupported retrieval strategy: {strategy}")

        try:
            vector_candidates = await self._vector_search(request, top_k=top_k)
        except Exception:
            return await self._vector_only_fallback(request, top_k=top_k)

        return vector_candidates

    async def _vector_search(self, request: RetrievalRequest, *, top_k: int) -> list[RetrievalCandidate]:
        self._langchain_retriever.top_k = top_k
        documents = await self._langchain_retriever.ainvoke(request.query)
        return [
            document_to_retrieval_candidate(document, rank=rank)
            for rank, document in enumerate(documents, start=1)
        ]

    async def _vector_only_fallback(self, request: RetrievalRequest, *, top_k: int) -> list[RetrievalCandidate]:
        try:
            return await self._vector_search(request, top_k=top_k)
        except Exception:
            return []

    async def fetch_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return await self._chunk_store.get_many_by_chunk_ids(chunk_ids)

    async def fetch_by_document_ids(self, document_ids: tuple[str, ...]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document_id in document_ids:
            chunks.extend(await self._chunk_store.list_by_document(document_id))
        return chunks


def _merge_candidates(
    vector_candidates: list[RetrievalCandidate],
    keyword_candidates: list[RetrievalCandidate],
    *,
    top_k: int,
) -> list[RetrievalCandidate]:
    merged: dict[str, RetrievalCandidate] = {}
    for source_candidates in (vector_candidates, keyword_candidates):
        for candidate in source_candidates:
            chunk_id = candidate.chunk.chunk_id
            existing = merged.get(chunk_id)
            if existing is None:
                merged[chunk_id] = candidate
                continue
            merged[chunk_id] = RetrievalCandidate(
                chunk=candidate.chunk,
                score=min(1.0, max(existing.score, candidate.score)),
                rank=min(existing.rank, candidate.rank),
            )
    return sorted(merged.values(), key=lambda candidate: (-candidate.score, candidate.rank, candidate.chunk.chunk_id))[:top_k]


def _model_to_chunk(model: AgenticChunkModel) -> DocumentChunk:
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


class _SingleSessionFactory:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def __call__(self) -> "_SingleSessionContext":
        return _SingleSessionContext(self._session)


class _SingleSessionContext:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


async def _embed_query(embedding_provider: EmbeddingProvider, query: str) -> list[float]:
    embeddings = await embedding_provider.embed([query])
    if not embeddings:
        return []
    return embeddings[0]


async def _select_embedding_rows(session: AsyncSession, query_embedding: list[float], *, top_k: int) -> list[Any]:
    if not query_embedding:
        return []
    distance = AgenticChunkEmbeddingModel.embedding.cosine_distance(query_embedding).label("distance")
    score = (1.0 - AgenticChunkEmbeddingModel.embedding.cosine_distance(query_embedding)).label("score")
    stmt = (
        select(
            AgenticChunkEmbeddingModel.chunk_id,
            AgenticChunkEmbeddingModel.document_id,
            AgenticChunkModel.text,
            AgenticChunkModel.token_count,
            AgenticChunkModel.chunk_index,
            AgenticChunkModel.chunker_version,
            AgenticChunkModel.source_type,
            AgenticChunkModel.mime_type,
            AgenticChunkModel.citation,
            AgenticChunkModel.access_policy,
            AgenticChunkModel.chunk_metadata,
            AgenticChunkModel.created_at,
            distance,
            score,
        )
        .join(AgenticChunkModel, AgenticChunkModel.chunk_id == AgenticChunkEmbeddingModel.chunk_id)
        .order_by("distance")
        .limit(top_k)
    )
    result = await session.execute(stmt)
    return result.all()


def _row_to_dict(row: Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    mapping = getattr(row, "_mapping", None)
    if mapping is not None:
        return dict(mapping)
    return dict(vars(row))


def _require_langchain_postgres_dependencies() -> None:
    if PGEngine is Any:  # type: ignore[comparison-overlap]
        raise RuntimeError("langchain-postgres must be installed")
