# Minimal Internal Support Bot Completion Plan

## TL;DR

> **Quick Summary**: Complete the current internal support chatbot into a reliable RAG system by making the knowledge base durable, keeping chat context short-lived for the active session only, wiring ingestion and retrieval end-to-end, and adding a simple demo/runbook path.
>
> **Deliverables**:
> - Durable knowledge base storage: documents, chunks, embeddings/index, metadata, upload/ingestion status
> - Retrieval-backed chat that uses recent session context plus indexed internal documents
> - Admin/manager-only upload guard
> - Minimal demo-facing API/UI flow for upload, chat, history-in-session, and document status
> - Seed/reset/runbook for repeatable demo execution
> - Automated tests and agent-verified QA evidence
>
> **Estimated Effort**: Medium
>
> **Parallel Execution**: YES - 4 waves
>
> **Critical Path**: KB persistence → ingestion/indexing → retrieval-backed chat → demo UI/runbook → final verification

---

## Context

### Original Request
The user asked to chốt lại kiến trúc tối giản for an internal support bot and rewrite the current plan accordingly.

### Interview Summary
**Key Discussions**:
- This is an internal support chatbot, not a full virtual assistant.
- The bot must answer from internal knowledge and keep context during an active chat session.
- If the user closes the app, long-term conversation memory is not required.
- The architecture should stay pipeline-first with LangGraph orchestration.
- Upload should remain restricted to `admin` and `manager`.

**Research Findings**:
- No SDD framework detected (`openspec/` or `.specify/` absent).
- Existing API primitives already support chat, conversations, messages, and documents.
- The previous plan was too heavy because it emphasized durable conversation/checkpoint persistence.
- For this use case, the right center of gravity is a durable knowledge base plus short-lived session context.

### Metis Review
**Identified Gaps** (addressed):
- Overbuilt conversation durability → rewritten to ephemeral session context.
- Overbuilt checkpoint persistence → explicitly excluded.
- Missing demo story → simplified to internal support bot flow with known questions and internal docs.
- Missing measurable acceptance criteria → every task now has concrete, testable criteria.

---

## Work Objectives

### Core Objective
Turn the current Agentic RAG MVP into a dependable internal support bot that answers internal questions from durable knowledge while only keeping short-lived chat context for the active session.

### Concrete Deliverables
- Durable knowledge base storage and indexing
- Retrieval-backed chat using recent session context
- Safe upload permission enforcement
- Minimal API/UI flow for chat, upload, and document status
- Simple seed/reset/runbook for a repeatable demo
- Automated regression tests plus agent QA evidence

### Definition of Done
- [ ] A seeded or uploaded internal document can be searched and used in chat
- [ ] Chat can use recent turn context during the active session
- [ ] Closing/restarting the app does not need to preserve conversation history
- [ ] Unauthorized upload attempts return `403`
- [ ] Demo smoke tests and agent-executed QA scenarios pass

### Must Have
- Preserve pipeline-first RAG and LangGraph orchestration
- Keep conversation context short-lived; do not require durable conversation memory
- Persist the knowledge base and retrieval artifacts
- Keep upload restricted to `admin` and `manager`
- All verification remains agent-executed

### Must NOT Have (Guardrails)
- No durable LangGraph checkpoint persistence
- No long-term user conversation memory
- No autonomous assistant/workflow features beyond internal Q&A
- No enterprise document management suite
- No separate chat architecture outside the existing orchestration layer
- No hidden manual setup steps outside the runbook

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - all verification must be runnable by the executing agent.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: pytest for backend; existing frontend tooling if UI changes are included
- **Agent QA**: Mandatory for every task

### QA Policy
Every task must include agent-executed QA scenarios with exact commands, exact inputs, and evidence paths under `.omo/evidence/`.

- **Backend/API**: use `pytest`, `curl`, or a small Python harness
- **UI**: use Playwright if UI changes are included
- **CLI/demo scripts**: shell execution to verify commands and generated files

---

## Execution Strategy

### Parallel Execution Waves

