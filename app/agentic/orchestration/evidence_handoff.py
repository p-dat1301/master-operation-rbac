"""Turn-local retrieval evidence handoff for LangGraph nodes."""
from __future__ import annotations

from app.agentic.contracts.chunk import RetrievalCandidate

_retrieval_candidates_by_thread: dict[str, tuple[RetrievalCandidate, ...]] = {}


def set_retrieval_candidates(thread_id: str, candidates: tuple[RetrievalCandidate, ...]) -> None:
    _retrieval_candidates_by_thread[thread_id] = candidates


def get_retrieval_candidates(thread_id: str) -> tuple[RetrievalCandidate, ...]:
    return _retrieval_candidates_by_thread.get(thread_id, ())


def clear_retrieval_candidates(thread_id: str) -> None:
    _retrieval_candidates_by_thread.pop(thread_id, None)
