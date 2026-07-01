# Plan: Thread-ID Checkpointer Memory Load

## TL;DR

> **Quick Summary**: Make agentic memory load previous state by `thread_id` from the checkpointer instead of relying on router-local `_last_states[conversation_id]`.
>
> **Deliverables**:
> - Thread-based previous-state loading for same-process multi-turn chat
> - Router/session flow updated so `thread_id` is the canonical memory key
> - Tests proving continuity, isolation, and fallback behavior when no checkpoint exists
>
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Conversation lookup → thread-based state load → graph invoke → turn persistence

---

## Context

### Original Request
The user wants to revise memory so it uses the checkpointer via `thread_id` for each conversation. The user explicitly said restart durability does not matter.

### Interview Summary
**Key Discussions**:
- The current flow stores previous state in `_last_states` keyed by `conversation_id`.
- `thread_id` is already present in the graph invocation path and is the intended key for session continuity.
- The user chose the minimal in-process approach and does not require durable storage.

**Research Findings**:
- `app/presentation/api/v1/agentic/router.py` currently keeps `_last_states` as the primary previous-state cache.
- `app/agentic/orchestration/rag_graph.py` already passes `thread_id` into graph invocation config.
- `app/agentic/adapters/checkpoint/inmemory_checkpointer.py` currently returns `InMemorySaver`.
- `app/agentic/orchestration/session_flow.py` already models a `load_previous_state(thread_id)` flow.
- `app/agentic/orchestration/session_seeding.py` carries prior state fields forward into the next turn.

### Metis Review
**Identified Gaps** (addressed):
- Clarify whether `_last_states` remains as fallback or is removed from read path. Resolved in this plan as: remove `_last_states` from the previous-state read path completely; `thread_id` checkpointer load is the only source of truth.
- Explicitly lock scope to same-process continuity only. Done.
- Add isolation tests for distinct `thread_id` values. Done.

---

## Work Objectives

### Core Objective
Make the agentic chat flow load prior turn state from the checkpointer using `thread_id`, so each conversation can continue from the correct in-process graph state with `thread_id` as the only previous-state read path.

### Concrete Deliverables
- Router/session flow uses `thread_id` to load prior graph state before each turn.
- `_last_states` is removed from the previous-state read path entirely.
- Same-process same-thread continuity works.
- Different threads remain isolated.
- First turn with no checkpoint starts cleanly.

### Definition of Done
- [ ] Two sequential turns in the same `thread_id` reuse prior graph state via checkpointer load within the same process.
- [ ] Two different `thread_id` values do not share state.
- [ ] First turn with no checkpoint initializes a clean state without error.
- [ ] Existing chat/history/auth endpoints still work with `conversation_id`.
- [ ] The plan makes no durability claim after restart.

### Must Have
- `thread_id` is the canonical key for loading previous state.
- `conversation_id` still handles ownership and conversation lookup.
- No durable storage or restart persistence is added.
- Tests prove same-process continuity and thread isolation.

### Must NOT Have (Guardrails)
- No Postgres/durable checkpoint work.
- No new tables or persistence schema.
- No conversational summary redesign.
- No broad auth/history refactor.
- No keeping `_last_states` as any previous-state read source or fallback.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring user confirmation are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: pytest
- **If TDD**: N/A; this plan is tests-after because the goal is a narrow wiring change, not a new feature shape.

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/backend**: use pytest and/or curl against the agentic routes.
- **Library/module**: use pytest + direct function invocation for state loading behavior.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (foundation + flow wiring):
├── 1. router.py thread_id previous-state load path [quick]
├── 2. session_flow.py canonical thread loader contract [quick]
├── 3. rag_graph.py / checkpointer wiring sanity [quick]

Wave 2 (behavior proof + cleanup):
├── 4. API tests for same-thread continuity and isolation [quick]
├── 5. session_flow/checkpointer tests for missing checkpoint and turn reuse [quick]
├── 6. remove legacy _last_states read-path assumptions [quick]

