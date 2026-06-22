"""Unit tests for Task 10 generation gateway integration."""
from __future__ import annotations

import pytest

from app.agentic.contracts.access_policy import AccessPolicyMetadata, Classification, UserAccessContext, VisibilityScope
from app.agentic.contracts.answer import AnswerCitation
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalRequest
from app.agentic.contracts.document import CitationMetadata
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.evidence_handoff import clear_retrieval_candidates, set_retrieval_candidates
from app.agentic.pipeline.answer_policy import GroundedAnswerPolicy
from app.agentic.orchestration.nodes.generate_answer import build_generate_answer_node


class FakeAnswerLLM:
    async def generate(self, *, query: str, evidence_text: str, citations, system_context: str | None = None) -> dict:
        return {
            "status": "answered",
            "answer": f"Answered: {query}",
            "citations": citations,
            "model_name": "fake-gateway-model",
            "model_version": "fake-v1",
            "metadata": {"gateway": "test"},
        }



def _state_with_evidence() -> GraphState:
    return GraphState(
        request=RetrievalRequest(query="What is this?", top_k=3),
        user_context=UserAccessContext(user_id=1),
        conversation_id="conv-1",
        retrieval_reason_code="ok",
    )


@pytest.mark.asyncio
async def test_grounded_answer_policy_rejects_unauthorized_citation() -> None:
    policy = GroundedAnswerPolicy()
    answer = AnswerCitation(chunk_id="bad", document_id="doc-1", page_number=1, section_path=())

    with pytest.raises(Exception):
        policy.validate(
            answer=__import__("app.agentic.contracts.answer", fromlist=["AnswerResult"]).AnswerResult(
                status="answered",
                answer="x",
                citations=(answer,),
                evidence_bundle=None,
            ),
            allowed_citations=(AnswerCitation(chunk_id="good", document_id="doc-1", page_number=1, section_path=()),),
        )


@pytest.mark.asyncio
async def test_generate_answer_node_returns_insufficient_evidence_without_evidence() -> None:
    state = _state_with_evidence()
    state.thread_id = "thr-test"
    clear_retrieval_candidates(state.thread_id)

    result = await build_generate_answer_node(FakeAnswerLLM())(state)

    assert result["last_answer_status"] == "insufficient_evidence"
    assert result["last_citations"] == ()
    assert result["retrieval_candidate_count"] == 0


@pytest.mark.asyncio
async def test_generate_answer_node_uses_gateway_answer() -> None:
    state = _state_with_evidence()
    state.thread_id = "thr-test"
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="authorized evidence",
        token_count=10,
        chunk_index=0,
        chunker_version="chunker-v1",
        source_type="pdf",
        mime_type="application/pdf",
        citation=CitationMetadata(page_number=1, section_path=("Section",), block_anchor="anchor-1"),
        access_policy=AccessPolicyMetadata(classification=Classification.PUBLIC, visibility_scope=VisibilityScope.GLOBAL),
    )
    candidate = RetrievalCandidate(chunk=chunk, score=1.0, rank=1)
    set_retrieval_candidates(state.thread_id, (candidate,))

    result = await build_generate_answer_node(FakeAnswerLLM())(state)

    assert result["last_answer_status"] == "answered"
    assert result["answer"].model_name == "fake-gateway-model"
    assert result["answer"].model_version == "fake-v1"
    assert result["answer"].evidence_bundle is None
    assert result["last_cited_chunk_ids"] == ("chunk-1",)
    assert result["last_citations"][0]["chunk_id"] == "chunk-1"
    assert result["retrieval_candidate_count"] == 1
