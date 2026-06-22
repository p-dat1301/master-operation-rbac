"""Langfuse observability helpers for RAG turns."""
from __future__ import annotations

from typing import Protocol

from app.agentic.contracts.chunk import RetrievalCandidate, RetrievalRequest


class LangfuseTurnLogger(Protocol):
    async def log_retrieved_chunks(
        self,
        *,
        trace_id: str | None,
        request: RetrievalRequest,
        candidates: tuple[RetrievalCandidate, ...],
        reason_code: str,
    ) -> None:
        """Record full retrieval payload for a single turn."""
        ...


class NullLangfuseTurnLogger:
    async def log_retrieved_chunks(
        self,
        *,
        trace_id: str | None,
        request: RetrievalRequest,
        candidates: tuple[RetrievalCandidate, ...],
        reason_code: str,
    ) -> None:
        return None
