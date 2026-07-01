from __future__ import annotations

import pytest

from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.conversation_registry import ConversationAccessDenied, ConversationRegistry
from app.agentic.orchestration.session_flow import start_next_rag_session


@pytest.mark.asyncio
async def test_start_next_rag_session_reuses_conversation_thread_and_registers_turn() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    observed: dict[str, object] = {}

    async def load_previous_state(thread_id: str) -> GraphState:
        observed["loaded_thread_id"] = thread_id
        return GraphState(
            request=RetrievalRequest(query="question-1", top_k=3),
            conversation_id="conv-1",
            thread_id="thr-1",
            user_id=7,
            current_turn_index=1,
            last_user_question="question-1",
            last_answer_status="answered",
            last_cited_chunk_ids=("chunk-1",),
            last_cited_document_ids=("doc-1",),
            last_citations=({"chunk_id": "chunk-1"},),
            memory_summary="summary-1",
        )

    async def invoke_graph(state: GraphState, thread_id: str) -> GraphState:
        observed["invoked_thread_id"] = thread_id
        observed["invoked_state"] = state
        return state

    result = await start_next_rag_session(
        registry=registry,
        conversation_id="conv-1",
        user_id=7,
        request=RetrievalRequest(query="question-2", top_k=5),
        load_previous_state=load_previous_state,
        invoke_graph=invoke_graph,
        turn_id="turn-2",
        turn_index=2,
    )

    assert observed["loaded_thread_id"] == "thr-1"
    assert observed["invoked_thread_id"] == "thr-1"
    assert observed["loaded_thread_id"] == result.conversation.thread_id
    invoked_state = observed["invoked_state"]
    assert isinstance(invoked_state, GraphState)
    assert invoked_state.request.query == "question-2"
    assert invoked_state.current_turn_index == 2
    assert invoked_state.last_cited_chunk_ids == ("chunk-1",)
    assert result.thread_id == "thr-1"
    assert result.turn is not None
    assert result.turn.turn_id == "turn-2"
    assert result.conversation.thread_id == "thr-1"


@pytest.mark.asyncio
async def test_start_next_rag_session_starts_cleanly_without_checkpoint() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-missing")

    loaded_threads: list[str] = []

    async def load_previous_state(thread_id: str) -> GraphState:
        loaded_threads.append(thread_id)
        return GraphState(
            request=RetrievalRequest(query="question-1", top_k=3),
            conversation_id="conv-1",
            thread_id=thread_id,
            user_id=7,
        )

    async def invoke_graph(state: GraphState, thread_id: str) -> GraphState:
        assert thread_id == "thr-missing"
        assert state.thread_id == "thr-missing"
        assert state.current_turn_index == 1
        assert state.current_user_message == "question-1"
        assert state.memory_summary is None
        assert state.last_cited_chunk_ids == ()
        return state

    result = await start_next_rag_session(
        registry=registry,
        conversation_id="conv-1",
        user_id=7,
        request=RetrievalRequest(query="question-1", top_k=3),
        load_previous_state=load_previous_state,
        invoke_graph=invoke_graph,
        turn_id="turn-1",
        turn_index=1,
    )

    assert loaded_threads == ["thr-missing"]
    assert result.thread_id == "thr-missing"
    assert result.state.current_turn_index == 1
    assert result.state.memory_summary is None
    assert result.turn is not None
    assert result.turn.turn_id == "turn-1"


@pytest.mark.asyncio
async def test_start_next_rag_session_continues_from_same_thread_checkpoint_state() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    checkpointed_states: dict[str, GraphState] = {}
    invoked_states: list[GraphState] = []

    async def load_previous_state(thread_id: str) -> GraphState:
        return checkpointed_states.get(
            thread_id,
            GraphState(
                request=RetrievalRequest(query="seed", top_k=3),
                conversation_id="conv-1",
                thread_id=thread_id,
                user_id=7,
            ),
        )

    async def invoke_graph(state: GraphState, thread_id: str) -> GraphState:
        invoked_states.append(state)
        result = state.model_copy(update={"memory_summary": f"summary after {state.request.query}"})
        checkpointed_states[thread_id] = result
        return result

    first = await start_next_rag_session(
        registry=registry,
        conversation_id="conv-1",
        user_id=7,
        request=RetrievalRequest(query="question-1", top_k=3),
        load_previous_state=load_previous_state,
        invoke_graph=invoke_graph,
        turn_id="turn-1",
        turn_index=1,
    )
    second = await start_next_rag_session(
        registry=registry,
        conversation_id="conv-1",
        user_id=7,
        request=RetrievalRequest(query="question-2", top_k=5),
        load_previous_state=load_previous_state,
        invoke_graph=invoke_graph,
        turn_id="turn-2",
        turn_index=2,
    )

    assert first.state.thread_id == "thr-1"
    assert first.state.current_turn_index == 1
    assert first.state.memory_summary == "summary after question-1"
    assert invoked_states[1].thread_id == "thr-1"
    assert invoked_states[1].request.query == "question-2"
    assert invoked_states[1].current_turn_index == 2
    assert invoked_states[1].memory_summary == "summary after question-1"
    assert second.state.memory_summary == "summary after question-2"
    assert second.turn is not None
    assert second.turn.turn_id == "turn-2"


@pytest.mark.asyncio
async def test_start_next_rag_session_rejects_foreign_conversation_access() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    async def load_previous_state(_: str) -> GraphState:
        raise AssertionError("should not be called")

    async def invoke_graph(_: GraphState, __: str) -> GraphState:
        raise AssertionError("should not be called")

    with pytest.raises(ConversationAccessDenied):
        await start_next_rag_session(
            registry=registry,
            conversation_id="conv-1",
            user_id=8,
            request=RetrievalRequest(query="question-2", top_k=5),
            load_previous_state=load_previous_state,
            invoke_graph=invoke_graph,
            turn_id="turn-2",
            turn_index=2,
        )