Wave FINAL (verification):
├── F1. plan compliance audit [oracle]
├── F2. code quality review [unspecified-high]
├── F3. real QA of same-thread / cross-thread scenarios [unspecified-high]
├── F4. scope fidelity check [deep]
```

### Dependency Matrix
- 1-3: start immediately
- 4 depends on 1 and 3
- 5 depends on 1 and 3
- 6 depends on 1 and 2
- F1-F4 depend on all implementation tasks

### Agent Dispatch Summary
- Task 1-3: quick
- Task 4-6: quick
- F1: oracle
- F2-F3: unspecified-high
- F4: deep

---

## TODOs

- [x] 1. `app/presentation/api/v1/agentic/router.py`: Load prior graph state by `thread_id` before each turn - expect same-thread continuity without `_last_states` as the primary read path

  **What to do**:
  - Replace the current `previous_state = _last_states.get(conversation.conversation_id)` flow with a `thread_id`-based load path for prior `GraphState`.
  - Keep `conversation_id` for access control and conversation lookup, but do not use it as the memory key.
  - Ensure the first turn still initializes cleanly when no checkpoint exists.

  **Must NOT do**:
  - Do not introduce durable storage.
  - Do not change auth/history endpoint semantics.
  - Do not rework retrieval quality or memory summaries.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is a narrow routing change in one backend file.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Useful for tracing the existing state flow and confirming the new load path matches current runtime behavior.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Omitted because this is not a broad symbol rename or multi-file architectural refactor.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 2, 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `app/presentation/api/v1/agentic/router.py:143-212` - Current quick-chat and conversation chat paths; this is the place where `_last_states` is currently the source of truth.
  - `app/agentic/orchestration/session_flow.py:24-59` - Existing `load_previous_state(thread_id)` shape that shows the intended thread-based load contract.

  **API/Type References** (contracts to implement against):
  - `app/agentic/contracts/graph_state.py:13-38` - GraphState fields that must survive turn seeding.
  - `app/presentation/schemas/agentic_schema.py:AgenticChatResponse` - Response shape that must stay stable.

  **Test References** (testing patterns to follow):
  - `tests/unit/test_agentic_api.py:81-97` - Existing pattern for asserting persisted message history after a chat turn.
  - `tests/unit/ai/test_session_flow.py:11-58` - Existing session-flow test style for thread reuse.

  **External References** (libraries and frameworks):
  - None needed - this is a local application flow change.

  **WHY Each Reference Matters**:
  - The router lines show exactly where the previous-state lookup happens today.
  - The session flow lines show the target shape for loading by `thread_id`.
  - The GraphState and schema references ensure the turn state and API response remain compatible.
  - The tests show how to prove the new path with concrete assertions.

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  - [ ] The router loads prior state using `thread_id`-based checkpointer/session flow instead of `_last_states` as the primary read path.
  - [ ] A first turn with no checkpoint still returns a valid chat response.
  - [ ] `pytest tests/unit/test_agentic_api.py -k chat` continues to pass.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Same-thread previous state is loaded before turn 2
    Tool: Bash (pytest)
    Preconditions: One conversation has already produced a checkpoint for `thread_id = thr-1`.
    Steps:
      1. Run the unit/integration test that sends two sequential turns through the same conversation/thread.
      2. Assert the second turn uses the prior state loaded by `thread_id` rather than a fresh empty state.
      3. Assert response fields still contain the same conversation/thread identity.
    Expected Result: Second turn sees prior turn state through the thread-based load path.
    Failure Indicators: Turn 2 behaves like a first turn or loads state from the wrong conversation.
    Evidence: .omo/evidence/task-1-same-thread-load.log

  Scenario: Missing checkpoint falls back to a clean state
    Tool: Bash (pytest)
    Preconditions: A brand-new `thread_id` has no previous checkpoint.
    Steps:
      1. Send a first-turn request for a new conversation/thread.
      2. Assert the route returns a valid response without an exception.
      3. Assert the response is generated from a clean initial state.
    Expected Result: No checkpoint exists, and the turn still completes successfully.
    Evidence: .omo/evidence/task-1-missing-checkpoint.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-1-same-thread-load.log`
  - [ ] `.omo/evidence/task-1-missing-checkpoint.log`

  **Commit**: YES | NO (groups with 2)
  - Message: `refactor(agentic): load memory state by thread_id`
  - Files: `app/presentation/api/v1/agentic/router.py`
  - Pre-commit: `pytest tests/unit/test_agentic_api.py -k chat`

