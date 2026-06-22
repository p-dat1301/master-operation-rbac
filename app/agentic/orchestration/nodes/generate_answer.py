"""Generate answer orchestration node."""
from __future__ import annotations

from app.agentic.adapters.llm import build_default_answer_llm
from app.agentic.contracts.answer import AnswerCitation, AnswerResult
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.evidence_handoff import clear_retrieval_candidates, get_retrieval_candidates
from app.agentic.pipeline.answer_policy import GroundedAnswerPolicy


def build_generate_answer_node(answer_llm=None):
    answer_llm = answer_llm or build_default_answer_llm()

    async def generate_answer_node(state: GraphState) -> dict:
        if state.thread_id is None:
            raise ValueError("missing_thread_id_for_generation_handoff")
        candidates = get_retrieval_candidates(state.thread_id)
        citations = tuple(
            AnswerCitation(
                chunk_id=item.chunk.chunk_id,
                document_id=item.chunk.document_id,
                page_number=item.chunk.citation.page_number,
                section_path=item.chunk.citation.section_path,
            )
            for item in candidates
        )

        if not citations:
            clear_retrieval_candidates(state.thread_id)
            answer = AnswerResult(
                status="insufficient_evidence",
                answer="Insufficient evidence.",
                citations=(),
                evidence_bundle=None,
            )
            return {
                "answer": answer,
                "last_answer_status": answer.status,
                "last_cited_chunk_ids": (),
                "last_cited_document_ids": (),
                "last_citations": (),
                "retrieval_candidate_count": 0,
                "retrieval_reason_code": state.retrieval_reason_code,
            }

        policy = GroundedAnswerPolicy()
        evidence_text = policy.build_evidence_text_from_candidates(candidates)
        llm_response = await answer_llm.generate(
            query=state.request.query,
            evidence_text=evidence_text,
            citations=citations,
            system_context=policy.build_system_context(),
        )
        answer = AnswerResult(
            status=llm_response["status"],
            answer=llm_response["answer"],
            citations=llm_response["citations"],
            evidence_bundle=None,
            model_name=llm_response.get("model_name"),
            model_version=llm_response.get("model_version"),
            metadata=llm_response.get("metadata", {}),
        )
        policy.validate(answer, citations)
        clear_retrieval_candidates(state.thread_id)
        return {
            "answer": answer,
            "last_answer_status": answer.status,
            "last_cited_chunk_ids": tuple(citation.chunk_id for citation in citations),
            "last_cited_document_ids": tuple(citation.document_id for citation in citations),
            "last_citations": tuple(citation.model_dump(mode="json") for citation in citations),
            "retrieval_candidate_count": len(candidates),
            "retrieval_reason_code": state.retrieval_reason_code,
        }

    return generate_answer_node


async def generate_answer_node(state: GraphState) -> dict:
    return await build_generate_answer_node()(state)
