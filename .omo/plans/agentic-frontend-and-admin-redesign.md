# Agentic Frontend, Contrast, and Navigation Redesign Plan

## TL;DR

> **Quick Summary**: Deliver full frontend coverage for the agentic/admin APIs, standardize text colors and readability across admin pages, and redesign admin navigation so system tools like menu sync and i18n sync are deprioritized under an Advanced/Admin tools grouping.
>
> **Deliverables**:
> - Full agentic frontend service/model/UI coverage for all backend agentic endpoints
> - Contrast-safe admin styling tokens and page-level cleanup for readability
> - Reworked admin navigation grouping with Advanced/Admin tools handling for config sync routes
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Backend API coverage matrix -> missing frontend surfaces -> contrast token standardization -> nav regrouping

---

## Context

### Original Request
The user asked for a plan to:
1. Add all remaining Agent/agentic APIs to the frontend.
2. Check the entire admin UI again because text colors currently blend into backgrounds.
3. Redesign navigation/tab grouping because `menu_sync` and `i18n_sync` appear underused and should likely be deprioritized under Advanced/Admin tools.

### Interview Summary
**Key Discussions**:
- Priority is **Agent APIs first**.
- Scope is **full coverage**, not just MVP completion.
- `menu_sync` and `i18n_sync` should remain available but be **deprioritized under Advanced / Admin tools**.
- UI work is **contrast-first**, but light layout tweaks are allowed if needed for readability.

**Research Findings**:
- Backend agentic API surface contains 9 endpoints: 3 conversation routes, 2 chat routes, and 2 document routes plus 2 detail routes.
- Frontend currently has a partial agentic service/model/chat UI, but is missing document detail, conversation detail, policy-aware upload UI, and richer conversation/document admin screens.
- Shared page styles already exist, but most admin pages duplicate dark/light text colors and card/table styles.
- Current nav is flat, but breadcrumbs and permissions already imply natural groups.
- `menu_sync` and `i18n_sync` are real admin-only config tools; they should be regrouped, not removed.

### Metis Review
**Identified Gaps** (addressed):
- Needed explicit scope decisions for Agent coverage, nav placement, and UI redesign depth.
- Needed guardrails to prevent a full theme redesign from swallowing the contrast pass.
- Needed explicit confirmation that menu/i18n sync should remain available but deprioritized.
- Needed to define whether the plan is full coverage or MVP-only. This is now resolved to **full coverage**.

---

## Work Objectives

### Core Objective
Build full admin frontend coverage for the agentic API surface, make text readable across the admin UI through semantic contrast tokens and targeted page cleanup, and regroup the admin nav so system tools are secondary to core business areas.

### Concrete Deliverables
- Full agentic frontend models and service methods for all backend agentic endpoints
- New/expanded admin screens for conversation and document management
- Updated `/chat` UX to support full conversation-aware agentic workflows
- Contrast-safe shared tokens and page styles for existing admin surfaces
- Navigation rework that groups business pages, operations, security, and advanced system tools
- Deprioritized `menu_sync` and `i18n_sync` under Advanced / Admin tools

### Definition of Done
- [ ] Every backend agentic endpoint has an explicit frontend coverage status: covered, partial, new, or deferred for a documented reason
- [ ] All full-coverage Agent UI deliverables are implemented and reachable through admin routes
- [ ] Shared styling tokens eliminate the major text-on-background readability issues on in-scope pages
- [ ] Navigation groups are updated and `menu_sync` / `i18n_sync` are deprioritized under Advanced / Admin tools
- [ ] Build and targeted QA checks pass for touched frontend areas

### Must Have
- Full agentic API coverage in the admin frontend
- Shared frontend models for all exposed agentic contracts
- Policy-aware upload handling in the frontend
- Conversation-aware UI for list/detail/history/chat workflows
- Document list/detail/upload UI
- Contrast-first text and surface tokens
- Navigation regrouping that preserves existing routes and permissions
- `menu_sync` and `i18n_sync` remain accessible to permitted admins

### Must NOT Have (Guardrails)
- No backend API shape changes unless a verified mismatch blocks frontend integration
- No removal of `menu_sync` or `i18n_sync`
- No route path renames unless explicitly justified and approved
- No full theme overhaul unless required for contrast readability
- No broad layout redesign beyond what is needed to make text readable and groups coherent
- No new design system from scratch; prefer reusing and extending existing admin page style utilities