#### Wave 1 — Knowledge base foundation
- Durable document metadata/storage
- Chunk storage and indexing contracts
- Session context boundary definition (keep chat memory short-lived)
- Demo story and success criteria skeleton

#### Wave 2 — Ingestion and retrieval
- Upload/seed ingestion path wired to parsing/chunking
- Indexing into a real retrieval store
- Retrieval candidates and source metadata returned to chat
- Graceful handling for invalid uploads, empty text, and indexing errors

#### Wave 3 — Chat and demo-facing flow
- Chat route uses retrieval plus recent session context
- Conversation list/history remains session-scoped or ephemeral as needed
- Minimal UI/API polish for upload, chat, and document status
- Clear loading/empty/error states for demo flow

#### Wave 4 — Demo hardening and runbook
- Seed data and scripted demo prompts
- Reset/cleanup flow
- End-to-end smoke tests for permissions, retrieval, and empty-state behavior
- Final evidence collection

### Dependency Matrix
- **Wave 1** blocks Wave 2 and Wave 3
- **Wave 2** blocks retrieval-backed chat demo scenarios in Wave 3
- **Wave 3** blocks runbook finalization in Wave 4
- **Wave 4** is the last integration gate

### Agent Dispatch Summary
- Persistence and contract work: `unspecified-high`
- Ingestion/retrieval wiring: `deep` and `unspecified-high`
- API/UI polish: `quick` or `visual-engineering`
- Demo scripts / runbook / documentation: `writing`
- Final verification / integration QA: `oracle` and `unspecified-high`

---

## TODOs

- [x] 1. Define the internal support bot story and measurable demo criteria

  **What to do**:
  - Document the internal support bot audience and the exact demo flow.
  - Define the minimal successful behavior: ask a question, retrieve internal evidence, answer correctly, and keep context during the active session.
  - State clearly that long-term conversation memory is out of scope.

  **Must NOT do**:
  - Do not expand this into a general assistant roadmap.
  - Do not require durable chat memory after app close.

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: requirements and runbook definition work.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: None directly; it informs the rest of the plan
  - **Blocked By**: None

  **References**:
  - `app/presentation/api/v1/agentic/router.py` - current demo surface and chat/upload routes
  - `.omo/drafts/internal-support-bot-minimal-architecture.md` - confirmed simplified architecture decision

  **Why Each Reference Matters**:
  - The router shows the current API surface that the demo must expose.
  - The draft captures the decision to keep only short-lived session context.

  **Acceptance Criteria**:
  - The story states the audience, primary user action, and expected result in 3-5 bullets.
  - The success criteria list includes a measurable pass/fail check for upload, chat, and retrieval.
  - The out-of-scope section explicitly states that long-term conversation memory is excluded.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Story clearly describes internal support bot
    Tool: writing
    Preconditions: None
    Steps:
      1. Read the story section.
      2. Verify it names internal knowledge, active-session context, and no long-term memory.
    Expected Result: A single concise demo flow is documented.
    Evidence: .omo/evidence/task-1-story.md

  Scenario: Scope excludes persistent chat memory
    Tool: writing
    Preconditions: None
    Steps:
      1. Read the out-of-scope section.
      2. Verify durable conversation memory and checkpoint persistence are excluded.
    Expected Result: The plan is clearly aligned to the minimal architecture.
    Evidence: .omo/evidence/task-1-scope.md
  ```

  **Commit**: NO

- [x] 2. Persist the knowledge base and retrieval artifacts

  **What to do**:
  - Persist documents, chunks, embeddings/index entries, document metadata, upload status, and access policy metadata.
  - Keep the knowledge base durable across app restarts.
  - Replace any remaining in-memory KB state with durable accessors.

  **Must NOT do**:
  - Do not persist long-term conversation memory.
  - Do not add durable LangGraph checkpoint storage in this task.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: backend persistence work touches multiple files and contracts.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 3-8 through KB contracts
  - **Blocked By**: None

  **References**:
  - `app/agentic/pipeline/ingestion/core.py` - ingestion entry point
  - `app/agentic/pipeline/retrieval/core.py` - retrieval contract
  - `app/infrastructure/database/models/` - existing persistence model patterns
  - `tests/unit/ai/test_ingestion.py` - ingestion behavior baseline

  **Why Each Reference Matters**:
  - Ingestion core and retrieval core define the KB data flow.
  - Database models show how durable storage should be shaped.
  - Tests define the current behavior that must be preserved.

  **Acceptance Criteria**:
  - Documents and chunks persist across restart.
  - Indexed retrieval artifacts can be loaded after restart.
  - Document metadata/status are queryable from durable storage.
  - The system can answer questions using persisted KB data after restart.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Knowledge base survives restart
    Tool: pytest
    Preconditions: Seed one document and index it.
    Steps:
      1. Query the indexed document.
      2. Restart the app/test fixture.
      3. Query the same document again.
    Expected Result: The document and retrieval artifacts remain available.
    Evidence: .omo/evidence/task-2-kb-restart.log

  Scenario: Document metadata round-trip works
    Tool: pytest
    Preconditions: Upload or seed a document.
    Steps:
      1. Persist metadata and status.
      2. Reload list/detail endpoints.
      3. Verify the same record is returned.
    Expected Result: Durable storage returns the same document record.
    Evidence: .omo/evidence/task-2-document-roundtrip.log
  ```

  **Commit**: YES
  - Message: `feat(agentic): persist knowledge base artifacts`
  - Files: storage models/adapters, ingestion/retrieval persistence
  - Pre-commit: `pytest tests/unit/ai/test_ingestion.py tests/unit/ai/test_retrieval.py`

