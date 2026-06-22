"""Retrieval config and store boundary for role-aware retrieval."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.agentic.contracts.access_policy import UserAccessContext
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalOutcome, RetrievalRequest
from app.agentic.contracts.retrieval import RetrievalFilter
from app.agentic.pipeline.access_control import build_retrieval_filter, evaluate_access
from app.agentic.pipeline.retrieval.rerank import rerank_candidates


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int = 5
    score_threshold: float = 0.7
    max_evidence_tokens: int = 1200
    max_followup_document_ids: int = 8


class RetrievalStore(Protocol):
    async def search(
        self,
        request: RetrievalRequest,
        retrieval_filter: RetrievalFilter,
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        ...

    async def fetch_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        ...

    async def fetch_by_document_ids(self, document_ids: tuple[str, ...]) -> list[DocumentChunk]:
        ...


async def retrieve_evidence(
    store: RetrievalStore,
    request: RetrievalRequest,
    user_context: UserAccessContext,
    *,
    config: RetrievalConfig | None = None,
    last_cited_chunk_ids: tuple[str, ...] = (),
    last_cited_document_ids: tuple[str, ...] = (),
) -> RetrievalOutcome:
    config = config or RetrievalConfig(top_k=request.top_k)
    retrieval_filter = build_retrieval_filter(user_context)

    prioritized_chunks: list[DocumentChunk] = []
    if last_cited_chunk_ids:
        prioritized_chunks.extend(await store.fetch_by_chunk_ids(last_cited_chunk_ids))
    if last_cited_document_ids and len(prioritized_chunks) < config.max_followup_document_ids:
        prioritized_chunks.extend(await store.fetch_by_document_ids(last_cited_document_ids[: config.max_followup_document_ids]))

    authorized_priority = _filter_authorized(prioritized_chunks, user_context)
    prioritized_candidates = _chunks_to_candidates(authorized_priority, start_rank=1)

    search_candidates = await store.search(request, retrieval_filter, top_k=config.top_k)
    ranked = rerank_candidates([*prioritized_candidates, *search_candidates])

    filtered: list[RetrievalCandidate] = []
    total_tokens = 0
    seen_chunk_ids: set[str] = set()
    for candidate in ranked:
        if candidate.chunk.chunk_id in seen_chunk_ids:
            continue
        if candidate.score < config.score_threshold:
            continue
        if not evaluate_access(candidate.chunk, user_context).allowed:
            continue
        if not _has_citation_metadata(candidate.chunk):
            continue
        token_count = candidate.chunk.token_count or 0
        if total_tokens + token_count > config.max_evidence_tokens:
            continue
        filtered.append(candidate)
        seen_chunk_ids.add(candidate.chunk.chunk_id)
        total_tokens += token_count
        if len(filtered) >= config.top_k:
            break

    if not filtered:
        reason_code = "denied" if prioritized_chunks and not authorized_priority else "no_evidence"
        return RetrievalOutcome(status="denied" if reason_code == "denied" else "no_evidence", candidates=(), reason_code=reason_code)

    return RetrievalOutcome(status="ok", candidates=tuple(filtered), reason_code="ok")


def _filter_authorized(chunks: list[DocumentChunk], user_context: UserAccessContext) -> list[DocumentChunk]:
    return [chunk for chunk in chunks if evaluate_access(chunk, user_context).allowed]


def _chunks_to_candidates(chunks: list[DocumentChunk], *, start_rank: int) -> list[RetrievalCandidate]:
    candidates: list[RetrievalCandidate] = []
    rank = start_rank
    for chunk in chunks:
        candidates.append(RetrievalCandidate(chunk=chunk, score=1.0, rank=rank))
        rank += 1
    return candidates


def _has_citation_metadata(chunk: DocumentChunk) -> bool:
    citation = chunk.citation
    return (
        citation.page_number is not None
        or bool(citation.section_path)
        or citation.block_anchor is not None
    )