### Spec Framework Integration
- **Detected Framework**: None
- **Config File**: N/A
- **Active Specs**: N/A
- **Active Changes/Proposals**: N/A
- **Available Commands**: N/A
- **Spec-to-Task Mapping**: N/A

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after / targeted QA, with full build verification
- **Framework**: Existing frontend test stack + Playwright for browser QA where user-facing
- **If TDD**: Not required for the whole plan; targeted tests can be added where useful for shared models/services/components

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright - navigate, interact, assert DOM, screenshot
- **API/Backend**: Use curl for backend route checks when needed to validate frontend assumptions
- **Library/Module**: Use build/test/lint commands and browser snapshots for verification

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - parallel, start immediately):
├── Task 1: Agentic models coverage + contract normalization [quick]
├── Task 2: Agentic service completion for missing endpoints + policy upload [unspecified-high]
├── Task 3: Admin route/shell entry points for new agentic screens [quick]
├── Task 4: Shared contrast tokens + admin page style standardization [unspecified-high]
└── Task 5: Navigation grouping model + Advanced/Admin tools treatment [unspecified-high]

Wave 2 (Agentic UI surfaces - parallel after Wave 1):
├── Task 6: Conversation list/detail/history UI [unspecified-high]
├── Task 7: Document list/detail/upload UI [unspecified-high]
├── Task 8: Chat page upgrade to conversation-aware flow [visual-engineering]
├── Task 9: Readability audit + page-specific contrast cleanup [unspecified-high]
└── Task 10: Sidebar regrouping + breadcrumbs/nav updates [unspecified-high]

Wave 3 (Integration + polish - parallel):
├── Task 11: Agentic page integration polish + permission/state/error handling [unspecified-high]
├── Task 12: Cross-page contrast regression cleanup + shared utility adoption [unspecified-high]
├── Task 13: Advanced/Admin tools placement refinement for menu/i18n sync [quick]
└── Task 14: Build, browser QA, and route regression sweep [unspecified-high]

Wave FINAL (4 parallel reviewers, then user okay):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Real browser QA [unspecified-high]
├── Task F4: Scope fidelity check [deep]
-> Present results -> Get explicit user okay
```

### Dependency Matrix

- **1-5**: foundational, mostly parallel; 2 depends on 1, 6-8 depend on 2/3, 9 depends on 4, 10 depends on 5
- **6**: depends on 1, 2, 3
- **7**: depends on 1, 2, 3
- **8**: depends on 2, 3
- **9**: depends on 4, partially on 6-8 for page coverage context
- **10**: depends on 5 and route metadata from 3
- **11-13**: depend on 6-10 as appropriate
- **14**: depends on all implementation tasks

### Agent Dispatch Summary

- **Wave 1**: 5 tasks - T1, T3 -> `quick`; T2, T4, T5 -> `unspecified-high`
- **Wave 2**: 5 tasks - T6, T7, T9, T10 -> `unspecified-high`; T8 -> `visual-engineering`
- **Wave 3**: 4 tasks - T11, T12, T14 -> `unspecified-high`; T13 -> `quick`
- **FINAL**: 4 tasks - F1 -> `oracle`; F2 -> `unspecified-high`; F3 -> `unspecified-high`; F4 -> `deep`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> A task WITHOUT QA Scenarios is INCOMPLETE.
> FORMAT: Task labels MUST use bare numbers: `1.`, `2.`, `3.` — NOT `T1.`, `Task 1.`, `Phase 1:`.
> Final Verification Wave labels MUST use `F1.`, `F2.`, etc. — NOT `T-F1.`, `F-1.`, `Final 1.`.

- [x] 1. Agentic API coverage matrix and model normalization

  **What to do**:
  - Verify the backend agentic endpoint inventory from `app/presentation/api/v1/agentic/router.py` and `app/presentation/schemas/agentic_schema.py`.
  - Expand `apps/admin/src/app/models/agentic.models.ts` so exported frontend models cover conversations, messages, chat responses, document summaries, document upload payloads, and response wrappers.
  - Remove duplicated private agentic interfaces from `AgenticApiService` once exported model coverage exists.

  **Must NOT do**:
  - Do not change backend response contracts.
  - Do not add placeholder models that are not backed by backend schemas.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Type/model normalization is bounded and mostly single-file with contract references.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Use to confirm backend schema and frontend references.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI design work in this task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3, 4, 5)
  - **Blocks**: Tasks 2, 6, 7, 8
  - **Blocked By**: None

  **References**:
  - `app/presentation/schemas/agentic_schema.py:7-81` - Backend schemas to mirror.
  - `apps/admin/src/app/models/agentic.models.ts:1-32` - Current partial frontend model file.
  - `apps/admin/src/app/services/agentic-api.service.ts:12-49` - Private interfaces to replace with exported models.

  **Acceptance Criteria**:
  - [ ] `agentic.models.ts` exports models for all backend agentic schema equivalents.
  - [ ] `agentic-api.service.ts` imports exported agentic models instead of defining duplicate private response types.
  - [ ] `npm run build` in `apps/admin` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Type contract build succeeds
    Tool: Bash
    Preconditions: Repository dependencies installed.
    Steps:
      1. Run `cd apps/admin && npm run build`.
      2. Assert exit code is 0.
      3. Assert output includes `Application bundle generation complete`.
    Expected Result: Frontend builds without TypeScript errors after model normalization.
    Failure Indicators: TS compile errors, missing exported types, or private duplicate types remain.
    Evidence: .omo/evidence/task-1-model-build.txt
  ```

  **Commit**: NO (group with Wave 1)

