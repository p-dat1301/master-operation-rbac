# Agentic Integration - RAG Chat & Document Management

## TL;DR

> **Quick Summary**: Integrate agentic backend API (RAG/chat system) into admin frontend, enabling users to chat with AI assistant and admins to manage knowledge base documents.
>
> **Deliverables**:
> - User-facing chat interface at `/chat` with conversation history and citations
> - Admin document management at `/agentic-documents` for uploading/managing RAG knowledge base
> - TypeScript service layer, models, lazy-loaded routes
> - Unit tests and E2E tests
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Models → Service → Chat UI → Tests

---

## Context

### Original Request
User added agentic backend API endpoints for RAG (Retrieval-Augmented Generation) chat system and wants to integrate them into admin frontend.

### Interview Summary
**Key Discussions**:
- Explored agentic API: 3 endpoint groups (conversations, chat, documents)
- Proposed scope: Priority 1 (user chat interface) + Priority 2 (admin document management)
- Clarified 5 features: message history persistent (IN), conversation monitoring/analytics/batch upload/preview (OUT Phase 2)
- User confirmed: "thực hiện với score đề xuất"

**API Groups Identified**:
1. **Conversations**: Create, list, get detail, get messages
2. **Chat**: Quick chat (auto-conversation), chat in specific conversation with citations
3. **Documents**: Upload (admin/manager only), list, get detail

**Research Findings**:
- Backend API ready: `/api/v1/agentic/*` endpoints functional
- Permissions: document upload restricted to admin/manager (backend enforces)
- Message history: stored on backend (persistent across sessions)
- Citations: responses include cited_chunk_ids, cited_document_ids, citations array
- No Metis/Oracle consultation (platform codex issue - self-verified)

### Metis Review
**Skipped** due to platform issue. Self-verified interview completeness: core objective clear, scope explicit, test strategy decided, no outstanding questions.

---

## Work Objectives

### Core Objective
Integrate agentic backend API into admin frontend, providing user-facing chat interface for document Q&A and admin tools for knowledge base management.

### Concrete Deliverables
- `/chat` route with chat interface (lazy-loaded)
- `/agentic-documents` route with document management (lazy-loaded)
- `AgenticService` extending `BaseApiService`
- TypeScript models matching backend schemas
- Unit tests: service, key components
- E2E tests: chat flow, document upload

### Definition of Done
- [ ] User can chat with AI assistant at `/chat`
- [ ] User can see conversation history and citations
- [ ] Admin/manager can upload documents at `/agentic-documents`
- [ ] Admin can view document list with status
- [ ] All unit tests pass (`npm run test:unit`)
- [ ] All E2E tests pass (`npm run e2e`)
- [ ] Build passes with no errors (`npm run build`)

### Must Have
- User chat interface with persistent message history
- Conversation list sidebar
- Citations display (show sources for answers)
- Document upload form (admin/manager only)
- Document list with status
- Service layer following `BaseApiService` pattern
- Lazy-loaded routes
- Error handling via `mapAdminHttpError`
- Loading states via `runAdminAsync`

### Must NOT Have (Guardrails)
- **No conversation monitoring** - Admin cannot view other users' conversations (privacy, Phase 2)
- **No document analytics** - No citation counts, usage stats, popular docs (Phase 2)
- **No multi-file batch upload** - Single file only (Phase 2 enhancement)
- **No document content preview** - No inline PDF/DOCX viewer (Phase 2)
- **No fake UI** - Every feature maps to real backend endpoint
- **No backend changes** - Frontend-only work
- **No premature abstraction** - Keep components simple, extract only when needed
- **No excessive comments** - Code should be self-documenting
- **No console.log in source** - Use proper error handling

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES (from frontend-improvement plan)
- **Automated tests**: Tests-after (not TDD)
- **Framework**: Jest + Playwright
- **Pattern**: Follow frontend-improvement test structure

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright - Navigate, interact, assert DOM, screenshot
- **API Service**: Use Bash (curl) - Call endpoints, assert responses
- **Component Tests**: Use Bash (npm test) - Run Jest, assert pass

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.
> Target: 5-8 tasks per wave. Fewer than 3 per wave (except final) = under-splitting.

```
Wave 1 (Foundation - start immediately):
├── Task 1: TypeScript models [quick]
├── Task 2: AgenticService [quick]
└── Task 3: Route setup [quick]

Wave 2 (Chat UI - max parallel):
├── Task 4: Chat page shell [visual-engineering]
├── Task 5: Conversation list sidebar [visual-engineering]
├── Task 6: Chat window component [visual-engineering]
└── Task 7: Citation display component [visual-engineering]

Wave 3 (Document Management):
├── Task 8: Document page [visual-engineering]
├── Task 9: Upload form [visual-engineering]
└── Task 10: Document list [visual-engineering]

Wave 4 (Quality):
├── Task 11: Unit tests [quick]
└── Task 12: E2E tests [unspecified-high]

Wave FINAL (After ALL tasks - 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 2 → Task 4 → Task 11 → F1-F4 → user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 4 (Wave 2)
```

### Dependency Matrix

- **1-3**: - - 4-10, 1
- **4**: 1, 2, 3 - 11, 12, 2
- **5**: 1, 2, 3 - 11, 12, 2
- **6**: 1, 2, 3 - 11, 12, 2
- **7**: 1, 2, 3 - 11, 12, 2
- **8**: 1, 2, 3 - 11, 12, 3
- **9**: 1, 2, 3 - 11, 12, 3
- **10**: 1, 2, 3 - 11, 12, 3
- **11**: 4-10 - F1-F4, 4
- **12**: 4-10 - F1-F4, 4

