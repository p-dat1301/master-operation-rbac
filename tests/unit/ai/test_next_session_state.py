from __future__ import annotations

from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.session_seeding import build_next_session_state


def test_build_next_session_state_carries_previous_context_but_clears_transient_outputs() -> None:
    previous = GraphState(
        request=RetrievalRequest(query="question-1", top_k=3),
        conversation_id="conv-1",
        thread_id="thr-1",
        user_id=7,
        current_turn_index=1,
        current_user_message="question-1",
        recent_messages=[{"role": "user", "content": "question-1"}],
        current_topic="topic-1",
        last_user_question="question-1",
        last_answer_status="answered",
        last_cited_document_ids=("doc-1",),
        last_cited_chunk_ids=("chunk-1",),
        last_citations=({"chunk_id": "chunk-1"},),
        recent_cited_document_ids=("doc-1",),
        recent_cited_chunk_ids=("chunk-1",),
        memory_summary="summary-1",
        retrieval_hints={"hint": "value"},
        metadata={
            "origin": "test",
            "audit_events": [{"event": "done"}],
            "policy_version": "policy-v1",
            "index_version": "index-v1",
        },
    )

    new_state = build_next_session_state(
        previous,
        request=RetrievalRequest(query="question-2", top_k=5),
        conversation_id="conv-1",
    )

    assert new_state.request.query == "question-2"
    assert new_state.conversation_id == "conv-1"
    assert new_state.thread_id == "thr-1"
    assert new_state.user_id == 7
    assert new_state.current_turn_index == 2
    assert new_state.current_user_message == "question-2"
    assert new_state.recent_messages == [{"role": "user", "content": "question-1"}]
    assert new_state.current_topic == "topic-1"
    assert new_state.last_answer_status == "answered"
    assert new_state.last_cited_document_ids == ("doc-1",)
    assert new_state.last_cited_chunk_ids == ("chunk-1",)
    assert new_state.last_citations == ({"chunk_id": "chunk-1"},)
    assert new_state.recent_cited_document_ids == ("doc-1",)
    assert new_state.recent_cited_chunk_ids == ("chunk-1",)
    assert new_state.memory_summary == "summary-1"
    assert new_state.retrieval_hints == {"hint": "value"}
    assert new_state.audit_events == [{"event": "done"}]
    assert new_state.policy_version == "policy-v1"
    assert new_state.index_version == "index-v1"
    assert new_state.metadata == {
        "origin": "test",
        "audit_events": [{"event": "done"}],
        "policy_version": "policy-v1",
        "index_version": "index-v1",
    }
    assert new_state.answer is None