- [x] 2. Complete AgenticApiService endpoints and policy-aware upload

  **What to do**:
  - Add missing `getConversation(conversationId)` and `getDocument(documentId)` methods.
  - Extend `uploadDocument(...)` to send policy fields: `classification`, `visibility_scope`, `allowed_roles`, and `department_id` when provided.
  - Preserve existing methods for quick chat, conversation chat, list conversations, list messages, and list documents.

  **Must NOT do**:
  - Do not introduce a second API client.
  - Do not hardcode backend base URLs.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Needs endpoint coverage and upload FormData correctness.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Confirm endpoint paths and consumers.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI implementation in this task.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 after Task 1
  - **Blocks**: Tasks 6, 7, 8, 11
  - **Blocked By**: Task 1

  **References**:
  - `app/presentation/api/v1/agentic/router.py:84-356` - Backend endpoint definitions.
  - `apps/admin/src/app/services/base-api.service.ts` - URL construction pattern.
  - `apps/admin/src/app/services/user-api.service.ts` - Existing service method pattern.

  **Acceptance Criteria**:
  - [ ] Service exposes all 9 backend agentic endpoint interactions.
  - [ ] Upload service appends policy fields only when present and preserves file upload.
  - [ ] `npm run build` in `apps/admin` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Service endpoint coverage compiles
    Tool: Bash
    Preconditions: Task 1 completed.
    Steps:
      1. Run `cd apps/admin && npm run build`.
      2. Assert exit code is 0.
      3. Search `agentic-api.service.ts` for `getConversation(` and `getDocument(`.
    Expected Result: Missing detail service methods exist and compile.
    Failure Indicators: Missing method names, TS errors, or hardcoded URLs.
    Evidence: .omo/evidence/task-2-service-coverage.txt
  ```

  **Commit**: NO (group with Wave 1)

- [x] 3. Agentic admin route shell and navigation entries

  **What to do**:
  - Add routes for agentic conversations and documents using existing lazy standalone component route pattern.
  - Add nav entries under an Agent/AI or Workspace grouping placeholder, keeping `/chat` available.
  - Ensure route guards follow existing admin conventions.

  **Must NOT do**:
  - Do not remove or rename `/chat`.
  - Do not change existing route paths unrelated to agentic pages.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Route/nav wiring is bounded and pattern-based.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Confirm route and shell nav patterns.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No symbol rename/move planned.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 4, 5)
  - **Blocks**: Tasks 6, 7, 8, 10
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/app.routes.ts:85-90` - Existing `/chat` route.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:204-218` - Current flat nav item list.

  **Acceptance Criteria**:
  - [ ] New agentic routes are lazy-loaded and guarded consistently.
  - [ ] `/chat` still resolves.
  - [ ] `npm run build` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Direct agentic routes resolve through router
    Tool: Playwright
    Preconditions: Admin dev server running and user authenticated.
    Steps:
      1. Navigate to `http://localhost:4200/chat`.
      2. Navigate to each new agentic route created by this task.
      3. Assert no route redirects to `/not-found` for authenticated admin.
    Expected Result: Agentic routes render their page shells.
    Failure Indicators: 404, not-found page, unauthorized for valid admin, or console route errors.
    Evidence: .omo/evidence/task-3-agentic-routes.md
  ```

  **Commit**: NO (group with Wave 1)

- [x] 4. Shared contrast tokens and admin page style foundation

  **What to do**:
  - Define semantic text/background/border/action tokens using existing shared style utilities.
  - Update `ADMIN_PAGE_COMMON_STYLES` or equivalent shared style layer for contrast-safe defaults.
  - Establish table/modal text strategy: explicit light-surface text or dark-surface text, not mixed accidentally.

  **Must NOT do**:
  - Do not perform a full visual theme rewrite.
  - Do not change data density/layout except where readability requires it.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-page visual foundation with risk of regressions.
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Needed for contrast/readability choices.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No broad source move or rename planned.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 5)
  - **Blocks**: Tasks 9, 12
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/shared/admin-page-styles.ts:1-70` - Existing shared page style utility.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:80-183` - Shell color usage.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts:40` - Inline nav/sidebar hardcoded styles.

  **Acceptance Criteria**:
  - [ ] Shared style tokens/classes exist for primary, secondary, muted, card, table, modal, and action text contexts.
  - [ ] Existing shared page styles use semantic tokens instead of repeated raw colors where feasible.
  - [ ] `npm run build` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Shared contrast style foundation builds
    Tool: Bash
    Preconditions: Task starts from current admin frontend.
    Steps:
      1. Run `cd apps/admin && npm run build`.
      2. Search shared style files for newly defined semantic text tokens.
      3. Assert build output completes successfully.
    Expected Result: Shared contrast foundation compiles and is available for page cleanup.
    Failure Indicators: CSS/TS build errors or absence of semantic tokens/classes.
    Evidence: .omo/evidence/task-4-contrast-foundation.txt
  ```

  **Commit**: NO (group with Wave 1)

- [x] 5. Navigation grouping data model and Advanced/Admin tools design

  **What to do**:
  - Use existing optional `group?: string` nav item field or equivalent structure to define nav groups.
  - Design groups for Workspace, Agent/AI, Organization, Access Control, Operations, Security, and Advanced/Admin tools.
  - Place `menu_sync` and `i18n_sync` under Advanced/Admin tools while preserving direct route access and permission guards.

  **Must NOT do**:
  - Do not remove `menu_sync` or `i18n_sync`.
  - Do not rename route paths or permission keys.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Information architecture affects all admin users and permissions.
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Needed for navigation hierarchy decisions.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No rename/move required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Tasks 10, 13
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts:7-13` - Existing `ShellNavItem` type includes optional `group`.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:204-218` - Current flat nav list.
  - `docs/admin-sync-operations.md` - Evidence that sync routes are admin-only tools.

  **Acceptance Criteria**:
  - [ ] Proposed nav grouping preserves all existing route paths.
  - [ ] `menu_sync` and `i18n_sync` are assigned to Advanced/Admin tools.
  - [ ] Permission filtering still hides groups with no visible children.

  **QA Scenarios**:
  ```
  Scenario: Admin tools are grouped but still reachable
    Tool: Playwright
    Preconditions: Admin authenticated with `system.config.manage`.
    Steps:
      1. Navigate to `http://localhost:4200/config/menu-sync`.
      2. Assert page does not return not-found.
      3. Navigate to `http://localhost:4200/config/i18n-sync`.
      4. Assert page does not return not-found.
    Expected Result: Both tools remain reachable after grouping design.
    Failure Indicators: Route removed, 404, or permission regression for valid admin.
    Evidence: .omo/evidence/task-5-admin-tools-routing.md
  ```

  **Commit**: NO (group with Wave 1)

- [x] 6. Conversation list, detail, and message history UI

  **What to do**:
  - Build conversation list UI using `GET /api/v1/agentic/conversations`.
  - Build conversation detail UI using `GET /api/v1/agentic/conversations/{conversation_id}`.
  - Load message history using `GET /api/v1/agentic/conversations/{conversation_id}/messages`.
  - Include loading, empty, error, and not-found states.

  **Must NOT do**:
  - Do not fake conversations with local-only state.
  - Do not omit error states for missing or unauthorized conversations.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multi-endpoint UI with state transitions.
  - **Skills**: [`frontend-ui-ux`, `gitnexus-exploring`]
    - `frontend-ui-ux`: UI layout/readability.
    - `gitnexus-exploring`: Confirm service and route consumers.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No broad refactor required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 1, 2, 3

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts` - List/detail/modal page pattern.
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts` - All-in-one list/action pattern.
  - `app/presentation/api/v1/agentic/router.py:84-135` - Conversation routes.

  **Acceptance Criteria**:
  - [ ] Conversation list page renders persisted conversations from the API.
  - [ ] Conversation detail displays ID, status/title/thread metadata where available.
  - [ ] Message history displays persisted user and assistant messages.

  **QA Scenarios**:
  ```
  Scenario: Conversation list and detail load
    Tool: Playwright
    Preconditions: Backend running with authenticated admin session.
    Steps:
      1. Navigate to the agentic conversations route.
      2. Assert a conversation list, empty state, or API error state is visible.
      3. Open a conversation detail if one exists.
      4. Assert message history or empty history state is visible.
    Expected Result: Conversation UI handles list/detail/history states without crashing.
    Failure Indicators: Blank panel, unhandled exception, or missing loading/error/empty states.
    Evidence: .omo/evidence/task-6-conversation-ui.md
  ```

  **Commit**: NO (group with Wave 2)

- [x] 7. Document list, detail, and policy-aware upload UI

  **What to do**:
  - Build document list using `GET /api/v1/agentic/documents`.
  - Build document detail using `GET /api/v1/agentic/documents/{document_id}`.
  - Build upload UI using `POST /api/v1/agentic/documents` with policy fields.
  - Validate required policy fields before submit: `allowed_roles` for role scope and `department_id` for department scope.

  **Must NOT do**:
  - Do not send file-only uploads after service supports policy fields.
  - Do not expose upload actions to users lacking backend-required permissions.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Upload forms, validation, detail/list states.
  - **Skills**: [`frontend-ui-ux`, `gitnexus-exploring`]
    - `frontend-ui-ux`: Upload form and table readability.
    - `gitnexus-exploring`: Confirm upload policy rules.
  - **Skills Evaluated but Omitted**:
    - `security-research`: Not a security audit, only existing permission respect.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 8, 9, 10)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 1, 2, 3

  **References**:
  - `app/presentation/api/v1/agentic/router.py:229-356` - Document upload/list/detail routes and policy logic.
  - `apps/admin/src/app/features/rbac/roles-page.component.ts` - Checkbox/assignment modal pattern.
  - `apps/admin/src/app/features/audit/audit-logs-page.component.ts` - Read-only table pattern.

  **Acceptance Criteria**:
  - [ ] Documents page can list documents or show a valid empty/error state.
  - [ ] Document detail route/modal fetches real document detail.
  - [ ] Upload UI sends file and policy fields through `FormData`.
  - [ ] Role/department policy validation prevents invalid submit.

  **QA Scenarios**:
  ```
  Scenario: Policy-aware upload validation
    Tool: Playwright
    Preconditions: Admin user with upload permission authenticated.
    Steps:
      1. Navigate to the agentic documents page.
      2. Open upload form.
      3. Select `role` visibility without selecting allowed roles.
      4. Click submit.
    Expected Result: UI blocks submit and shows a concrete allowed roles validation message.
    Failure Indicators: Network request fires with invalid policy or no validation message appears.
    Evidence: .omo/evidence/task-7-upload-validation.md
  ```

  **Commit**: NO (group with Wave 2)

- [x] 8. Upgrade chat to conversation-aware full coverage

  **What to do**:
  - Preserve quick chat support while adding selected-conversation chat flow.
  - Use `POST /api/v1/agentic/conversations/{conversation_id}/messages` when a conversation is selected.
  - Display response metadata: status, cited chunk/document IDs, citations when present, thread/conversation ID.
  - Add `top_k` control with backend-valid range.

  **Must NOT do**:
  - Do not remove the existing basic `/chat` flow.
  - Do not hide backend errors behind generic-only messages.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: User-facing chat workflow with layout/readability requirements.
  - **Skills**: [`frontend-ui-ux`, `playwright`]
    - `frontend-ui-ux`: Conversation/chat UX.
    - `playwright`: Browser verification.
  - **Skills Evaluated but Omitted**:
    - `security-research`: Not a new auth/security design task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 9, 10)
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 1, 2, 3

  **References**:
  - `apps/admin/src/app/features/chat/chat-window.component.ts:20-63` - Current basic chat UI.
  - `apps/admin/src/app/features/chat/chat-window.component.ts:191-221` - Current quick chat send flow.
  - `app/presentation/schemas/agentic_schema.py:41-54` - Chat request/response metadata.

  **Acceptance Criteria**:
  - [ ] Existing `/chat` still sends quick chat when no conversation is selected.
  - [ ] Selected conversation sends via conversation message endpoint.
  - [ ] Response status/citations/IDs render when present.
  - [ ] `top_k` control rejects values outside backend range.

  **QA Scenarios**:
  ```
  Scenario: Chat input handles backend validation and metadata
    Tool: Playwright
    Preconditions: Admin authenticated and backend running.
    Steps:
      1. Navigate to `http://localhost:4200/chat`.
      2. Set `top_k` to `0`.
      3. Attempt to send `alo`.
      4. Assert validation blocks the invalid request.
      5. Set `top_k` to `5` and send `alo`.
    Expected Result: Invalid top_k is blocked; valid submit shows user message plus either assistant response or explicit backend error state.
    Failure Indicators: Invalid request sent, no error state, or page crash.
    Evidence: .omo/evidence/task-8-chat-flow.md
  ```

  **Commit**: NO (group with Wave 2)

- [x] 9. Readability audit and page-specific contrast cleanup

  **What to do**:
  - Audit in-scope admin pages for text/background contrast failures.
  - Replace duplicated hardcoded text colors with shared semantic classes/tokens.
  - Apply light layout adjustments only where readability requires them (e.g. card/header/table spacing or grouping).

  **Must NOT do**:
  - Do not change page information architecture during contrast cleanup.
  - Do not redesign unrelated visual branding.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Broad but bounded UI quality pass.
  - **Skills**: [`frontend-ui-ux`, `playwright`]
    - `frontend-ui-ux`: Contrast/readability decisions.
    - `playwright`: Real browser validation.
  - **Skills Evaluated but Omitted**:
    - `visual-qa`: Optional later, not required for baseline execution.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 10)
  - **Blocks**: Tasks 12, 14
  - **Blocked By**: Task 4

  **References**:
  - `apps/admin/src/app/shared/admin-page-styles.ts:1-70` - Shared reusable style utility.
  - `apps/admin/src/app/features/users/users-page.component.ts` - Repeated page style patterns.
  - `apps/admin/src/app/features/rbac/roles-page.component.ts` - Mixed light/dark surface text patterns.
  - `apps/admin/src/app/features/audit/audit-logs-page.component.ts` - Read-only table text patterns.

  **Acceptance Criteria**:
  - [ ] In-scope pages use shared contrast-safe text classes/tokens instead of repeated raw colors where practical.
  - [ ] Major text-on-background readability defects are eliminated on audited pages.
  - [ ] `npm run build` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Text remains readable on audited pages
    Tool: Playwright
    Preconditions: Admin dev server running.
    Steps:
      1. Open representative pages: `/users`, `/rbac/roles`, `/audit-logs`, `/chat`.
      2. Capture snapshots.
      3. Confirm visible headings, subtitles, body text, and muted text remain legible against their backgrounds.
    Expected Result: No obviously blended text on the tested surfaces.
    Failure Indicators: Text visually merges with card/table/background surfaces or disappears on hover/active states.
    Evidence: .omo/evidence/task-9-contrast-snapshots.md
  ```

  **Commit**: NO (group with Wave 2)

