"""LangGraph assembly for Task 9 MVP."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.session_seeding import build_next_session_state
from app.agentic.orchestration.langfuse_logger import NullLangfuseTurnLogger
from app.agentic.orchestration.nodes.audit_event import audit_event_node
from app.agentic.orchestration.nodes.deny_request import deny_request_node
from app.agentic.orchestration.nodes.generate_answer import build_generate_answer_node
from app.agentic.orchestration.nodes.load_user_context import load_user_context_node
from app.agentic.orchestration.nodes.retrieve_evidence import build_retrieve_evidence_node
from app.agentic.orchestration.nodes.validate_policy import route_after_retrieval


def build_rag_graph(*, checkpointer, retrieval_store, answer_llm=None, langfuse_logger=None):
    builder = StateGraph(GraphState)
    builder.add_node("load_user_context", load_user_context_node)
    builder.add_node(
        "retrieve_evidence",
        build_retrieve_evidence_node(retrieval_store, langfuse_logger=langfuse_logger or NullLangfuseTurnLogger()),
    )
    builder.add_node("deny_request", deny_request_node)
    builder.add_node("generate_answer", build_generate_answer_node(answer_llm))
    builder.add_node("audit_event", audit_event_node)
    builder.add_edge(START, "load_user_context")
    builder.add_edge("load_user_context", "retrieve_evidence")
    builder.add_conditional_edges(
        "retrieve_evidence",
        route_after_retrieval,
        {"deny_request": "deny_request", "generate_answer": "generate_answer"},
    )
    builder.add_edge("deny_request", "audit_event")
    builder.add_edge("generate_answer", "audit_event")
    builder.add_edge("audit_event", END)
    return builder.compile(checkpointer=checkpointer)


async def invoke_rag_graph(graph, state: GraphState, *, thread_id: str) -> GraphState:
    state.thread_id = thread_id
    result = await graph.ainvoke(state, config={"configurable": {"thread_id": thread_id}})
    return GraphState.model_validate(result)


async def invoke_next_rag_session(
    graph,
    previous_state: GraphState,
    *,
    request: RetrievalRequest,
    thread_id: str,
    conversation_id: str | None = None,
) -> GraphState:
    state = build_next_session_state(previous_state, request=request, conversation_id=conversation_id)
    return await invoke_rag_graph(graph, state, thread_id=thread_id)