- [x] 3. Wire upload ingestion into parsing, chunking, and indexing

  **What to do**:
  - Connect uploaded or seeded files to the real parsing/chunking/indexing flow.
  - Store ingestion status, parse failures, and chunk metadata.
  - Ensure document content becomes searchable in the retrieval store.

  **Must NOT do**:
  - Do not add a second ingestion pipeline outside the current architecture.
  - Do not support every file format if the demo only needs the curated set.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: end-to-end pipeline wiring with parsing, chunking, indexing, and failure handling.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2A
  - **Blocks**: Tasks 4-8 through the indexing contract
  - **Blocked By**: Task 2

  **References**:
  - `app/agentic/pipeline/ingestion/core.py` - ingestion entry point
  - `app/agentic/pipeline/parsing/` - parser patterns and supported file types
  - `app/agentic/pipeline/chunking/core.py` - chunk boundary behavior
  - `app/agentic/pipeline/indexing/core.py` - indexing contract
  - `tests/unit/ai/test_ingestion.py` - existing ingestion expectations

  **Why Each Reference Matters**:
  - Ingestion core defines how uploaded files become ingestible sources.
  - Parsing and chunking determine what text the bot can retrieve.
  - Indexing is required so chat can surface internal evidence.
  - Existing tests tell us the baseline behavior to keep.

  **Acceptance Criteria**:
  - Uploading a document produces parse/chunk/index artifacts.
  - Ingestion status is visible and failure cases are represented.
  - Indexed documents can be found by retrieval.
  - Demo documents are ready without manual DB edits.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Valid demo document ingests end-to-end
    Tool: pytest
    Preconditions: Known-good PDF/DOCX/MD sample exists.
    Steps:
      1. Upload the document.
      2. Observe ingestion status changes.
      3. Confirm chunks are created and indexed.
    Expected Result: Document becomes searchable and has a stable document_id.
    Evidence: .omo/evidence/task-3-ingest-success.log

  Scenario: Unsupported or empty document fails gracefully
    Tool: pytest
    Preconditions: Upload malformed/unsupported file.
    Steps:
      1. Upload the bad file.
      2. Read the ingestion failure response.
    Expected Result: Clear failure status without crashing the app.
    Evidence: .omo/evidence/task-3-ingest-failure.log
  ```

  **Commit**: YES
  - Message: `feat(agentic): wire document ingestion pipeline`
  - Files: ingestion, parsing, chunking, indexing modules
  - Pre-commit: `pytest tests/unit/ai/test_ingestion.py tests/unit/ai/test_chunking.py tests/unit/ai/test_parsing_*`

- [x] 4. Replace empty retrieval with a real searchable store

  **What to do**:
  - Plug the chat path into a retrieval store that can return indexed chunks.
  - Return source metadata and evidence identifiers with retrieved candidates.
  - Make retrieval deterministic enough for internal support questions.

  **Must NOT do**:
  - Do not build a new retrieval abstraction if the current one is sufficient.
  - Do not make retrieval dependent on the demo UI.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: retrieval quality and answer grounding are core bot risks.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES, after the indexing contract from Task 3 is available
  - **Parallel Group**: Wave 2B
  - **Blocks**: Tasks 5-8
  - **Blocked By**: Tasks 2 and 3

  **References**:
  - `app/agentic/pipeline/retrieval/core.py` - retrieval store contract
  - `app/agentic/adapters/vector_store/` - existing vector store adapters
  - `app/agentic/orchestration/rag_graph.py` - how retrieval is injected into chat
  - `app/agentic/orchestration/nodes/retrieve_evidence.py` - evidence retrieval behavior
  - `tests/unit/ai/test_retrieval.py` - current retrieval expectations

  **Why Each Reference Matters**:
  - Retrieval core tells us the interface to implement.
  - Vector store adapters show the repo’s preferred storage shape.
  - The graph and retrieve node show where evidence is consumed.
  - Existing tests define the current baseline and edge cases.

  **Acceptance Criteria**:
  - Retrieval returns relevant chunks for seeded internal docs.
  - Empty retrieval is handled gracefully.
  - Retrieved items include source metadata for citations.
  - Demo questions can hit expected documents consistently.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Seeded question retrieves expected source
    Tool: pytest
    Preconditions: Demo corpus is indexed.
    Steps:
      1. Ask a known internal support question.
      2. Inspect retrieval candidates.
      3. Verify expected chunk/document ids appear.
    Expected Result: Retrieval returns the expected source evidence.
    Evidence: .omo/evidence/task-4-retrieval-success.log

  Scenario: Empty store produces safe fallback
    Tool: pytest
    Preconditions: Retrieval index is empty.
    Steps:
      1. Query the chat endpoint.
      2. Observe the answer status.
    Expected Result: No unsupported confident answer is produced.
    Evidence: .omo/evidence/task-4-retrieval-empty.log
  ```

  **Commit**: YES
  - Message: `feat(agentic): connect retrieval store`
  - Files: retrieval adapters, graph wiring, retrieve node
  - Pre-commit: `pytest tests/unit/ai/test_retrieval.py tests/unit/ai/test_session_memory.py`