- [x] 10. Sidebar regrouping and breadcrumb/nav consistency

  **What to do**:
  - Implement grouped nav rendering instead of a single flat list.
  - Preserve existing route destinations while reflecting agreed groupings.
  - Ensure breadcrumbs and page titles remain coherent after grouping changes.

  **Must NOT do**:
  - Do not break direct URLs.
  - Do not surface Advanced/Admin tools as primary business navigation.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Navigation affects whole admin shell.
  - **Skills**: [`frontend-ui-ux`, `playwright`]
    - `frontend-ui-ux`: Grouping and hierarchy.
    - `playwright`: Verify navigation behavior.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No cross-repo refactor needed.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: Tasks 13, 14
  - **Blocked By**: Tasks 3, 5

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:220-236` - Existing breadcrumb/title metadata.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts:28-33` - Current flat nav renderer.

  **Acceptance Criteria**:
  - [ ] Nav items render in groups consistent with agreed categories.
  - [ ] `menu_sync` and `i18n_sync` appear under Advanced/Admin tools, not mixed with daily workflows.
  - [ ] Existing direct routes remain accessible.

  **QA Scenarios**:
  ```
  Scenario: Grouped nav preserves route access
    Tool: Playwright
    Preconditions: Admin authenticated.
    Steps:
      1. Open the sidebar and inspect grouped sections.
      2. Click `Chat`, `Users`, and one Advanced/Admin tools entry.
      3. Confirm page titles and breadcrumbs update correctly.
    Expected Result: Grouped nav works and routes still resolve.
    Failure Indicators: Missing entries, broken links, mismatched breadcrumbs, or inaccessible advanced tools.
    Evidence: .omo/evidence/task-10-grouped-nav.md
  ```

  **Commit**: NO (group with Wave 2)

