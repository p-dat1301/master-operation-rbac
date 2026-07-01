# Draft: memory-checkpointer-pg

## Requirements (confirmed)
- User wants to update the memory mechanism to use a checkpointer and store it in PostgreSQL.
- Critical concern: ensure `thread_id` of one user cannot be mistakenly used for another user when responding.

## Technical Decisions
- Proposed direction: PostgreSQL-backed checkpointer with strict ownership binding on every checkpoint read/write.
- Proposed identity model: `thread_id` is not globally sufficient; ownership must be enforced by authenticated `user_id` (and optionally tenant/scope version fields).
- Proposed retrieval rule: memory can assist context only; factual answers must still re-run authorized retrieval before answering.
- User proposed concrete mechanism: server-created `thread_id` format `user_{user_id}_{uuid4}`, client cannot create or pass arbitrary thread IDs, new thread on logout/new chat, no cross-session context, cleanup after 7 days.
- User proposed concrete LangGraph checkpointer: `PostgresSaver` from `langgraph-checkpoint-postgres`, `ConnectionPool` with `autocommit=True`, `checkpointer.setup()` at app startup, automatic checkpoint after each node.
- User proposed checkpoint state policy: persist only short summaries/metadata/user context/answer metadata/audit events; do not persist sensitive evidence chunks, full answer text, or rewritten query.
- User proposed mandatory node order: load_context → query_rewrite → retrieval → access_control → generate → update_context, with update_context clearing sensitive one-turn fields before checkpoint persistence.
- User proposed API security: validate thread ownership against JWT user before invoking graph; return 403 and do not invoke on mismatch.
- User proposed cleanup: nightly delete checkpoints older than 7 days plus related checkpoint_blobs and checkpoint_writes.
- User confirmed preference: `thread_id` should be opaque (no `user_id` embedded), ownership must be checked through DB mapping, and `user_id` stays visible only in server-side DB tables for debugging.

## Research Findings
- Existing auth boundary resolves JWT `sub` into backend `request.state.user` and protected routes use `get_current_user`.
- The current codebase already uses PostgreSQL + SQLAlchemy + Alembic and has pgvector-backed agentic persistence.
- The current plan already expects LangGraph checkpointer + stable `thread_id`, but its wording should be tightened so reads/writes are ownership-checked by `user_id`, not `thread_id` alone.
- No existing conversation/thread persistence layer was found, so this will be a new ownership-sensitive design.

## Open Questions
- None blocking.

## Final Decisions
- Thread ID: opaque format `thr_{uuid4}`; never embed `user_id` in the thread string; ownership is stored and enforced through `rag_threads`.
- TTL: MVP session/thread expiry is 24 hours via `expires_at = NOW() + INTERVAL '24 hours'`.
- Summary: use short LLM summary in `update_context_node`, not deterministic truncation, because truncation can cut meaning in long internal RAG questions/answers.
- Test strategy: tests-after plus mandatory agent-executed QA scenarios, consistent with the existing `agentic-rag-pipeline.md` plan.

## Scope Boundaries
- INCLUDE: memory/checkpointer design, PostgreSQL persistence, thread isolation strategy.
- EXCLUDE: unrelated feature changes unless required for safe isolation.
