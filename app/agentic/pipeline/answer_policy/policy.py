"""Grounded answer policy for the agentic pipeline."""
from __future__ import annotations

from app.agentic.contracts.answer import AnswerCitation, AnswerResult
from app.agentic.contracts.chunk import RetrievalCandidate
from app.agentic.contracts.retrieval import EvidenceBundle


class GroundedAnswerPolicyError(ValueError):
    pass


class GroundedAnswerPolicy:
    def build_system_context(self) -> str:
        return (
            "You are a grounded answer generator for an AI assistant. "
            "Use only the provided authorized evidence. "
            "Do not invent citations or use external knowledge."
        )

    def build_evidence_text(self, evidence_bundle: EvidenceBundle) -> str:
        return "\n\n".join(
            f"[{candidate.chunk.chunk_id}] {candidate.chunk.text}"
            for candidate in evidence_bundle.evidence
        )

    def build_evidence_text_from_candidates(self, candidates: tuple[RetrievalCandidate, ...]) -> str:
        return "\n\n".join(f"[{candidate.chunk.chunk_id}] {candidate.chunk.text}" for candidate in candidates)

    def validate(self, answer: AnswerResult, allowed_citations: tuple[AnswerCitation, ...]) -> AnswerResult:
        allowed = {citation.chunk_id for citation in allowed_citations}
        for citation in answer.citations:
            if citation.chunk_id not in allowed:
                raise GroundedAnswerPolicyError(f"citation_not_authorized:{citation.chunk_id}")
        return answer