- [x] 11. Agentic integration polish: permission, loading, empty, and error states

  **What to do**:
  - Add coherent loading, empty, not-found, unauthorized, and API-error states across all new agentic screens.
  - Ensure upload/chat/document/conversation actions respect existing auth and permission behavior.
  - Normalize error presentation so backend failures surface explicitly without crashing the shell.

  **Must NOT do**:
  - Do not swallow backend errors silently.
  - Do not expose actions a user cannot complete.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-screen integration hardening.
  - **Skills**: [`gitnexus-exploring`, `playwright`]
    - `gitnexus-exploring`: Confirm guards/error mapping patterns.
    - `playwright`: Verify real error states.
  - **Skills Evaluated but Omitted**:
    - `security-research`: No new auth model required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 6, 7, 8

  **References**:
  - `apps/admin/src/app/shared/http-error-mapper.ts` - Existing frontend error mapping pattern.
  - `apps/admin/src/app/core/interceptors/auth.interceptor.ts` - Auth header handling.
  - `apps/admin/src/app/features/system/unauthorized-page.component.ts` - Unauthorized state pattern.

  **Acceptance Criteria**:
  - [ ] All new agentic screens expose loading, empty, error, and permission-denied states.
  - [ ] Auth/permission failures do not crash the admin shell.
  - [ ] Browser QA confirms explicit user-visible failure states.

  **QA Scenarios**:
  ```
  Scenario: Backend error state is user-visible
    Tool: Playwright
    Preconditions: Admin dev server running; backend temporarily unavailable or failing for an agentic request.
    Steps:
      1. Open an agentic page.
      2. Trigger a request to the backend.
      3. Observe the UI.
    Expected Result: The page shows an explicit error state/toast/message without a blank screen or shell crash.
    Failure Indicators: Unhandled console exception, blank panel, or frozen UI.
    Evidence: .omo/evidence/task-11-error-state.md
  ```

  **Commit**: NO (group with Wave 3)