### Agent Dispatch Summary

- **Wave 1**: **3 tasks** - T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **4 tasks** - T4-T7 → `visual-engineering`
- **Wave 3**: **3 tasks** - T8-T10 → `visual-engineering`
- **Wave 4**: **2 tasks** - T11 → `quick`, T12 → `unspecified-high`
- **FINAL**: **4 tasks** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**
> **FORMAT**: Task labels MUST use bare numbers: `1.`, `2.`, `3.` — NOT `T1.`, `Task 1.`, `Phase 1:`.
> The /start-work progress counter requires exact format. Deviation = progress shows 0/0.
> Final Verification Wave labels MUST use `F1.`, `F2.`, etc. — NOT `T-F1.`, `F-1.`, `Final 1.`.

### Wave 1: Foundation (Start Immediately)

- [ ] 1. TypeScript Models for Agentic API

  **What to do**:
  - Create `apps/admin/src/app/models/agentic.models.ts`
  - Define interfaces matching backend schemas:
    - `AgenticConversation`: conversation_id, thread_id, user_id, status, title
    - `AgenticMessage`: turn_id, conversation_id, turn_index, user_message, assistant_message, assistant_status, langfuse_trace_id
    - `AgenticChatRequest`: message, top_k (default 5)
    - `AgenticChatResponse`: conversation_id, thread_id, answer, status, cited_chunk_ids, cited_document_ids, citations
    - `AgenticDocument`: document_id, status, filename, mime_type
  - Use TypeScript strict types (no `any`)

  **Must NOT do**:
  - Add fields not in backend schema (no premature extensions)
  - Use `any` type or cast workarounds

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple TypeScript interface definitions, straightforward mapping from backend schemas
  - **Skills**: None
  - **Skills Evaluated but Omitted**: None needed for interface definitions

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4-10 (all components need models)
  - **Blocked By**: None (can start immediately)

  **References**:
  - `app/presentation/schemas/agentic_schema.py:7-74` - Backend schema definitions (source of truth)
  - `apps/admin/src/app/models/user.models.ts` - Existing model pattern to follow
  - `apps/admin/src/app/models/task.models.ts` - Another example of model structure

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/models/agentic.models.ts`
  - [ ] All 5 interfaces defined with correct fields
  - [ ] TypeScript compiles: `npm run build` → no errors in agentic.models.ts
  - [ ] No `any` types: `grep -r "any" apps/admin/src/app/models/agentic.models.ts` → no matches

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: TypeScript compilation validates model definitions
    Tool: Bash (npm)
    Preconditions: agentic.models.ts created with all interfaces
    Steps:
      1. Run: cd apps/admin && npm run build
      2. Check output for errors related to agentic.models.ts
      3. Assert: exit code 0, no compilation errors
    Expected Result: Build succeeds, agentic.models.ts compiles cleanly
    Failure Indicators: Compilation errors, missing fields, type mismatches
    Evidence: .omo/evidence/task-1-model-compile.txt

  Scenario: No 'any' types used (strict typing check)
    Tool: Bash (grep)
    Preconditions: agentic.models.ts created
    Steps:
      1. Run: grep -n "any" apps/admin/src/app/models/agentic.models.ts
      2. Assert: no matches found (exit code 1 from grep = no matches)
    Expected Result: grep returns no results, confirming strict typing
    Failure Indicators: grep finds "any" keyword
    Evidence: .omo/evidence/task-1-no-any-check.txt
  ```

  **Commit**: YES
  - Message: `feat(agentic): add TypeScript models for agentic API`
  - Files: `apps/admin/src/app/models/agentic.models.ts`
  - Pre-commit: `npm run build`