- [x] 5. Ground chat answers in retrieved evidence and short-lived session context

  **What to do**:
  - Ensure chat uses recent session context plus retrieved evidence.
  - Keep the `conversation_id -> thread_id` relationship for the active session.
  - Keep citation/source data attached to the response.
  - Maintain graceful behavior for missing evidence or refusal cases.

  **Must NOT do**:
  - Do not require long-term conversation memory after app close.
  - Do not expose raw chain-of-thought or internal tool traces in demo responses.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: chat behavior touches orchestration, session context, and response shaping.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 6-8
  - **Blocked By**: Tasks 2, 3, and 4

  **References**:
  - `app/presentation/api/v1/agentic/router.py` - current chat and history endpoints
  - `app/agentic/orchestration/session_flow.py` - session/thread behavior
  - `app/agentic/orchestration/nodes/generate_answer.py` - answer generation boundary
  - `tests/unit/test_agentic_api.py` - current API smoke tests

  **Why Each Reference Matters**:
  - The router is where session context and retrieval meet.
  - Session flow preserves the thread continuity contract for the active session.
  - Answer generation is where grounded responses are formed.
  - API tests tell us what the bot endpoints must continue to satisfy.

  **Acceptance Criteria**:
  - Chat answers use retrieved evidence when available.
  - Recent session context influences follow-up questions during the active chat.
  - Answer response includes citations/source identifiers.
  - Empty retrieval produces a safe, understandable fallback.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Known internal question returns grounded answer
    Tool: pytest
    Preconditions: Demo documents are indexed and session exists.
    Steps:
      1. Send question through chat endpoint.
      2. Ask a follow-up question in the same session.
      3. Verify answer and citations align with retrieved evidence.
    Expected Result: Grounded answer is returned and session context is respected.
    Evidence: .omo/evidence/task-5-chat-grounded.log

  Scenario: Follow-up question reuses active session context
    Tool: pytest
    Preconditions: Existing session with prior turn.
    Steps:
      1. Send follow-up question using same session.
      2. Verify the recent turn history is used.
      3. Verify the response is coherent without durable memory.
    Expected Result: Active-session continuity is preserved; no long-term memory is required.
    Evidence: .omo/evidence/task-5-chat-history.log
  ```

  **Commit**: YES
  - Message: `feat(agentic): ground chat in retrieval and session context`
  - Files: router, orchestration nodes, session flow helpers
  - Pre-commit: `pytest tests/unit/test_agentic_api.py tests/unit/ai/test_session_memory.py tests/unit/ai/test_generation.py`

- [x] 6. Polish the demo-facing API/UI flow for upload, chat, and document status

  **What to do**:
  - Make the upload, chat, and document status flow easy to demo.
  - Add loading, empty, and error states where users need them.
  - Ensure the UI/API does not require users to know internal storage details.

  **Must NOT do**:
  - Do not redesign the full product UI.
  - Do not add advanced admin UX beyond what the demo needs.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: user-facing demo polish and state handling.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 2-5

  **References**:
  - `app/presentation/api/v1/agentic/router.py` - demo-facing backend route shape
  - frontend app modules that consume the API - upload/chat/document status UI entry points
  - existing component patterns in the frontend app

  **Why Each Reference Matters**:
  - The router defines what the UI can show.
  - Frontend patterns must be followed for consistent demo presentation.

  **Acceptance Criteria**:
  - A demo user can upload → chat → inspect document status without internal IDs.
  - Each visible state has a concrete loading/empty/error message in the UI or API response.
  - The upload/history/document controls are reachable from the main demo surface in one click or one route change.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Demo user can upload, chat, and inspect document status
    Tool: Playwright
    Preconditions: Demo app is running with seeded data.
    Steps:
      1. Open the demo page.
      2. Upload a known document.
      3. Ask a known question.
      4. Inspect document status or source info.
    Expected Result: Upload, chat, and document status are visible in one smooth flow.
    Evidence: .omo/evidence/task-6-demo-flow.png

  Scenario: UI shows clear error state on forbidden upload
    Tool: Playwright
    Preconditions: Logged in as employee role.
    Steps:
      1. Open upload UI.
      2. Attempt to upload a file.
      3. Observe the error message.
    Expected Result: A clear forbidden message is shown without crashing the UI.
    Evidence: .omo/evidence/task-6-upload-forbidden.png
  ```

  **Commit**: YES
  - Message: `feat(ui): polish internal support demo flow`
  - Files: frontend upload/chat/document views
  - Pre-commit: frontend test/lint command as appropriate