- [x] 2. `app/agentic/orchestration/session_flow.py`: Make thread_id the canonical previous-state loader - expect reusable thread-based session continuation

  **What to do**:
  - Ensure `start_next_rag_session(...)` and the helper flow load prior state using `load_previous_state(conversation.thread_id)` as the canonical path.
  - Keep the helper shaped around `thread_id` so the router can reuse it without relying on conversation-local RAM.
  - Preserve the current `build_next_session_state(...)` contract and turn increment behavior.

  **Must NOT do**:
  - Do not add persistence beyond the in-memory checkpointer.
  - Do not change conversation authorization logic.
  - Do not change retrieval behavior in this task.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is a focused orchestration helper change.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Useful for tracing the existing session flow and confirming thread ownership semantics.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: Omitted because the change is narrow and already scoped by the plan.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4, 5
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `app/agentic/orchestration/session_flow.py:24-59` - Existing helper already expresses thread-based previous-state loading.
  - `app/agentic/orchestration/session_seeding.py:8-34` - Field-by-field state carry-forward contract that should remain intact.

  **API/Type References** (contracts to implement against):
  - `app/agentic/contracts/graph_state.py:13-38` - State fields passed into the next turn.
  - `app/agentic/orchestration/conversation_registry.py:33-112` - Conversation/thread ownership model that must remain separate from memory loading.

  **Test References** (testing patterns to follow):
  - `tests/unit/ai/test_session_flow.py:11-58` - Thread-reuse test pattern.
  - `tests/unit/ai/test_next_session_state.py:8-66` - Carry-forward assertions for state seeding.

  **External References** (libraries and frameworks):
  - None needed.

  **WHY Each Reference Matters**:
  - The session flow file already models the exact contract we want, so the implementation should align with it instead of inventing a new path.
  - The seeding and GraphState references prove which fields must be preserved turn-to-turn.
  - The registry reference keeps conversation identity and memory identity separate.

  **Acceptance Criteria**:
  - [ ] `start_next_rag_session(...)` continues to load prior state by `thread_id`.
  - [ ] Turn index increments and `GraphState` seeding still work unchanged.
  - [ ] Existing session-flow unit tests still pass.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Session helper reuses prior state for the same thread
    Tool: Bash (pytest)
    Preconditions: A previous GraphState exists for the same `thread_id`.
    Steps:
      1. Invoke `start_next_rag_session(...)` twice with the same `thread_id`.
      2. Assert the second invocation receives the prior state.
      3. Assert `current_turn_index` increments by 1.
    Expected Result: The helper uses thread-based state continuity.
    Evidence: .omo/evidence/task-2-thread-session-continuity.log

  Scenario: Foreign conversation access is still rejected
    Tool: Bash (pytest)
    Preconditions: A conversation belongs to a different `user_id`.
    Steps:
      1. Call `start_next_rag_session(...)` with an unauthorized user.
      2. Assert `ConversationAccessDenied` is raised.
    Expected Result: Authorization remains intact and unchanged.
    Evidence: .omo/evidence/task-2-foreign-access.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-2-thread-session-continuity.log`
  - [ ] `.omo/evidence/task-2-foreign-access.log`

  **Commit**: YES | NO (groups with 1)
  - Message: `refactor(agentic): load memory state by thread_id`
  - Files: `app/agentic/orchestration/session_flow.py`
  - Pre-commit: `pytest tests/unit/ai/test_session_flow.py`

- [x] 3. `app/agentic/orchestration/rag_graph.py` and `app/agentic/adapters/checkpoint/inmemory_checkpointer.py`: Keep graph invocation/checkpointer wiring aligned with thread_id loading - expect consistent same-process checkpoint behavior

  **What to do**:
  - Verify `invoke_rag_graph(...)` still binds `thread_id` into graph config and the graph uses the same thread identity for checkpoint lookup.
  - Keep the in-memory checkpointer path intact for this plan.
  - Make sure the wiring is simple enough that the router/session loader can rely on it.

  **Must NOT do**:
  - Do not add durable storage.
  - Do not change graph node logic.
  - Do not alter retrieval or answer generation behavior.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is wiring validation and possibly a small alignment tweak.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Useful for confirming how the graph and checkpointer interact.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Omitted because the issue is architectural wiring, not runtime failure investigation.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 1, 2 if a wiring mismatch is found; otherwise unblocks Wave 2 tests
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `app/agentic/orchestration/rag_graph.py:18-44` - Current graph assembly and `thread_id` invocation config.
  - `app/agentic/adapters/checkpoint/inmemory_checkpointer.py:1-6` - Current `InMemorySaver` factory.

  **API/Type References** (contracts to implement against):
  - `app/agentic/contracts/graph_state.py:13-38` - The state object compiled by LangGraph.
  - `app/agentic/orchestration/evidence_handoff.py:6-18` - Separate thread-local handoff state must remain unaffected.

  **Test References** (testing patterns to follow):
  - `tests/unit/ai/test_session_memory.py:72-101` - Graph/checkpointer behavior with citations and in-memory execution.

  **External References** (libraries and frameworks):
  - LangGraph `InMemorySaver` behavior (already wired in repo; no external docs needed for the plan).

  **WHY Each Reference Matters**:
  - The graph assembly shows where `thread_id` is bound today.
  - The checkpointer factory shows the exact same-process memory mechanism we are keeping.
  - The tests prove the in-memory graph path and prevent accidental drift into durable or unrelated behaviors.

  **Acceptance Criteria**:
  - [ ] The graph is still compiled with the in-memory checkpointer.
  - [ ] `thread_id` remains the graph config key used during invocation.
  - [ ] Existing graph unit tests continue to pass.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Graph invocation binds the same thread_id across turns
    Tool: Bash (pytest)
    Preconditions: A test graph is built with the in-memory checkpointer.
    Steps:
      1. Invoke the graph for a first turn using `thread_id = thr-1`.
      2. Invoke a second turn with the same `thread_id`.
      3. Assert the second turn can access checkpointed state from the first.
    Expected Result: Graph config remains thread-bound and consistent.
    Evidence: .omo/evidence/task-3-graph-thread-binding.log

  Scenario: In-memory checkpointer remains same-process only
    Tool: Bash (pytest)
    Preconditions: The in-memory checkpointer is in use.
    Steps:
      1. Build the graph and execute a turn.
      2. Assert state is available immediately to a second turn in the same process.
    Expected Result: The in-memory path works in-process without introducing persistence.
    Evidence: .omo/evidence/task-3-inmemory-checkpointer.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-3-graph-thread-binding.log`
  - [ ] `.omo/evidence/task-3-inmemory-checkpointer.log`

  **Commit**: YES | NO (groups with 1)
  - Message: `refactor(agentic): load memory state by thread_id`
  - Files: `app/agentic/orchestration/rag_graph.py`, `app/agentic/adapters/checkpoint/inmemory_checkpointer.py`
  - Pre-commit: `pytest tests/unit/ai/test_session_memory.py`