- [ ] 2. AgenticService API Layer

  **What to do**:
  - Create `apps/admin/src/app/services/agentic-api.service.ts`
  - Extend `BaseApiService` (follow pattern from UsersService/TasksService)
  - Implement methods:
    - `getConversations(): Observable<AgenticConversation[]>` → GET `/api/v1/agentic/conversations`
    - `createConversation(title?: string): Observable<AgenticConversation>` → POST `/api/v1/agentic/conversations`
    - `getConversationMessages(conversationId: string): Observable<AgenticMessage[]>` → GET `/api/v1/agentic/conversations/{id}/messages`
    - `quickChat(message: string, topK?: number): Observable<AgenticChatResponse>` → POST `/api/v1/agentic/chat`
    - `chatInConversation(conversationId: string, message: string, topK?: number): Observable<AgenticChatResponse>` → POST `/api/v1/agentic/conversations/{id}/messages`
    - `uploadDocument(file: File): Observable<AgenticDocument>` → POST `/api/v1/agentic/documents`
    - `getDocuments(): Observable<AgenticDocument[]>` → GET `/api/v1/agentic/documents`
  - Use `buildUrl()` for all endpoints (no hard-coded URLs)
  - Return typed Observables using models from task 1
  - Error handling via interceptor (don't catch locally)

  **Must NOT do**:
  - Hard-code API URLs (use buildUrl)
  - Add cast workarounds
  - Catch errors locally (let interceptor handle)
  - Add methods for OUT-of-scope features (monitoring, analytics)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Following established service pattern, straightforward HTTP calls
  - **Skills**: None
  - **Skills Evaluated but Omitted**: None needed for service layer

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 4-10 (all components need service)
  - **Blocked By**: Task 1 (needs models for return types)

  **References**:
  - `apps/admin/src/app/services/users.service.ts:1-50` - Service pattern to follow (BaseApiService extension)
  - `apps/admin/src/app/services/base-api.service.ts` - Parent class with buildUrl()
  - `app/presentation/api/v1/agentic/router.py:73-245` - Backend endpoints (API contracts)
  - `apps/admin/src/app/models/agentic.models.ts` - Models for typing (from task 1)

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/services/agentic-api.service.ts`
  - [ ] Service extends BaseApiService
  - [ ] All 7 methods implemented with correct signatures
  - [ ] TypeScript compiles: `npm run build` → no errors
  - [ ] No hard-coded URLs: `grep -r "http://\|https://" apps/admin/src/app/services/agentic-api.service.ts` → no matches

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Service methods return typed Observables
    Tool: Bash (npm test)
    Preconditions: agentic-api.service.ts created with all methods
    Steps:
      1. Create unit test: agentic.service.spec.ts
      2. Mock HttpClient, test each method returns Observable with correct type
      3. Run: npm run test:unit -- agentic.service.spec.ts
      4. Assert: all tests pass
    Expected Result: All 7 service methods return correctly typed Observables
    Failure Indicators: Type errors, compilation failures, test failures
    Evidence: .omo/evidence/task-2-service-test.txt

  Scenario: No hard-coded URLs (buildUrl compliance check)
    Tool: Bash (grep)
    Preconditions: agentic-api.service.ts created
    Steps:
      1. Run: grep -En "http://|https://" apps/admin/src/app/services/agentic-api.service.ts
      2. Assert: no matches found (exit code 1 = no matches)
    Expected Result: grep returns no results, all URLs use buildUrl()
    Failure Indicators: grep finds hard-coded URLs
    Evidence: .omo/evidence/task-2-no-hardcoded-urls.txt
  ```

  **Commit**: YES
  - Message: `feat(agentic): add AgenticService API layer`
  - Files: `apps/admin/src/app/services/agentic-api.service.ts`
  - Pre-commit: `npm run build`

- [ ] 3. Lazy-Loaded Routes Setup

  **What to do**:
  - Edit `apps/admin/src/app/app.routes.ts`
  - Add two new lazy-loaded routes:
    - `/chat` → `loadComponent: () => import('./features/chat/chat-page.component').then(m => m.ChatPageComponent)`
    - `/agentic-documents` → `loadComponent: () => import('./features/agentic-documents/documents-page.component').then(m => m.DocumentsPageComponent)`
  - Add AuthGuard to both routes (canActivate: [authGuard])
  - Update navigation menu in `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`:
    - Add "Chat" link to `/chat` (icon: chat_bubble or forum)
    - Add "Documents" link to `/agentic-documents` (icon: description or folder, admin/manager only via *ngIf role check)

  **Must NOT do**:
  - Eager load routes (must use lazy loadComponent)
  - Skip AuthGuard (security requirement)
  - Add routes for OUT-of-scope features (monitoring, analytics)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple route configuration, following existing pattern
  - **Skills**: None
  - **Skills Evaluated but Omitted**: None needed for route setup

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Tasks 4-10 (routes must exist for components to be accessible)
  - **Blocked By**: None (route definitions don't depend on components existing yet)

  **References**:
  - `apps/admin/src/app/app.routes.ts:10-50` - Existing lazy-loaded routes pattern
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:30-60` - Navigation menu structure
  - `apps/admin/src/app/core/guards/auth.guard.ts` - AuthGuard to apply

  **Acceptance Criteria**:
  - [ ] Routes added to app.routes.ts: `/chat`, `/agentic-documents`
  - [ ] Both routes use lazy loadComponent (not eager)
  - [ ] Both routes have authGuard
  - [ ] Navigation links added to admin shell
  - [ ] Documents link has role check (*ngIf for admin/manager)
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Routes are lazy-loaded (not eager)
    Tool: Bash (grep)
    Preconditions: Routes added to app.routes.ts
    Steps:
      1. Run: grep -A2 "path: 'chat'" apps/admin/src/app/app.routes.ts
      2. Assert: output contains "loadComponent" keyword
      3. Run: grep -A2 "path: 'agentic-documents'" apps/admin/src/app/app.routes.ts
      4. Assert: output contains "loadComponent" keyword
    Expected Result: Both routes use loadComponent (lazy loading)
    Failure Indicators: Routes use "component:" instead of "loadComponent:"
    Evidence: .omo/evidence/task-3-lazy-routes.txt

  Scenario: AuthGuard applied to both routes
    Tool: Bash (grep)
    Preconditions: Routes added with authGuard
    Steps:
      1. Run: grep -B2 -A4 "path: 'chat'" apps/admin/src/app/app.routes.ts | grep authGuard
      2. Assert: exit code 0 (match found)
      3. Run: grep -B2 -A4 "path: 'agentic-documents'" apps/admin/src/app/app.routes.ts | grep authGuard
      4. Assert: exit code 0 (match found)
    Expected Result: Both routes have canActivate: [authGuard]
    Failure Indicators: grep returns no match
    Evidence: .omo/evidence/task-3-auth-guard.txt
  ```

  **Commit**: YES
  - Message: `feat(agentic): add lazy-loaded routes for chat and documents`
  - Files: `apps/admin/src/app/app.routes.ts`, `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`
  - Pre-commit: `npm run build`

### Wave 2: Chat UI (After Wave 1 - Max Parallel)

- [ ] 4. Chat Page Shell Component

  **What to do**:
  - Create `apps/admin/src/app/features/chat/chat-page.component.ts`
  - Create `apps/admin/src/app/features/chat/chat-page.component.html`
  - Layout structure: two-column (sidebar + main)
    - Left sidebar (30%): placeholder for conversation list (task 5)
    - Right main (70%): placeholder for chat window (task 6)
  - Use `ADMIN_PAGE_COMMON_STYLES` from shared/admin-page-styles.ts
  - Inject `AgenticService` from task 2
  - Create signal state:
    - `conversations = signal<AgenticConversation[]>([])` - conversation list
    - `selectedConversationId = signal<string | null>(null)` - active conversation
    - `loadingState = signal<'idle' | 'loading' | 'error'>('idle')`
  - Load conversations on init: `runAdminAsync(this.agenticService.getConversations(), ...)`
  - Provide selectConversation(id: string) method to update selectedConversationId

  **Must NOT do**:
  - Implement conversation list UI (that's task 5)
  - Implement chat window UI (that's task 6)
  - Add business logic beyond state management
  - Excessive comments or abstractions

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI layout, component structure, styling
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (basic layout, not complex design)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7)
  - **Blocks**: Task 11, 12 (tests need component to exist)
  - **Blocked By**: Tasks 1, 2, 3 (needs models, service, route)

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts:1-80` - Page shell pattern to follow
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared styles to reuse
  - `apps/admin/src/app/shared/async-state.ts:runAdminAsync` - Loading state helper
  - `apps/admin/src/app/services/agentic-api.service.ts` - Service to inject (from task 2)
  - `apps/admin/src/app/models/agentic.models.ts` - Models for typing (from task 1)

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-page.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-page.component.html`
  - [ ] Component uses ADMIN_PAGE_COMMON_STYLES
  - [ ] Signal state defined: conversations, selectedConversationId, loadingState
  - [ ] Conversations loaded on init via runAdminAsync
  - [ ] TypeScript compiles: `npm run build` → no errors
  - [ ] Route `/chat` renders component: can navigate without 404

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Chat page loads conversations on init
    Tool: Playwright (browser test via playwright skill)
    Preconditions: Backend running, at least 1 conversation exists for test user
    Steps:
      1. Navigate to http://localhost:4200/chat
      2. Wait for page load (waitForSelector: '.chat-page')
      3. Check network requests: assert GET /api/v1/agentic/conversations called
      4. Assert: no error state displayed
    Expected Result: Page renders, conversations API called, no errors
    Failure Indicators: 404 error, network request not sent, error state shown
    Evidence: .omo/evidence/task-4-page-load.png (screenshot)

  Scenario: Component compiles and route is accessible
    Tool: Bash (build + curl)
    Preconditions: Component created, route configured
    Steps:
      1. Run: cd apps/admin && npm run build
      2. Assert: exit code 0, no compilation errors
      3. Start dev server: npm start (background)
      4. Wait 10s for server ready
      5. Run: curl -I http://localhost:4200/chat
      6. Assert: HTTP 200 response (route exists)
    Expected Result: Build succeeds, route accessible
    Failure Indicators: Build errors, 404 on /chat
    Evidence: .omo/evidence/task-4-route-check.txt
  ```

  **Commit**: NO (group with task 5-7)

- [ ] 5. Conversation List Sidebar Component

  **What to do**:
  - Create `apps/admin/src/app/features/chat/conversation-list.component.ts`
  - Create `apps/admin/src/app/features/chat/conversation-list.component.html`
  - Input: `@Input() conversations: AgenticConversation[]`
  - Input: `@Input() selectedId: string | null`
  - Output: `@Output() selectConversation = new EventEmitter<string>()`
  - Display list of conversations:
    - Show title (or "Untitled Chat" if title is null)
    - Show status badge (active/archived)
    - Highlight selected conversation
    - Show "New Chat" button at top → emits selectConversation with empty string
  - Styling: vertical list, hover effects, selected state
  - Empty state: "No conversations yet. Start a new chat!"

  **Must NOT do**:
  - Fetch conversations directly (parent provides via @Input)
  - Implement chat logic (just presentation)
  - Over-style (keep simple and functional)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component, list rendering, styling
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (straightforward list, not complex)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 6, 7)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models)

  **References**:
  - `apps/admin/src/app/features/chat/chat-page.component.ts` - Parent component (from task 4)
  - `apps/admin/src/app/models/agentic.models.ts:AgenticConversation` - Data model
  - Angular Material or CSS for list styling

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/chat/conversation-list.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/conversation-list.component.html`
  - [ ] Component has @Input conversations, selectedId
  - [ ] Component has @Output selectConversation
  - [ ] "New Chat" button present
  - [ ] Empty state handled
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Conversation list displays conversations
    Tool: Playwright
    Preconditions: Test user has 3 conversations
    Steps:
      1. Navigate to /chat
      2. Wait for sidebar to render (waitForSelector: '.conversation-list')
      3. Count conversation items: querySelectorAll('.conversation-item')
      4. Assert: count === 3
      5. Assert: "New Chat" button visible
    Expected Result: 3 conversations displayed, New Chat button present
    Failure Indicators: Wrong count, button missing, empty state shown incorrectly
    Evidence: .omo/evidence/task-5-conversation-list.png

  Scenario: Selecting conversation emits event
    Tool: Playwright
    Preconditions: Multiple conversations exist
    Steps:
      1. Navigate to /chat
      2. Click first conversation item
      3. Check if conversation is highlighted (has selected class)
      4. Assert: selected styling applied
    Expected Result: Conversation selectable, visual feedback on selection
    Failure Indicators: Click does nothing, no highlight
    Evidence: .omo/evidence/task-5-select-conversation.png
  ```

  **Commit**: NO (group with tasks 4, 6, 7)

- [ ] 6. Chat Window Component

  **What to do**:
  - Create `apps/admin/src/app/features/chat/chat-window.component.ts`
  - Create `apps/admin/src/app/features/chat/chat-window.component.html`
  - Input: `@Input() conversationId: string | null`
  - Inject `AgenticService`
  - Signal state:
    - `messages = signal<AgenticMessage[]>([])` - message history
    - `userInput = signal<string>('')` - current message being typed
    - `sendingMessage = signal<boolean>(false)` - sending state
    - `latestCitations = signal<any[]>([])` - citations from last response
  - Load messages when conversationId changes: `effect(() => { if (conversationId) load messages })`
  - Message list: display user_message and assistant_message in chat bubble style
  - Input box at bottom: textarea + "Send" button
  - Send message flow:
    - Call `agenticService.chatInConversation(conversationId, message)`
    - On response: append new message to messages array, show citations (task 7)
    - Handle loading state via runAdminAsync
  - Auto-scroll to bottom when new message arrives

  **Must NOT do**:
  - Implement citations display (that's task 7 - just store in latestCitations)
  - Add markdown rendering (keep text plain for Phase 1)
  - Over-engineer message formatting
  - Add features like message editing/deletion (out of scope)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Chat UI, message bubbles, input handling, scrolling behavior
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (standard chat interface)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5, 7)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models, service)

  **References**:
  - `apps/admin/src/app/features/chat/chat-page.component.ts` - Parent component (from task 4)
  - `apps/admin/src/app/services/agentic-api.service.ts:chatInConversation` - Service method to call
  - `apps/admin/src/app/models/agentic.models.ts:AgenticMessage` - Message model
  - `apps/admin/src/app/shared/async-state.ts:runAdminAsync` - Loading helper

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-window.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-window.component.html`
  - [ ] Component has @Input conversationId
  - [ ] Messages loaded when conversationId changes
  - [ ] Send message functionality works (calls agenticService.chatInConversation)
  - [ ] Message list displays user/assistant messages
  - [ ] Auto-scroll to bottom on new message
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Chat window loads message history
    Tool: Playwright
    Preconditions: Test conversation exists with 2 messages
    Steps:
      1. Navigate to /chat
      2. Select conversation (click conversation item)
      3. Wait for messages to load (waitForSelector: '.message-item')
      4. Count messages: querySelectorAll('.message-item').length
      5. Assert: count === 2 (user + assistant messages)
    Expected Result: Message history displayed correctly
    Failure Indicators: No messages shown, API not called, loading forever
    Evidence: .omo/evidence/task-6-message-history.png

  Scenario: Send message and receive response
    Tool: Playwright
    Preconditions: In active conversation
    Steps:
      1. Type message in input: "What is the leave policy?"
      2. Click "Send" button
      3. Wait for loading state to clear (button re-enabled)
      4. Wait for assistant response to appear (new message bubble)
      5. Assert: new message contains assistant response text
      6. Assert: POST /api/v1/agentic/conversations/{id}/messages called
    Expected Result: Message sent, response received and displayed
    Failure Indicators: Message not sent, no response, error shown
    Evidence: .omo/evidence/task-6-send-message.png
  ```

  **Commit**: NO (group with tasks 4, 5, 7)

- [ ] 7. Citation Display Component

  **What to do**:
  - Create `apps/admin/src/app/features/chat/citation-display.component.ts`
  - Create `apps/admin/src/app/features/chat/citation-display.component.html`
  - Input: `@Input() citations: any[]` - citation objects from AgenticChatResponse
  - Display citations as expandable list below assistant message:
    - Show count: "3 sources cited"
    - List each citation with: document name, chunk preview (if available)
    - Collapsible/expandable (start collapsed)
  - Handle empty state: if citations.length === 0, don't render anything
  - Styling: subtle, secondary info appearance (not prominent)

  **Must NOT do**:
  - Add document preview modal (out of scope)
  - Add complex citation formatting
  - Fetch additional document info (use what's in citations array)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component, list display, expandable section
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (simple list component)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5, 6)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models)

  **References**:
  - `apps/admin/src/app/features/chat/chat-window.component.ts` - Parent component (from task 6)
  - `apps/admin/src/app/models/agentic.models.ts:AgenticChatResponse.citations` - Citation data structure
  - Angular Material expansion panel or custom collapsible

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/chat/citation-display.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/citation-display.component.html`
  - [ ] Component has @Input citations
  - [ ] Citation count displayed
  - [ ] Citation list expandable/collapsible
  - [ ] Empty state handled (no render if citations empty)
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Citations displayed after assistant response with sources
    Tool: Playwright
    Preconditions: Send message that triggers citations (e.g., "What is leave policy?")
    Steps:
      1. Send message in chat window
      2. Wait for assistant response
      3. Look for citation display component (waitForSelector: '.citation-display')
      4. Assert: "N sources cited" text visible (N > 0)
      5. Click to expand citations
      6. Assert: citation list items visible
    Expected Result: Citations shown, expandable, list items present
    Failure Indicators: Citations not shown despite response having citations
    Evidence: .omo/evidence/task-7-citations-display.png

  Scenario: No citations shown when response has no sources
    Tool: Playwright
    Preconditions: Send message with no citations in response
    Steps:
      1. Mock response with empty citations array
      2. Send message
      3. Wait for response
      4. Check DOM: querySelector('.citation-display')
      5. Assert: citation display not rendered (null)
    Expected Result: Citation component not visible when no citations
    Failure Indicators: Empty citation display shown
    Evidence: .omo/evidence/task-7-no-citations.png
  ```

  **Commit**: YES (end of Wave 2)
  - Message: `feat(agentic): add chat interface components`
  - Files: `apps/admin/src/app/features/chat/*`
  - Pre-commit: `npm run build && npm run test:unit`

### Wave 3: Document Management (After Wave 1)

- [ ] 8. Document Page Shell Component

  **What to do**:
  - Create `apps/admin/src/app/features/agentic-documents/documents-page.component.ts`
  - Create `apps/admin/src/app/features/agentic-documents/documents-page.component.html`
  - Use `ADMIN_PAGE_COMMON_STYLES` from shared/admin-page-styles.ts
  - Inject `AgenticService` from task 2
  - Signal state:
    - `documents = signal<AgenticDocument[]>([])` - document list
    - `loadingState = signal<'idle' | 'loading' | 'error'>('idle')`
    - `uploadInProgress = signal<boolean>(false)`
  - Page layout:
    - Header: "Knowledge Base Documents" + "Upload Document" button (admin/manager only via role check)
    - Main area: placeholder for document list (task 10) and upload form (task 9)
  - Load documents on init: `runAdminAsync(this.agenticService.getDocuments(), ...)`
  - Provide uploadDocument(file: File) method to trigger upload

  **Must NOT do**:
  - Implement upload form UI (that's task 9)
  - Implement document list UI (that's task 10)
  - Allow non-admin/manager to see upload button

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Page shell, layout, component structure
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (basic page layout)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 10)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models, service, route)

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts:1-80` - Page shell pattern
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared styles
  - `apps/admin/src/app/shared/async-state.ts:runAdminAsync` - Loading helper
  - `apps/admin/src/app/services/agentic-api.service.ts` - Service (from task 2)
  - `apps/admin/src/app/models/agentic.models.ts` - Models (from task 1)

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/documents-page.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/documents-page.component.html`
  - [ ] Component uses ADMIN_PAGE_COMMON_STYLES
  - [ ] Signal state defined: documents, loadingState, uploadInProgress
  - [ ] Documents loaded on init via runAdminAsync
  - [ ] Upload button visible only for admin/manager (role check)
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Document page loads documents on init
    Tool: Playwright
    Preconditions: Backend running, test user is admin, at least 1 document exists
    Steps:
      1. Navigate to http://localhost:4200/agentic-documents
      2. Wait for page load (waitForSelector: '.documents-page')
      3. Check network requests: assert GET /api/v1/agentic/documents called
      4. Assert: no error state displayed
    Expected Result: Page renders, documents API called, no errors
    Failure Indicators: 404 error, network request not sent, error state
    Evidence: .omo/evidence/task-8-page-load.png

  Scenario: Upload button visible only for admin/manager
    Tool: Playwright
    Preconditions: Two test users: one admin, one employee
    Steps:
      1. Login as admin
      2. Navigate to /agentic-documents
      3. Assert: "Upload Document" button visible
      4. Logout, login as employee
      5. Navigate to /agentic-documents
      6. Assert: "Upload Document" button NOT visible
    Expected Result: Button shown for admin, hidden for employee
    Failure Indicators: Button always shown or always hidden
    Evidence: .omo/evidence/task-8-upload-button-role.png
  ```

  **Commit**: NO (group with tasks 9, 10)

- [ ] 9. Document Upload Form Component

  **What to do**:
  - Create `apps/admin/src/app/features/agentic-documents/document-upload-form.component.ts`
  - Create `apps/admin/src/app/features/agentic-documents/document-upload-form.component.html`
  - Output: `@Output() uploadFile = new EventEmitter<File>()`
  - File input: `<input type="file" accept=".pdf,.docx,.txt">`
  - UI: "Choose File" button + selected file name display + "Upload" button
  - Upload button disabled until file selected
  - On "Upload" click: emit uploadFile event with selected File object
  - Clear file selection after upload initiated
  - Validation: file size < 10MB (show error if larger)

  **Must NOT do**:
  - Call AgenticService directly (parent handles via @Output)
  - Upload multiple files (single file only)
  - Add drag-and-drop (Phase 2 enhancement)
  - Preview file content

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Form UI, file input handling, validation
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (standard file upload form)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 10)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models)

  **References**:
  - `apps/admin/src/app/features/agentic-documents/documents-page.component.ts` - Parent component (from task 8)
  - HTML file input API for file selection
  - Angular forms for validation

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/document-upload-form.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/document-upload-form.component.html`
  - [ ] Component has @Output uploadFile
  - [ ] File input accepts .pdf, .docx, .txt
  - [ ] Upload button disabled until file selected
  - [ ] File size validation (< 10MB)
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Upload valid file successfully
    Tool: Playwright
    Preconditions: Admin logged in, on /agentic-documents page
    Steps:
      1. Click "Upload Document" button (opens form)
      2. Upload test file: test-document.pdf (size < 10MB)
      3. Assert: selected file name displayed
      4. Click "Upload" button
      5. Wait for upload completion (loading state clears)
      6. Check network: assert POST /api/v1/agentic/documents called with multipart form
      7. Assert: success message or document appears in list
    Expected Result: File uploaded, API called, success feedback
    Failure Indicators: Upload fails, no API call, error shown
    Evidence: .omo/evidence/task-9-upload-success.png

  Scenario: File size validation rejects large files
    Tool: Playwright
    Preconditions: Admin logged in
    Steps:
      1. Try to upload file > 10MB
      2. Assert: error message shown "File too large (max 10MB)"
      3. Assert: Upload button remains disabled
    Expected Result: Large file rejected with clear error message
    Failure Indicators: Large file accepted, no error shown
    Evidence: .omo/evidence/task-9-file-size-validation.png
  ```

  **Commit**: NO (group with tasks 8, 10)

- [ ] 10. Document List Component

  **What to do**:
  - Create `apps/admin/src/app/features/agentic-documents/document-list.component.ts`
  - Create `apps/admin/src/app/features/agentic-documents/document-list.component.html`
  - Input: `@Input() documents: AgenticDocument[]`
  - Display documents as table:
    - Columns: Filename, Status, Uploaded Date (if available), Actions
    - Status badge: color-coded (processed=green, pending=yellow, error=red)
    - Actions: "Delete" button (Phase 2 - show disabled for now)
  - Empty state: "No documents uploaded yet. Upload your first document to get started."
  - Sorting: by upload date (most recent first)

  **Must NOT do**:
  - Implement delete functionality (out of scope Phase 1)
  - Add document preview (out of scope)
  - Fetch documents directly (parent provides via @Input)
  - Over-complicate table (keep simple)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Table UI, list rendering, status badges
  - **Skills**: None
  - **Skills Evaluated but Omitted**: `frontend-ui-ux` (standard data table)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 9)
  - **Blocks**: Task 11, 12 (tests)
  - **Blocked By**: Tasks 1, 2, 3 (needs models)

  **References**:
  - `apps/admin/src/app/features/agentic-documents/documents-page.component.ts` - Parent component (from task 8)
  - `apps/admin/src/app/models/agentic.models.ts:AgenticDocument` - Data model
  - `apps/admin/src/app/features/users/users-page.component.html` - Table pattern example

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/document-list.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/document-list.component.html`
  - [ ] Component has @Input documents
  - [ ] Table displays: filename, status, actions
  - [ ] Status badges color-coded
  - [ ] Empty state handled
  - [ ] TypeScript compiles: `npm run build` → no errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Document list displays uploaded documents
    Tool: Playwright
    Preconditions: 3 documents uploaded with different statuses
    Steps:
      1. Navigate to /agentic-documents
      2. Wait for document list to render (waitForSelector: '.document-list')
      3. Count table rows: querySelectorAll('tr.document-row').length
      4. Assert: count === 3
      5. Check status badges visible for each row
      6. Assert: filename, status displayed for each document
    Expected Result: All documents shown in table with correct data
    Failure Indicators: Missing documents, status not shown, table broken
    Evidence: .omo/evidence/task-10-document-list.png

  Scenario: Empty state shown when no documents
    Tool: Playwright
    Preconditions: No documents uploaded (fresh state)
    Steps:
      1. Navigate to /agentic-documents
      2. Wait for page load
      3. Check for empty state message
      4. Assert: text contains "No documents uploaded yet"
      5. Assert: no table rows rendered
    Expected Result: Empty state message shown, no table
    Failure Indicators: Empty table shown, wrong message
    Evidence: .omo/evidence/task-10-empty-state.png
  ```

  **Commit**: YES (end of Wave 3)
  - Message: `feat(agentic): add document management components`
  - Files: `apps/admin/src/app/features/agentic-documents/*`
  - Pre-commit: `npm run build`

### Wave 4: Quality (After Waves 2 & 3)

- [ ] 11. Unit Tests for Service and Components

  **What to do**:
  - Create `apps/admin/src/app/services/agentic.service.spec.ts`
    - Test all 7 service methods
    - Mock HttpClient
    - Assert correct HTTP calls (method, URL, body)
    - Assert return types are Observables
  - Create `apps/admin/src/app/features/chat/chat-page.component.spec.ts`
    - Test component initialization
    - Test conversation loading
    - Test selectConversation updates selectedConversationId
  - Create `apps/admin/src/app/features/agentic-documents/documents-page.component.spec.ts`
    - Test component initialization
    - Test documents loading
    - Test role-based upload button visibility
  - All tests must pass: `npm run test:unit`
  - Follow existing test patterns from users-page.component.spec.ts

  **Must NOT do**:
  - Test every minor component (focus on service + page shells)
  - Add excessive mocks (keep tests simple)
  - Skip error case tests (test both success and error paths)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Following established test patterns, straightforward unit tests
  - **Skills**: None
  - **Skills Evaluated but Omitted**: None needed for unit tests

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Task 12)
  - **Blocks**: F1-F4 (final verification needs tests passing)
  - **Blocked By**: Tasks 4-10 (needs components to test)

  **References**:
  - `apps/admin/src/app/services/users.service.spec.ts` - Service test pattern
  - `apps/admin/src/app/features/users/users-page.component.spec.ts` - Component test pattern
  - `apps/admin/src/app/services/agentic-api.service.ts` - Service to test (from task 2)
  - `apps/admin/src/app/features/chat/chat-page.component.ts` - Component to test (from task 4)
  - `apps/admin/src/app/features/agentic-documents/documents-page.component.ts` - Component to test (from task 8)

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/services/agentic.service.spec.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-page.component.spec.ts`
  - [ ] File exists: `apps/admin/src/app/features/agentic-documents/documents-page.component.spec.ts`
  - [ ] All tests pass: `npm run test:unit` → 0 failures
  - [ ] Test count increased (check test output for new test count)

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: All unit tests pass
    Tool: Bash (npm test)
    Preconditions: Unit test files created with test cases
    Steps:
      1. Run: cd apps/admin && npm run test:unit
      2. Wait for test completion
      3. Parse output for test results
      4. Assert: "Tests: X passed, X total" with 0 failures
      5. Assert: test files for agentic service and components executed
    Expected Result: All unit tests pass, no failures
    Failure Indicators: Test failures, compilation errors, missing tests
    Evidence: .omo/evidence/task-11-unit-tests.txt

  Scenario: Service tests cover all methods
    Tool: Bash (grep + count)
    Preconditions: agentic.service.spec.ts created
    Steps:
      1. Run: grep -c "it(" apps/admin/src/app/services/agentic.service.spec.ts
      2. Assert: count >= 7 (one test per service method minimum)
    Expected Result: At least 7 test cases in service spec
    Failure Indicators: Fewer tests than methods
    Evidence: .omo/evidence/task-11-test-coverage.txt
  ```

  **Commit**: NO (group with task 12)

- [ ] 12. E2E Tests for Chat and Document Flows

  **What to do**:
  - Edit `apps/admin/e2e/admin.spec.ts`
  - Add test scenarios:
    1. **Chat flow**: Login → navigate to /chat → create new conversation → send message → assert response received → verify citations displayed
    2. **Document upload flow**: Login as admin → navigate to /agentic-documents → upload test file → assert file appears in list with "processed" status
    3. **Permission check**: Login as employee → navigate to /agentic-documents → assert upload button NOT visible
    4. **Conversation persistence**: Send message → reload page → navigate back to /chat → assert conversation still visible → select conversation → assert messages still there
  - All tests must pass: `npm run e2e`
  - Use Playwright selectors specific to agentic components

  **Must NOT do**:
  - Test every UI detail (focus on critical user flows)
  - Add flaky waits (use proper waitForSelector)
  - Skip negative scenarios (test both success and permission denial)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: E2E tests require careful scenario design, proper waits, cross-component flows
  - **Skills**: [`playwright`]
    - `playwright`: E2E tests use Playwright browser automation, skill provides best practices
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Task 11)
  - **Blocks**: F1-F4 (final verification needs E2E passing)
  - **Blocked By**: Tasks 4-10 (needs full UI implemented)

  **References**:
  - `apps/admin/e2e/admin.spec.ts:1-170` - Existing E2E test patterns
  - `apps/admin/src/app/features/chat/chat-page.component.ts` - Chat page to test (from task 4)
  - `apps/admin/src/app/features/agentic-documents/documents-page.component.ts` - Documents page to test (from task 8)
  - Playwright documentation for browser automation

  **Acceptance Criteria**:
  - [ ] E2E tests added to `apps/admin/e2e/admin.spec.ts`
  - [ ] 4 test scenarios implemented (chat flow, upload, permission check, persistence)
  - [ ] All E2E tests pass: `npm run e2e` → 0 failures
  - [ ] Tests use proper selectors (not brittle XPath)

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: All E2E tests pass
    Tool: Bash (npm e2e)
    Preconditions: E2E tests added, backend running on localhost:8010, frontend on localhost:4200
    Steps:
      1. Start backend: cd /path/to/backend && uvicorn app.main:app (background)
      2. Start frontend: cd apps/admin && npm start (background)
      3. Wait 15s for servers ready
      4. Run: npm run e2e
      5. Parse output for test results
      6. Assert: all tests passed, 0 failures
    Expected Result: All 4 new E2E scenarios pass
    Failure Indicators: Test failures, timeouts, selector issues
    Evidence: .omo/evidence/task-12-e2e-tests.txt

  Scenario: E2E tests cover critical user flows
    Tool: Bash (grep)
    Preconditions: E2E tests added
    Steps:
      1. Run: grep -c "test(" apps/admin/e2e/admin.spec.ts
      2. Assert: count increased by at least 4 (new agentic tests)
      3. Check test names contain: "chat", "upload", "permission", "persistence"
    Expected Result: 4+ new test cases covering critical flows
    Failure Indicators: Fewer tests, missing scenarios
    Evidence: .omo/evidence/task-12-e2e-coverage.txt
  ```

  **Commit**: YES (end of Wave 4)
  - Message: `test(agentic): add unit and e2e tests for agentic features`
  - Files: `apps/admin/src/**/*.spec.ts`, `apps/admin/e2e/admin.spec.ts`
  - Pre-commit: `npm run test:unit && npm run e2e`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .omo/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `npm run build` + `npm run test:unit`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Tests [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (chat → documents, routing). Test edge cases: empty state, network errors, invalid uploads. Save to `.omo/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(agentic): add models, service, routes` - agentic.models.ts, agentic-api.service.ts, app.routes.ts
- **Wave 2**: `feat(agentic): add chat interface` - chat/**
- **Wave 3**: `feat(agentic): add document management` - agentic-documents/**
- **Wave 4**: `test(agentic): add unit and e2e tests` - *.spec.ts, admin.spec.ts

---

## Success Criteria

### Verification Commands
```bash
npm run build           # Expected: SUCCESS, no errors
npm run test:unit       # Expected: all tests PASS, including agentic tests
npm run e2e            # Expected: all E2E scenarios PASS
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Chat interface functional at `/chat`
- [ ] Document management functional at `/agentic-documents`
- [ ] All tests pass
- [ ] Build passes
- [ ] Evidence files exist for all tasks