- [x] 7. Build the demo seed, reset, and runbook flow

  **What to do**:
  - Create a repeatable seed command for demo documents and any minimal session bootstrap.
  - Create a reset/cleanup path so the demo can be rerun from a known state.
  - Write the runbook that explains exact steps to start the demo.

  **Must NOT do**:
  - Do not depend on manual database edits.
  - Do not bury environment requirements outside the runbook.
  - Do not require persistent chat memory in the demo runbook.

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: mostly operational documentation and scripted setup.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Final verification only
  - **Blocked By**: Tasks 1-6 for final runbook validation; seed/reset skeleton can start earlier

  **References**:
  - repo scripts/commands used for seeding or migration
  - `.omo/evidence/` patterns for capturing run outputs
  - existing backend setup and test fixtures

  **Why Each Reference Matters**:
  - The runbook must match real commands and project conventions.
  - Seed/reset behavior must be repeatable in practice.

  **Acceptance Criteria**:
  - The seed command creates at least one demo document and prints a clear success message.
  - The reset command/procedure restores demo data to a known baseline and exits successfully.
  - The runbook lists exact commands for prerequisites, backend start, optional frontend start, seed/reset, and the scripted demo questions.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Seed command prepares demo data
    Tool: bash
    Preconditions: Clean environment or reset state.
    Steps:
      1. Run the seed command.
      2. Check resulting documents/conversations exist.
    Expected Result: Demo corpus and expected state are ready.
    Evidence: .omo/evidence/task-7-seed.log

  Scenario: Reset command restores clean demo state
    Tool: bash
    Preconditions: Existing demo state present.
    Steps:
      1. Run reset/cleanup.
      2. Re-run list endpoints.
    Expected Result: Demo state is cleared or returned to known baseline.
    Evidence: .omo/evidence/task-7-reset.log
  ```

  **Commit**: YES
  - Message: `docs(demo): add internal support seed and runbook`
  - Files: scripts, docs, demo seed assets
  - Pre-commit: script validation command

- [x] 8. Run end-to-end verification for the internal support bot demo path

  **What to do**:
  - Verify the full demo flow from a clean start.
  - Exercise happy path and failure modes.
  - Collect evidence artifacts for the demo path and final approval.

  **Must NOT do**:
  - Do not accept manual-only verification.
  - Do not skip failure scenarios.
  - Do not require long-term conversation memory in the final demo.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: end-to-end verification across backend and optionally UI.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential final integration
  - **Blocks**: Final sign-off
  - **Blocked By**: Tasks 1-7

  **References**:
  - `.omo/drafts/internal-support-bot-minimal-architecture.md` - baseline requirements and scope
  - `tests/unit/test_agentic_api.py` - API smoke coverage
  - `tests/unit/ai/test_conversation_registry.py` - baseline contract checks

  **Why Each Reference Matters**:
  - The draft captures the agreed minimal architecture scope.
  - The tests tell us what the system currently guarantees.

  **Acceptance Criteria**:
  - The final verification runs the full demo path: seeded upload/selection, grounded question, document status check, and forbidden upload check.
  - At least 3 negative cases are exercised: forbidden upload, empty retrieval, and malformed or unsupported file.
  - Evidence files exist for each executed demo scenario.
  - The runbook is sufficient to start the demo without asking the author for missing steps.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Full demo path succeeds
    Tool: Playwright + pytest + bash
    Preconditions: Demo seed is loaded.
    Steps:
      1. Start the app.
      2. Open the demo UI.
      3. Upload or select seeded documents.
      4. Ask a known question.
      5. Inspect citations/document status.
    Expected Result: End-to-end demo completes successfully.
    Evidence: .omo/evidence/task-8-full-demo.log

  Scenario: Demo failure cases remain safe
    Tool: pytest
    Preconditions: Invalid upload or empty retrieval state.
    Steps:
      1. Trigger forbidden upload.
      2. Trigger empty retrieval.
      3. Trigger a bad file upload.
    Expected Result: All failure states are handled gracefully with clear messages.
    Evidence: .omo/evidence/task-8-demo-failures.log
  ```

  **Commit**: NO

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify that the internal-support-bot scope is complete, the waves are dependency-safe, and every task has concrete acceptance criteria plus QA scenarios. Confirm the plan stays within the minimal architecture and preserves the existing pipeline-first design.

  **Recommended Agent Profile**:
  - **Category**: `oracle`
    - Reason: read-only plan compliance audit benefits from independent reasoning.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Final Verification Wave
  - **Blocks**: Final sign-off
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - Must Have and Must NOT Have sections are fully reflected in the task list.
  - Every numbered task contains both acceptance criteria and QA scenarios.
  - No task reintroduces durable checkpoint persistence or long-term memory.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Plan sections match minimal architecture
    Tool: oracle
    Preconditions: Final plan file exists.
    Steps:
      1. Read the Must Have and Must NOT Have sections.
      2. Read all numbered tasks.
      3. Verify there is no contradiction.
    Expected Result: The plan is internally consistent with the minimal architecture.
    Evidence: .omo/evidence/f1-plan-compliance.md
  ```

  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Plan Quality Review** — `unspecified-high`
  Check that the plan is practical to execute, the tasks are correctly sized, the wave structure maximizes parallelism, and the references point to real code areas. Flag any missing internal-support-bot edge cases or dependency mistakes.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: plan quality review needs broad implementation awareness without editing.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Final Verification Wave
  - **Blocks**: Final sign-off
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - Each task is scoped small enough to be actionable.
  - Wave ordering and dependency constraints are executable without contradictions.
  - References are concrete enough for an executor to locate the relevant code area.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Task sizing and wave structure are executable
    Tool: unspecified-high
    Preconditions: Final plan file exists.
    Steps:
      1. Review every task and wave assignment.
      2. Check dependency chains for contradictions.
      3. Verify references name real code areas or artifacts.
    Expected Result: The plan is practical to execute without restructuring.
    Evidence: .omo/evidence/f2-plan-quality.md
  ```

  Output: `Structure [PASS/FAIL] | Parallelism [PASS/FAIL] | References [PASS/FAIL] | VERDICT`

