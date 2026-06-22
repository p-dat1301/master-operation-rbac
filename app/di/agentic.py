"""Minimal in-memory conversation registry for agentic API."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.agentic.adapters.embeddings.default_embeddings import get_embedding_provider
from app.agentic.adapters.search.elasticsearch_client import build_agentic_elasticsearch_retriever
from app.agentic.adapters.storage.sqlalchemy_storage import SQLAlchemyChunkStorageAdapter
from app.agentic.adapters.vector_store.pgvector_retrieval_store import (
    PGVectorRetrievalStore,
    build_langchain_pgvector_retriever,
    document_to_retrieval_candidate,
)
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalRequest
from app.agentic.contracts.retrieval import RetrievalFilter
from app.agentic.orchestration.conversation_registry import ConversationRegistry
from app.agentic.pipeline.retrieval.core import RetrievalStore
from app.infrastructure.database.session import AsyncSessionLocal


class SessionScopedVectorRetrievalStore(RetrievalStore):
    def __init__(
        self,
        session_factory: async_sessionmaker = AsyncSessionLocal,
        *,
        strategy: str = "hybrid",
        use_elasticsearch: bool = False,
        pgvector_weight: float = 0.5,
        elasticsearch_weight: float = 0.5,
    ) -> None:
        self._session_factory = session_factory
        self._embedding_provider = get_embedding_provider()
        self._strategy = _normalize_retrieval_strategy(strategy)
        self._use_elasticsearch = use_elasticsearch
        self._pgvector_weight = pgvector_weight
        self._elasticsearch_weight = elasticsearch_weight

    async def search(
        self,
        request: RetrievalRequest,
        retrieval_filter: RetrievalFilter,
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        if self._strategy == "hybrid" and self._use_elasticsearch:
            return await self._hybrid_search(request, retrieval_filter, top_k=top_k)

        async with self._session_factory() as session:
            store = PGVectorRetrievalStore(
                session,
                SQLAlchemyChunkStorageAdapter(session),
                self._embedding_provider,
            )
            fallback_strategy = "vector" if self._strategy == "hybrid" else self._strategy
            return await store.search_with_strategy(
                request,
                retrieval_filter,
                strategy=fallback_strategy,
                top_k=top_k,
            )

    async def _hybrid_search(
        self,
        request: RetrievalRequest,
        retrieval_filter: RetrievalFilter,
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        try:
            pgvector_retriever = build_langchain_pgvector_retriever(
                session_factory=self._session_factory,
                embedding_provider=self._embedding_provider,
                top_k=top_k,
            )
            elasticsearch_retriever = build_agentic_elasticsearch_retriever(top_k=top_k)
            ensemble = EnsembleRetriever(
                retrievers=[pgvector_retriever, elasticsearch_retriever],
                weights=[self._pgvector_weight, self._elasticsearch_weight],
            )
            documents = await ensemble.ainvoke(request.query)
            return _documents_to_deterministic_candidates(documents, retrieval_filter, top_k=top_k)
        except Exception:
            # Fallback to vector-only if ES is down or hybrid fails
            async with self._session_factory() as session:
                store = PGVectorRetrievalStore(
                    session,
                    SQLAlchemyChunkStorageAdapter(session),
                    self._embedding_provider,
                )
                return await store.search_with_strategy(
                    request,
                    retrieval_filter,
                    strategy="vector",
                    top_k=top_k,
                )

    async def fetch_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        async with self._session_factory() as session:
            store = PGVectorRetrievalStore(
                session,
                SQLAlchemyChunkStorageAdapter(session),
                self._embedding_provider,
            )
            return await store.fetch_by_chunk_ids(chunk_ids)

    async def fetch_by_document_ids(self, document_ids: tuple[str, ...]) -> list[DocumentChunk]:
        async with self._session_factory() as session:
            store = PGVectorRetrievalStore(
                session,
                SQLAlchemyChunkStorageAdapter(session),
                self._embedding_provider,
            )
            return await store.fetch_by_document_ids(document_ids)



def _documents_to_deterministic_candidates(
    documents: list[Document],
    retrieval_filter: RetrievalFilter,
    *,
    top_k: int,
) -> list[RetrievalCandidate]:
    candidates: list[RetrievalCandidate] = []
    seen_chunk_ids: set[str] = set()
    for rank, document in enumerate(documents, start=1):
        chunk_id = str(document.metadata.get("chunk_id") or document.id or "")
        if not chunk_id or chunk_id in seen_chunk_ids:
            continue
        candidate = document_to_retrieval_candidate(document, rank=rank)
        if not _matches_retrieval_filter(candidate.chunk, retrieval_filter):
            continue
        if not _has_valid_citation(candidate.chunk):
            continue
        candidates.append(candidate)
        seen_chunk_ids.add(chunk_id)
        if len(candidates) >= top_k:
            break
    return candidates


def _matches_retrieval_filter(chunk: DocumentChunk, retrieval_filter: RetrievalFilter) -> bool:
    raw_clauses = getattr(retrieval_filter, "clauses", ())
    if not raw_clauses:
        return True

    clauses = (raw_clauses,) if isinstance(raw_clauses, dict) else tuple(raw_clauses)
    for clause in clauses:
        visibility_scope = clause.get("visibility_scope")
        if visibility_scope == "global":
            return True
        if visibility_scope == "owner" and chunk.access_policy.owner_id == clause.get("owner_id"):
            return True
        if visibility_scope == "department" and chunk.access_policy.department_id == clause.get("department_id"):
            return True
        if visibility_scope == "role":
            allowed_roles = set(chunk.access_policy.allowed_roles or ())
            required_roles = set(clause.get("allowed_roles_any") or ())
            if allowed_roles.intersection(required_roles):
                return True

    return False


def _has_valid_citation(chunk: DocumentChunk) -> bool:
    citation = chunk.citation
    return (
        citation.page_number is not None
        or bool(citation.section_path)
        or citation.block_anchor is not None
    )


def _normalize_retrieval_strategy(strategy: str) -> str:
    normalized = strategy.strip().lower()
    if normalized in {"vector", "keyword", "hybrid"}:
        return normalized
    return "hybrid"


@dataclass(slots=True)
class AgenticConversationService:
    registry: ConversationRegistry

    def create_conversation(self, *, user_id: int, title: str | None = None) -> dict[str, object]:
        conversation_id = f"conv-{uuid4().hex}"
        thread_id = f"thr-{uuid4().hex}"
        record = self.registry.register(
            conversation_id=conversation_id,
            user_id=user_id,
            thread_id=thread_id,
            title=title,
        )
        return {
            "conversation_id": record.conversation_id,
            "thread_id": record.thread_id,
            "user_id": record.user_id,
            "status": record.status,
            "title": record.title,
        }


def build_agentic_retrieval_store() -> RetrievalStore:
    return SessionScopedVectorRetrievalStore(
        strategy=settings.RAG_RETRIEVAL_STRATEGY,
        use_elasticsearch=settings.RAG_USE_ELASTICSEARCH,
    )