- [x] 4. `tests/unit/test_agentic_api.py`: Prove same-thread continuity and cross-thread isolation at the API layer - expect user-visible chat behavior to follow thread_id

  **What to do**:
  - Add or update tests that send two turns in the same conversation/thread and verify the second turn reuses prior state.
  - Add a separate test proving a different `thread_id` does not see the prior thread state.
  - Keep response shape assertions intact for chat/conversation endpoints.

  **Must NOT do**:
  - Do not require restart persistence.
  - Do not assert on durable storage.
  - Do not change unrelated endpoint behavior.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is a unit/integration test expansion in one file.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Useful for reasoning about how the API route selects previous state and where thread isolation could fail.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: Omitted because the API area is already scoped and covered by the plan.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 1 and 2

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `tests/unit/test_agentic_api.py:36-97` - Existing API test patterns for conversation creation, chat turns, and message history.

  **API/Type References** (contracts to implement against):
  - `app/presentation/schemas/agentic_schema.py` - Response contracts for conversation/chat endpoints.
  - `app/presentation/api/v1/agentic/router.py` - The runtime route behavior being exercised by the tests.

  **Test References** (testing patterns to follow):
  - `tests/unit/ai/test_session_flow.py:11-58` - Thread reuse test shape to mirror at the API layer.
  - `tests/unit/ai/test_next_session_state.py:8-66` - Carry-forward assertions to validate state continuity.

  **External References** (libraries and frameworks):
  - `pytest` and `fastapi.testclient` - already used by the repo.

  **WHY Each Reference Matters**:
  - The existing API tests show how to create conversations and exercise chat endpoints.
  - The router and schema references define what the test should observe.
  - The AI tests show the state-continuity pattern we want to prove at the endpoint level.

  **Acceptance Criteria**:
  - [ ] Same-thread chat turns reuse prior state within the same process.
  - [ ] Different `thread_id` values do not leak state.
  - [ ] Existing API response assertions still pass.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Same-thread conversation keeps prior state across two chat turns
    Tool: Bash (pytest)
    Preconditions: One conversation has been created for a known user.
    Steps:
      1. Send a first chat turn.
      2. Send a second chat turn for the same conversation/thread.
      3. Assert the second response reflects continuity from the first turn's checkpointed state.
    Expected Result: The API behaves like thread-based memory is working.
    Evidence: .omo/evidence/task-4-same-thread-api.log

  Scenario: Different thread ids remain isolated
    Tool: Bash (pytest)
    Preconditions: Two conversations exist with distinct `thread_id` values.
    Steps:
      1. Send a turn in the first conversation.
      2. Send a turn in the second conversation.
      3. Assert the second conversation does not see state from the first.
    Expected Result: No cross-thread memory leakage.
    Evidence: .omo/evidence/task-4-cross-thread-isolation.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-4-same-thread-api.log`
  - [ ] `.omo/evidence/task-4-cross-thread-isolation.log`

  **Commit**: YES | NO (groups with 5)
  - Message: `test(agentic): verify thread-based memory loading`
  - Files: `tests/unit/test_agentic_api.py`
  - Pre-commit: `pytest tests/unit/test_agentic_api.py`

- [x] 5. `tests/unit/ai/test_session_flow.py` and `tests/unit/ai/test_next_session_state.py`: Prove helper-level thread loading and state carry-forward - expect canonical thread reuse behavior in unit tests

  **What to do**:
  - Update or expand the session-flow tests so `start_next_rag_session(...)` proves thread-based continuity.
  - Keep the state carry-forward assertions that show `build_next_session_state(...)` preserves prior fields and increments turn index.
  - Add explicit coverage for missing checkpoint behavior if needed.

  **Must NOT do**:
  - Do not add durable persistence expectations.
  - Do not change unrelated graph node tests.
  - Do not introduce a summary-memory story.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is mostly test expansion around existing helper contracts.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Useful for verifying the exact loader contract and edge cases.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-exploring`: Omitted because the relevant session flow is already mapped in the research findings.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 1 and 2

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `tests/unit/ai/test_session_flow.py:11-82` - Existing thread-reuse and access-denial patterns.
  - `tests/unit/ai/test_next_session_state.py:8-66` - Exact carry-forward contract for GraphState.

  **API/Type References** (contracts to implement against):
  - `app/agentic/orchestration/session_flow.py:24-59` - Thread-based helper contract.
  - `app/agentic/orchestration/session_seeding.py:8-34` - Fields that must persist into the next turn.

  **Test References** (testing patterns to follow):
  - Existing tests in the same files - follow their async style and explicit assertions.

  **External References** (libraries and frameworks):
  - `pytest`.

  **WHY Each Reference Matters**:
  - These tests prove the core concept directly at the helper layer.
  - They also prove the existing state seeding contract still behaves the same while the load source changes.

  **Acceptance Criteria**:
  - [ ] Thread-based session helper loads the prior state for the same `thread_id`.
  - [ ] The helper rejects foreign access as before.
  - [ ] `build_next_session_state(...)` carry-forward assertions still pass.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Session helper loads previous state by thread_id
    Tool: Bash (pytest)
    Preconditions: A prior state exists for the same thread.
    Steps:
      1. Call the helper twice with the same `thread_id`.
      2. Assert the second call receives the loaded prior state.
      3. Assert the next state increments turn index.
    Expected Result: Thread-based continuity is proven at the helper layer.
    Evidence: .omo/evidence/task-5-session-helper-thread-load.log

  Scenario: State seeding still carries fields forward
    Tool: Bash (pytest)
    Preconditions: A populated prior GraphState is available.
    Steps:
      1. Build the next session state.
      2. Assert cited ids, metadata, and user context are preserved.
      3. Assert transient output is cleared.
    Expected Result: The seeding contract stays intact.
    Evidence: .omo/evidence/task-5-state-seeding.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-5-session-helper-thread-load.log`
  - [ ] `.omo/evidence/task-5-state-seeding.log`

  **Commit**: YES | NO (groups with 4)
  - Message: `test(agentic): verify thread-based memory loading`
  - Files: `tests/unit/ai/test_session_flow.py`, `tests/unit/ai/test_next_session_state.py`
  - Pre-commit: `pytest tests/unit/ai/test_session_flow.py tests/unit/ai/test_next_session_state.py`

- [x] 6. `app/presentation/api/v1/agentic/router.py`: Remove legacy `_last_states` read-path assumptions after thread_id loader is in place - expect `thread_id` to remain the only previous-state read source

  **What to do**:
  - Remove `_last_states.get(...)` from the router’s previous-state read path entirely.
  - Do not keep `_last_states` as fallback for loading previous `GraphState`.
  - Keep `conversation_id` for access control, turn persistence, and history lookup only.
  - Preserve response shape and turn recording behavior.

  **Must NOT do**:
  - Do not reintroduce fallback state loading from `_last_states`.
  - Do not alter auth/history endpoint behavior.
  - Do not widen scope into retrieval, durable persistence, or summarization changes.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is a narrow cleanup change in one router file after the canonical loader is in place.
  - **Skills**: [`gitnexus-refactoring`]
    - `gitnexus-refactoring`: Useful for removing the old read path cleanly without breaking adjacent route behavior.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Omitted because the target failure mode is already captured by the continuity and isolation tests.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Task 1
  - **Blocks**: Final verification wave
  - **Blocked By**: Task 1

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `app/presentation/api/v1/agentic/router.py:48-52, 143-212` - Current `_last_states` declaration and both route use sites to remove from previous-state loading.
  - `tests/unit/test_agentic_api.py:81-97` - Existing history behavior that must continue working.

  **API/Type References** (contracts to implement against):
  - `app/agentic/orchestration/conversation_registry.py` - Still needed for turn history, not state loading.
  - `app/presentation/schemas/agentic_schema.py:AgenticChatResponse` - Public response shape must remain stable.

  **Test References** (testing patterns to follow):
  - `tests/unit/test_agentic_api.py` - API route coverage for chat and history behavior.

  **External References** (libraries and frameworks):
  - None.

  **WHY Each Reference Matters**:
  - The router lines are where the legacy previous-state read behavior lives.
  - The registry/schema references clarify what must remain unchanged while removing memory-cache reads.
  - The test lines prove history persistence remains intact even after the load-path change.

  **Acceptance Criteria**:
  - [ ] `_last_states` is not used to load previous state in either chat route.
  - [ ] No `_last_states` fallback exists for previous `GraphState` loading.
  - [ ] Conversation/message history endpoints still pass.
  - [ ] The router still emits correct `AgenticChatResponse` payloads.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Router uses thread_id path instead of legacy read cache
    Tool: Bash (pytest)
    Preconditions: A same-thread multi-turn test is available.
    Steps:
      1. Run the API test suite relevant to chat and message history.
      2. Confirm state continuity still passes through `thread_id` checkpoint loading.
      3. Confirm no route path loads previous state from `_last_states`.
    Expected Result: The router is not using `_last_states` as any previous-state read source.
    Failure Indicators: Any test or runtime path still treats `_last_states` as fallback for loading previous `GraphState`.
    Evidence: .omo/evidence/task-6-thread-id-only.log

  Scenario: History endpoints remain intact after removing legacy read path
    Tool: Bash (pytest)
    Preconditions: A conversation with at least one chat turn exists.
    Steps:
      1. Fetch conversation and messages.
      2. Assert message history still contains the recorded turn.
      3. Assert response fields serialize with the expected conversation and thread identifiers.
    Expected Result: The UI/history contract remains unchanged while legacy fallback is absent.
    Evidence: .omo/evidence/task-6-history-intact.log
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-6-thread-id-only.log`
  - [ ] `.omo/evidence/task-6-history-intact.log`

  **Commit**: YES | NO (groups with 1)
  - Message: `refactor(agentic): remove legacy read-path cache`
  - Files: `app/presentation/api/v1/agentic/router.py`
  - Pre-commit: `pytest tests/unit/test_agentic_api.py`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify the plan stays in the A-scope only: thread_id loading via checkpointer, same-process continuity, no durability work, no summary redesign. Confirm every Must Have and Must NOT Have is reflected in tasks.

  **Acceptance Criteria**:
  - [ ] The audit reports `Must Have [N/N]` and `Must NOT Have [N/N]` with no missing scope items.
  - [ ] The audit returns `VERDICT: APPROVE`.
  - [ ] Any detected scope drift is cited with file/line references.

  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run the relevant test command(s), inspect changed files for obvious slop, and check that the wiring follows existing graph/session patterns.

  **Acceptance Criteria**:
  - [ ] Relevant tests pass for the changed backend files.
  - [ ] No new obvious slop or unrelated rewrites are present in the diff.
  - [ ] The review returns `VERDICT: PASS`.

  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real QA** — `unspecified-high`
  Execute the two critical scenarios: same-thread sequential turns and cross-thread isolation. Capture evidence files under `.omo/evidence/final-qa/`.

  **Acceptance Criteria**:
  - [ ] Same-thread sequential turn scenario passes.
  - [ ] Cross-thread isolation scenario passes.
  - [ ] Evidence files are written for both scenarios.
  - [ ] The QA run returns `VERDICT: PASS`.

  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Compare the implemented diff to the plan. Verify the change is limited to thread-based state loading and does not introduce durable storage, summary memory, or unrelated route changes.

  **Acceptance Criteria**:
  - [ ] Diff is limited to the planned files/tasks.
  - [ ] No durable storage or summary-memory code is present.
  - [ ] No unrelated route or auth/history behavior changed.
  - [ ] The check returns `VERDICT: CLEAN`.

  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

- **1**: `refactor(agentic): load memory state by thread_id`

---

## Success Criteria

### Verification Commands
```bash
pytest tests/unit/ai/test_session_flow.py  # thread-based continuity tests pass
pytest tests/unit/test_agentic_api.py      # conversation/chat endpoints still pass
```

### Final Checklist
- [ ] Same-thread continuity passes
- [ ] Cross-thread isolation passes
- [ ] No durable storage added
- [ ] `_last_states` is no longer the canonical read path