- [x] 12. Cross-page contrast regression cleanup and shared utility adoption

  **What to do**:
  - Apply the shared contrast/page style foundation to duplicated pages still using one-off text colors.
  - Standardize action colors and muted text usage across audited pages.
  - Remove avoidable duplicated page header/card style definitions where shared utilities suffice.

  **Must NOT do**:
  - Do not refactor untouched pages unnecessarily.
  - Do not introduce a second styling convention.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multi-page consistency cleanup.
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Consistency and readability decisions.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Better used in the dedicated regression task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 11, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 4, 9

  **References**:
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared style utility.
  - `apps/admin/src/app/features/users/users-page.component.ts` - Repeated action/text colors.
  - `apps/admin/src/app/features/rbac/permissions-page.component.ts` - Mixed modal/page color handling.

  **Acceptance Criteria**:
  - [ ] Shared utility adoption reduces repeated hardcoded text styles on in-scope pages.
  - [ ] Action/muted text styles are consistent across audited pages.
  - [ ] `npm run build` exits 0.

  **QA Scenarios**:
  ```
  Scenario: Shared styles replace duplicate patterns
    Tool: Bash
    Preconditions: Contrast tasks completed.
    Steps:
      1. Search in-scope pages for repeated raw text colors used before refactor.
      2. Compare counts before/after if tracked in notes.
      3. Run `cd apps/admin && npm run build`.
    Expected Result: Duplicated hardcoded contrast styles are reduced and build passes.
    Failure Indicators: Build breaks or shared utility is bypassed by new one-off colors.
    Evidence: .omo/evidence/task-12-style-dedup.txt
  ```

  **Commit**: NO (group with Wave 3)

