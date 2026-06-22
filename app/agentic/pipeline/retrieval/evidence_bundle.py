"""Retrieval bundle helpers."""
from __future__ import annotations

from app.agentic.contracts.chunk import RetrievalCandidate, RetrievalOutcome, RetrievalRequest
from app.agentic.contracts.retrieval import EvidenceBundle


def build_evidence_bundle(
    request: RetrievalRequest,
    candidates: tuple[RetrievalCandidate, ...],
    *,
    reason_code: str,
) -> EvidenceBundle:
    return EvidenceBundle(request=request, evidence=candidates, reason_code=reason_code)


__all__ = ["build_evidence_bundle", "EvidenceBundle", "RetrievalCandidate", "RetrievalOutcome", "RetrievalRequest"]
