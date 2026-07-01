# Draft: Checkpointer Thread Memory

## Requirements (confirmed)
- User wants a plan to revise memory so each conversation loads memory/state from the checkpointer via `thread_id`.
- Confirmed premise: source of memory truth should move away from router-local `_last_states[conversation_id]` toward checkpointer state keyed by `thread_id`.
- Confirmed premise: `conversation_id` remains the public conversation/authorization identifier, while `thread_id` is used to load prior graph state.
- Confirmed final decision: restart durability and multi-worker persistence are NOT important for this plan; same-process continuity through `InMemorySaver` is acceptable.

## Technical Decisions
- Need preserve `conversation_id` for API access control and history endpoints.
- Need design around checkpointer load semantics and avoid relying on `_last_states` as any previous-state read source.
- User clarified restart durability is NOT important, so a RAM-backed `InMemorySaver` approach is acceptable if it correctly loads state by `thread_id` during the same app process.
- User selected Option A: remove `_last_states` from the previous-state read path completely; do not keep it as fallback.

## Research Findings
- `app/presentation/api/v1/agentic/router.py` currently stores `_last_states: dict[str, GraphState]` keyed by `conversation_id`.
- `app/agentic/orchestration/rag_graph.py` invokes graph with `config={"configurable": {"thread_id": thread_id}}`.
- `app/agentic/adapters/checkpoint/inmemory_checkpointer.py` currently builds `InMemorySaver`.
- `app/agentic/adapters/checkpoint/postgres_checkpointer.py` exists as a durable checkpointer option.
- `app/agentic/orchestration/session_flow.py` already has a helper shape where `load_previous_state(conversation.thread_id)` feeds `build_next_session_state(...)`.
- `GraphState` carries memory fields, but current observed runtime memory mostly depends on prior citation fields and router-local state.

## Open Questions
- None. The user selected Option A: minimal thread loader using `InMemorySaver`, `thread_id` as the only previous-state read key, and complete removal of `_last_states` from the read path.

## Scope Boundaries
- INCLUDE: Backend memory state loading flow, checkpointer integration, tests proving state loads by `thread_id`, QA scenarios for multi-turn chat.
- INCLUDE: Removing or demoting `_last_states` from source-of-truth role.
- EXCLUDE: unrelated UI redesign, unrelated RAG retrieval quality changes, broad auth/RBAC changes.
