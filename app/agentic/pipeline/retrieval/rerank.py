"""Lightweight retrieval reranking helpers."""
from __future__ import annotations

from app.agentic.contracts.chunk import RetrievalCandidate


def rerank_candidates(candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
    return sorted(candidates, key=lambda candidate: (-candidate.score, candidate.rank, candidate.chunk.chunk_id))
