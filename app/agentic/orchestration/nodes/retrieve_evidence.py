from __future__ import annotations

from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.evidence_handoff import set_retrieval_candidates
from app.agentic.orchestration.langfuse_logger import LangfuseTurnLogger, NullLangfuseTurnLogger
from app.agentic.pipeline.retrieval.core import RetrievalConfig, retrieve_evidence


def build_retrieve_evidence_node(retrieval_store, langfuse_logger: LangfuseTurnLogger | None = None):
    turn_logger = langfuse_logger or NullLangfuseTurnLogger()

    async def retrieve_evidence_node(state: GraphState) -> dict:
        outcome = await retrieve_evidence(
            retrieval_store,
            state.request,
            state.user_context,
            config=RetrievalConfig(top_k=state.request.top_k),
            last_cited_chunk_ids=state.last_cited_chunk_ids,
            last_cited_document_ids=state.last_cited_document_ids,
        )
        if state.thread_id is None:
            raise ValueError("missing_thread_id_for_retrieval_handoff")
        set_retrieval_candidates(state.thread_id, outcome.candidates)
        await turn_logger.log_retrieved_chunks(
            trace_id=state.langfuse_trace_id,
            request=state.request,
            candidates=outcome.candidates,
            reason_code=outcome.reason_code,
        )
        return {
            "retrieval_candidate_count": len(outcome.candidates),
            "retrieval_reason_code": outcome.reason_code,
        }

    return retrieve_evidence_node