- [x] 13. Advanced/Admin tools placement refinement for menu and i18n sync

  **What to do**:
  - Refine labels, order, and placement of `menu_sync` and `i18n_sync` within Advanced/Admin tools.
  - Ensure these tools are visually deprioritized but still discoverable for eligible admins.
  - Preserve their existing pages and sync behavior.

  **Must NOT do**:
  - Do not remove the routes.
  - Do not merge these tools into unrelated business pages.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small focused navigation placement refinement.
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Needed for discoverability vs deprioritization balance.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-exploring`: Research already established tool purpose.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 11, 12)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 5, 10

  **References**:
  - `apps/admin/src/app/features/config/menu-sync-page.component.ts` - Existing page wrapper.
  - `apps/admin/src/app/features/config/i18n-sync-page.component.ts` - Existing page wrapper.
  - `docs/admin-sync-operations.md` - Operational justification for retaining both tools.

  **Acceptance Criteria**:
  - [ ] Both sync tools remain reachable by direct route and grouped nav.
  - [ ] Their placement is visually secondary to main workflows.
  - [ ] Breadcrumbs/titles remain consistent.

  **QA Scenarios**:
  ```
  Scenario: Advanced tools stay discoverable
    Tool: Playwright
    Preconditions: Admin authenticated with `system.config.manage`.
    Steps:
      1. Open sidebar.
      2. Locate the Advanced/Admin tools group.
      3. Navigate to `menu_sync` and `i18n_sync` from the grouped nav.
    Expected Result: Tools are still easy to find for admins but not promoted as primary workflow items.
    Failure Indicators: Tools missing, mislabeled, or mixed into unrelated groups.
    Evidence: .omo/evidence/task-13-advanced-tools.md
  ```

  **Commit**: NO (group with Wave 3)

- [x] 14. Build, browser QA, and route regression sweep

  **What to do**:
  - Run final build and targeted regression checks for all touched routes.
  - Verify direct URL access for agentic routes, existing business routes, and Advanced/Admin tools.
  - Capture browser evidence for key pages after contrast and nav changes.

  **Must NOT do**:
  - Do not mark work complete without browser verification.
  - Do not skip direct-route regression checks.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Final cross-cutting verification sweep.
  - **Skills**: [`playwright`]
    - `playwright`: Required for user-facing route and visual verification.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: This task verifies rather than redesigns.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 final gate
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 9, 10, 11, 12, 13

  **References**:
  - `apps/admin/src/app/app.routes.ts` - Route inventory.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Nav/breadcrumb inventory.

  **Acceptance Criteria**:
  - [ ] `npm run build` exits 0.
  - [ ] Core routes (`/chat`, agentic pages, `/users`, `/rbac/roles`, `/audit-logs`, `/config/menu-sync`, `/config/i18n-sync`) resolve as expected for an eligible admin.
  - [ ] Browser snapshots show readable text and correct nav grouping.

  **QA Scenarios**:
  ```
  Scenario: Direct-route regression sweep
    Tool: Playwright
    Preconditions: Admin authenticated and dev server running.
    Steps:
      1. Navigate directly to `/chat`.
      2. Navigate directly to each new agentic route.
      3. Navigate to `/users`, `/rbac/roles`, `/audit-logs`, `/config/menu-sync`, and `/config/i18n-sync`.
      4. Assert no unexpected redirect to `/not-found` or `/forbidden` for valid admin routes.
    Expected Result: Touched routes still resolve and render their pages.
    Failure Indicators: 404s, route crashes, unreadable text, or broken nav state.
    Evidence: .omo/evidence/task-14-route-regression.md
  ```

  **Commit**: YES
  - Message: `feat(admin): complete agentic coverage and redesign admin readability`
  - Files: all touched admin frontend files from Waves 1-3
  - Pre-commit: `cd apps/admin && npm run build`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end and verify each Must Have / Must Not Have / task dependency / wave boundary is internally consistent and evidenced by the research. Confirm the plan stays within scope: agentic frontend full coverage, contrast standardization, navigation regrouping.

  **Recommended Agent Profile**:
  - **Category**: `oracle`
    - Reason: Read-only compliance audit against the full plan and implementation evidence.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F2, F3, F4)
  - **Blocks**: Final user approval
  - **Blocked By**: Task 14

  **Acceptance Criteria**:
  - [ ] Every Must Have item has at least one matching implementation task.
  - [ ] No Must Not Have item is contradicted by a task description.
  - [ ] Wave dependencies are internally consistent.
  - [ ] Output format includes counts and an explicit APPROVE/REJECT verdict.

  Output: `Must Have [N/N] | Must Not Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Review the final implementation for build/typecheck success, lint issues, obvious anti-patterns, and any hardcoded color or nav regressions that violate the plan. Check for `as any`, `@ts-ignore`, empty catches, and duplicate style patterns.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Broad cross-file quality review with build/lint/test validation.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F3, F4)
  - **Blocks**: Final user approval
  - **Blocked By**: Task 14

  **Acceptance Criteria**:
  - [ ] Build/typecheck passes.
  - [ ] Lint passes or any failures are explicitly justified.
  - [ ] No obvious anti-patterns or unapproved regressions remain in touched files.

  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Browser QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Verify new agentic screens, contrast updates, and navigation grouping in the browser. Confirm `/chat`, conversation/document views, and advanced tools placement. Capture evidence and test key error states.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Hands-on browser verification across multiple user-facing routes.
  - **Skills**: [`playwright`]
    - `playwright`: Required for browser execution, screenshots, and interaction checks.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F4)
  - **Blocks**: Final user approval
  - **Blocked By**: Task 14

  **Acceptance Criteria**:
  - [ ] Each in-scope route can be opened in the browser.
  - [ ] Key happy-path and failure states are observed and recorded.
  - [ ] Browser evidence is saved for representative pages.

  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  Compare the final diff against the plan line by line. Verify no missing deliverables, no accidental removal of `menu_sync` / `i18n_sync`, no route renames, and no unintended layout/theme expansion beyond contrast-first cleanup.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Compare final diff against plan scope and task-by-task intent.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F3)
  - **Blocks**: Final user approval
  - **Blocked By**: Task 14

  **Acceptance Criteria**:
  - [ ] Each implementation task maps 1:1 to the final diff.
  - [ ] No forbidden scope creep is present.
  - [ ] Menu sync and i18n sync remain available under the agreed grouping.

  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1-14**: commit in logical groups by wave when implementation begins
- **Final**: review-only, no code changes expected

---

## Success Criteria

### Verification Commands
```bash
npm run build  # Expected: frontend build passes
npm run test   # Expected: targeted tests pass
```

### Final Checklist
- [ ] All agentic backend endpoints have clear frontend coverage status
- [ ] All full-coverage agentic UI deliverables are present
- [ ] Contrast tokens/shared styles remove major text readability issues
- [ ] Nav groups reflect business vs operations vs security vs advanced tools
- [ ] `menu_sync` and `i18n_sync` remain available but deprioritized
- [ ] Build and browser QA pass