- [x] F3. **Demo Readiness QA Review** — `unspecified-high`
  Review the QA scenarios for realism and completeness. Ensure upload, grounded chat, short-lived context, empty retrieval, and unauthorized upload are covered by executable checks with evidence outputs.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: demo QA review spans API, UI, scripts, and edge-case coverage.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Final Verification Wave
  - **Blocks**: Final sign-off
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - The QA scenarios cover the happy path for upload and grounded answering.
  - The QA scenarios cover negative cases for forbidden upload, empty retrieval, and bad file ingestion.
  - Every critical scenario has a named evidence path.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: QA coverage matches demo-critical paths
    Tool: unspecified-high
    Preconditions: Final plan file exists.
    Steps:
      1. Review all QA scenario blocks.
      2. Count happy-path and negative-path coverage.
      3. Verify evidence paths exist in every critical scenario definition.
    Expected Result: Demo-critical verification coverage is complete.
    Evidence: .omo/evidence/f3-demo-qa-review.md
  ```

  Output: `Scenarios [N/N pass] | Edge Cases [N/N] | Evidence [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Compare the plan against the draft and current repo patterns. Verify that the plan does not add long-term conversation memory or durable checkpoint persistence, does not introduce a separate architecture path, and does not creep into enterprise assistant behavior.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: scope fidelity requires cross-plan reasoning against architecture boundaries.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Final Verification Wave
  - **Blocks**: Final sign-off
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - The plan remains aligned with the minimal internal-support-bot draft.
  - No task requires long-term conversation memory or durable checkpoint persistence.
  - No task expands scope into virtual-assistant or enterprise-suite behavior.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Scope remains constrained to minimal support bot
    Tool: deep
    Preconditions: Final draft and plan files exist.
    Steps:
      1. Compare the draft scope boundaries with the final task list.
      2. Search for tasks that imply long-term memory or assistant autonomy.
      3. Check that pipeline-first RAG remains the only architecture path.
    Expected Result: The plan remains faithful to the simplified architecture.
    Evidence: .omo/evidence/f4-scope-fidelity.md
  ```

  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Scope Creep [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

- **1-4**: knowledge base and retrieval foundations
- **5-6**: chat grounding and UI polish
- **7**: seed/runbook assets
- **8**: verification only, no code commit

---

## Success Criteria

### Verification Commands
```bash
pytest tests/unit/test_agentic_api.py tests/unit/ai/test_conversation_registry.py
# Expected: all relevant demo-path tests pass
```

### Final Checklist
- [ ] Demo story and success criteria are explicit
- [ ] Knowledge base is durable
- [ ] Retrieval-backed chat works on seeded docs
- [ ] UI/API demo flow is understandable and repeatable
- [ ] Seed/reset/runbook exists and matches real commands
- [ ] Full demo verification passes with evidence
