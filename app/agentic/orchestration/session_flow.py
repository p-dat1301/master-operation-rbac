"""RAG session flow orchestration helpers."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.conversation_registry import ConversationRegistry, ConversationRecord, TurnRecord
from app.agentic.orchestration.session_seeding import build_next_session_state

PreviousStateLoader = Callable[[str], Awaitable[GraphState]]
GraphInvoker = Callable[[GraphState, str], Awaitable[GraphState]]


@dataclass(frozen=True)
class NextRagSessionResult:
    conversation: ConversationRecord
    turn: TurnRecord | None
    thread_id: str
    state: GraphState


async def start_next_rag_session(
    *,
    registry: ConversationRegistry,
    conversation_id: str,
    user_id: int,
    request: RetrievalRequest,
    load_previous_state: PreviousStateLoader,
    invoke_graph: GraphInvoker,
    turn_id: str | None = None,
    turn_index: int | None = None,
    assistant_status: str = "pending",
    langfuse_trace_id: str | None = None,
) -> NextRagSessionResult:
    conversation = registry.ensure_access(conversation_id=conversation_id, user_id=user_id)
    previous_state = await load_previous_state(conversation.thread_id)
    turn = None
    if turn_id is not None and turn_index is not None:
        turn = registry.register_turn(
            conversation_id=conversation_id,
            turn_id=turn_id,
            turn_index=turn_index,
            assistant_status=assistant_status,
            langfuse_trace_id=langfuse_trace_id,
        )
    state = build_next_session_state(
        previous_state,
        request=request,
        conversation_id=conversation_id,
    )
    result_state = await invoke_graph(state, conversation.thread_id)
    return NextRagSessionResult(
        conversation=conversation,
        turn=turn,
        thread_id=conversation.thread_id,
        state=result_state,
    )
