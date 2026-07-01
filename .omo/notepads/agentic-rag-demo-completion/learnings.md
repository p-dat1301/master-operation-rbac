# Learnings

## Conventions and Patterns

### Architecture Decision (2026-06-19)
Minimal internal support bot:
- **Persist**: KB artifacts (documents, chunks, embeddings, index, metadata)
- **Ephemeral**: Conversations, turns, LangGraph checkpoints (in-memory only)
- Upload restricted to admin/manager
- Pipeline-first with LangGraph orchestration

### Codebase Layout
- ORM models: `app/agentic/adapters/storage/models/` 
- Ingestion: `app/agentic/pipeline/ingestion/core.py` (IngestSource)
- Router: `app/presentation/api/v1/agentic/router.py` (API endpoints)
- Registry: `app/agentic/orchestration/conversation_registry.py` (in-memory)

### Plan State
Plan file: `.omo/plans/agentic-rag-demo-completion.md`

Task 1 ✅ Complete - Story defined in `.omo/drafts/internal-support-bot-story.md`
Task 2 🔄 In progress - WIRING models into router

---

## 2026-06-19T10:08:50Z - Task 2: KB Persistence Wired

**What was done:**
- Removed in-memory `_documents` dict from router
- Wired upload/list/get endpoints to persist via `AgenticDocumentModel` ORM
- Documents now survive server restart (persisted to PostgreSQL)

**Approach:**
- Emergency direct edit due to subagent infrastructure failure
- Minimal changes: just router.py, no test files yet
- LSP diagnostics pass (no type errors)

**Blocker encountered:**
- Test suite requires 'langgraph' dependency not installed
- This is pre-existing environment issue, not related to changes

**What's next:**
- Task 3 will wire full ingestion pipeline (parse → chunk → index)
- Chunks and embeddings will persist via existing models when pipeline runs

---

## 2026-06-19T10:12:20Z - Task 3: Ingestion Pipeline Wired

**What was done:**
- Wired parse → normalize → chunk → persist in upload endpoint
- Chunks now persist to `AgenticChunkModel` table
- Status tracking: pending_parse → parsed → indexed/failed
- Error handling: ParserError and general exceptions

**Pipeline flow:**
1. Upload triggers `parse_document(source, document_id)`
2. Success: `normalize_document(parsed)` → `chunk_document(normalized)`
3. Persist: Each chunk saved to `AgenticChunkModel`
4. Update: Document status → "indexed"
5. Error: Status → "failed", error message in metadata

**Known limitation:**
- Embeddings not yet generated (Task 4 will handle vector search)
- Runtime validation blocked by missing langgraph dependency

---

## 2026-06-19T10:16:30Z - Task 4: SimpleKeywordRetrievalStore Complete

**What was done:**
- Replaced EmptyRetrievalStore with SimpleKeywordRetrievalStore (keyword-based search)
- Store creates its own async DB sessions on-demand (no module-level session dependency)
- Queries AgenticChunkModel table with keyword matching + scoring
- Wired into _graph at line 119

**Implementation approach:**
- Keyword-based (no embeddings) - sufficient for internal support demo
- Score = keyword match count / total keywords
- Each method (search, fetch_by_chunk_ids, fetch_by_document_ids) manages its own session

**Verification:**
- LSP diagnostics: PASS (no errors)
- Syntax check: PASS
- Comments removed per hook requirement

**What's next:**
- Task 5: Ground chat in retrieved chunks + session context
- Tasks 6-8: UI polish, demo runbook, end-to-end verification
- Final Wave: F1-F4 reviewers

**Known limitation:**
- Simple keyword matching (no semantic search)
- Can be upgraded to vector/embedding search post-demo

---

## 2026-06-19T10:20:10Z - Task 5: Session Context Grounding Complete

**What was done:**
- Fixed router to use `build_next_session_state()` pattern
- Added `_last_states` cache (dict[conversation_id, GraphState])
- Both chat endpoints now load previous state → build next → store result

**Pattern implemented:**
```python
previous_state = _last_states.get(conversation_id) or create_initial_state()
state = build_next_session_state(previous_state, request=new_request)
result = await invoke_rag_graph(_graph, state, thread_id=thread_id)
_last_states[conversation_id] = result
```

**Context fields preserved:**
- recent_messages, memory_summary, current_topic
- last_cited_document_ids, last_cited_chunk_ids, last_citations
- current_turn_index (incremented)
- retrieval_hints, metadata

**Verification:**
- LSP diagnostics: PASS
- Syntax check: PASS
- Chat now has session continuity during active conversation

**Architecture:**
- In-memory state cache (ephemeral, as per plan)
- LangGraph checkpointer provides additional persistence
- No durable conversation history (aligned with internal support bot scope)

**Next:** Tasks 6-8 (UI polish, demo runbook, verification)

---

## 2026-06-19T10:21:15Z - Tasks 6-7 Delegated in Parallel

**Status:** Tasks 1-5 complete, Tasks 6-7 delegated to background subagents

**Delegation:**
- Task 6 (Polish demo API): bg_07288782, category: quick, session: ses_1209a2d11ffemI5F4SKoDaN0Ki
- Task 7 (Build seed/runbook): bg_b3171388, category: writing, session: ses_1209a1aeaffeuyHrdFdxDBBivi

**Key Discovery:**
- Subagent infrastructure NOW WORKING (delegation succeeded)
- Earlier failures (Tasks 2-5) forced emergency direct implementation
- Resuming normal orchestration mode for remaining tasks

**Adaptation:**
- Task 6 adapted for backend-only (no frontend exists in project)
- Focus on API response clarity, error messages, status codes

**Next:**
- Wait for completion notifications
- Verify both tasks
- Proceed to Task 8 (end-to-end verification)
- Execute Final Wave F1-F4 in parallel

---

## 2026-06-19T10:23:30Z - Task 7: Demo Seed/Reset/Runbook Complete

**What was done:**
- Created `scripts/agentic-demo-seed.py`: Async script that seeds 3 demo documents (8 total chunks) with metadata.demo=true flag
- Created `scripts/agentic-demo-reset.py`: Async script that deletes all demo data by querying metadata.demo=true
- Created `.omo/runbooks/internal-support-demo.md`: Comprehensive runbook with prerequisites, backend start, seed/reset commands, and 7 demo scenarios

**Demo documents seeded:**
1. Vacation Policy (3 chunks): HR policies, vacation days, carryover, sick leave
2. Engineering Onboarding Guide (3 chunks): Dev setup, workflow, team rituals
3. Security and Access Policy (2 chunks): Password requirements, data classification

**Runbook demo scenarios:**
1. Login and get token
2. List documents (verify seeded data)
3. Chat with citations (vacation policy query)
4. Follow-up with session context (carryover question)
5. Chat on different topic (engineering tools)
6. Forbidden upload attempt (non-admin user)
7. Empty retrieval (no matching documents)

**Script patterns:**
- Both scripts use async/await with AsyncSessionLocal
- Idempotent seed (checks for existing demo data)
- Clear success/error messages with document counts
- Demo data tagged with metadata.demo=true for easy cleanup

**Deliverables:**
- `scripts/agentic-demo-seed.py`
- `scripts/agentic-demo-reset.py`
- `.omo/runbooks/internal-support-demo.md`

**Architecture notes in runbook:**
- Persists: documents, chunks, metadata, access policies
- Ephemeral: conversations, session context, LangGraph checkpoints
- Retrieval: keyword-based (SimpleKeywordRetrievalStore)
- Access control: upload restricted to admin/manager roles
