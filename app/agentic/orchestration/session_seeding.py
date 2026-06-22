"""Pure helpers for seeding a new RAG session from a prior state."""
from __future__ import annotations

from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState


def build_next_session_state(
    previous_state: GraphState,
    *,
    request: RetrievalRequest,
    conversation_id: str | None = None,
) -> GraphState:
    return GraphState(
        request=request,
        conversation_id=conversation_id or previous_state.conversation_id,
        user_id=previous_state.user_id,
        thread_id=previous_state.thread_id,
        current_turn_index=(previous_state.current_turn_index or 0) + 1,
        current_user_message=request.query,
        recent_messages=previous_state.recent_messages,
        memory_summary=previous_state.memory_summary,
        current_topic=previous_state.current_topic,
        recent_cited_document_ids=previous_state.recent_cited_document_ids,
        recent_cited_chunk_ids=previous_state.recent_cited_chunk_ids,
        retrieval_hints=previous_state.retrieval_hints,
        last_answer_status=previous_state.last_answer_status,
        last_citations=previous_state.last_citations,
        last_cited_document_ids=previous_state.last_cited_document_ids,
        last_cited_chunk_ids=previous_state.last_cited_chunk_ids,
        user_context=previous_state.user_context,
        answer=None,
        metadata=previous_state.metadata,
    )
