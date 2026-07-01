# Agentic MVP - Minimal Chat Interface

## TL;DR

> **Quick Summary**: Minimal viable implementation của agentic chat để demo flow. Chỉ làm core: models, service, route, basic chat window. Skip conversation list, citations, document management, tests.
>
> **Deliverables**:
> - TypeScript models cho agentic API
> - Service layer với 7 API methods
> - Lazy-loaded route `/chat`
> - Basic chat window (send message, receive response, display history)
>
> **Estimated Effort**: Quick (~65 phút)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Models → Service → Route → Chat Window

---

## Context

### Original Request
User muốn incremental MVP: làm đủ để demo được chat flow, bỏ các features phức tạp (conversation list, citations, document management, tests).

### Scope Decision
**IN (MVP):**
- Models definitions
- Service API layer
- Route setup `/chat`
- Basic chat window (send/receive messages, history display)

**OUT (Phase 2):**
- Conversation list sidebar
- Citations display
- Document management
- Unit tests & E2E tests
- Chat page shell (full layout)
- Conversation selection

---

## Work Objectives

### Core Objective
Implement minimal chat interface để có thể chat với agentic API, xem responses, và verify integration hoạt động.

### Concrete Deliverables
- `models/agentic.models.ts` with TypeScript interfaces
- `services/agentic-api.service.ts` with 7 API methods
- Route `/chat` in `app.routes.ts`
- `features/chat/chat-window.component.ts` - basic chat UI

### Definition of Done
- [ ] User có thể navigate to `/chat`
- [ ] User có thể gửi message
- [ ] User nhận được AI response
- [ ] Message history hiển thị đúng
- [ ] Build passes (`npm run build`)

### Must Have
- TypeScript models matching backend schemas
- Service extending BaseApiService
- Lazy-loaded route with AuthGuard
- Chat input + send button
- Message display (user + assistant bubbles)
- Auto-scroll to bottom

### Must NOT Have (Phase 2)
- Conversation list/sidebar
- Conversation selection
- Citations display
- New conversation button
- Document upload
- Tests (skip for MVP)
- Complex error handling (basic only)

---

## Verification Strategy

> Basic verification for MVP. QA scenarios simplified - focus on "does it work".

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: SKIP for MVP
- **Manual verification**: Basic smoke test only

### QA Policy
Each task has basic smoke test scenario. Evidence capture optional for MVP.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - parallel):
├── Task 1: TypeScript models [quick]
├── Task 2: Service API layer [quick]
└── Task 3: Route setup [quick]

Wave 2 (UI):
└── Task 4: Basic chat window [visual-engineering]

Critical Path: Task 1 → Task 2 → Task 3 → Task 4
Parallel Speedup: Wave 1 runs in parallel (3 tasks)
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

- **1**: - - 2, 4
- **2**: 1 - 3, 4
- **3**: 1, 2 - 4
- **4**: 1, 2, 3 - (final)

### Agent Dispatch Summary

- **Wave 1**: **3 tasks** - T1-T3 → `quick`
- **Wave 2**: **1 task** - T4 → `visual-engineering`

---

## TODOs

> **FORMAT**: Task labels MUST use bare numbers: `1.`, `2.`, `3.` — NOT `T1.`, `Task 1.`, `Phase 1:`.

### Wave 1: Foundation (Start Immediately - Parallel)

- [ ] 1. TypeScript Models for Agentic API

  **What to do**:
  - Create `apps/admin/src/app/models/agentic.models.ts`
  - Define interfaces:
    - `AgenticConversation`: conversation_id, thread_id, user_id, status, title
    - `AgenticMessage`: turn_id, conversation_id, turn_index, user_message, assistant_message, assistant_status
    - `AgenticChatRequest`: message, top_k
    - `AgenticChatResponse`: conversation_id, thread_id, answer, status, cited_chunk_ids, cited_document_ids, citations
  - Use TypeScript strict types (no `any`)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  - `app/presentation/schemas/agentic_schema.py:7-74` - Backend schemas
  - `apps/admin/src/app/models/user.models.ts` - Existing model pattern

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/models/agentic.models.ts`
  - [ ] All 4 interfaces defined
  - [ ] TypeScript compiles: `npm run build` → no errors
  - [ ] No `any` types

  **Commit**: NO (group with Wave 1)

- [ ] 2. AgenticService API Layer

  **What to do**:
  - Create `apps/admin/src/app/services/agentic-api.service.ts`
  - Extend `BaseApiService`
  - Implement 7 methods:
    - `getConversations()` → GET `/api/v1/agentic/conversations`
    - `createConversation(title?)` → POST `/api/v1/agentic/conversations`
    - `getConversationMessages(conversationId)` → GET `/api/v1/agentic/conversations/{id}/messages`
    - `quickChat(message, topK?)` → POST `/api/v1/agentic/chat`
    - `chatInConversation(conversationId, message, topK?)` → POST `/api/v1/agentic/conversations/{id}/messages`
    - `uploadDocument(file)` → POST `/api/v1/agentic/documents`
    - `getDocuments()` → GET `/api/v1/agentic/documents`
  - Use `buildUrl()` for endpoints
  - Return typed Observables

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1 (needs models)

  **References**:
  - `apps/admin/src/app/services/user-api.service.ts` - Service pattern
  - `apps/admin/src/app/services/base-api.service.ts` - Base class
  - `app/presentation/api/v1/agentic/router.py:73-245` - Backend endpoints

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/services/agentic-api.service.ts`
  - [ ] Extends BaseApiService
  - [ ] All 7 methods implemented
  - [ ] TypeScript compiles: `npm run build` → no errors
  - [ ] No hard-coded URLs

  **Commit**: NO (group with Wave 1)

- [ ] 3. Lazy-Loaded Route Setup

  **What to do**:
  - Edit `apps/admin/src/app/app.routes.ts`
  - Add lazy route:
    ```typescript
    {
      path: 'chat',
      loadComponent: () => import('./features/chat/chat-window.component').then(m => m.ChatWindowComponent),
      canActivate: [authGuard]
    }
    ```
  - Add navigation link in `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`:
    - "Chat" link to `/chat` (icon: chat_bubble)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/app.routes.ts:10-50` - Existing routes
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Nav menu

  **Acceptance Criteria**:
  - [ ] Route added: `/chat`
  - [ ] Lazy loadComponent
  - [ ] Has authGuard
  - [ ] Nav link added
  - [ ] Build passes

  **Commit**: YES (end of Wave 1)
  - Message: `feat(agentic): add MVP foundation (models, service, route)`
  - Files: `models/agentic.models.ts`, `services/agentic-api.service.ts`, `app.routes.ts`, `admin-shell.component.ts`

---

### Wave 2: Basic Chat Window (After Wave 1)

- [ ] 4. Basic Chat Window Component

  **What to do**:
  - Create `apps/admin/src/app/features/chat/chat-window.component.ts`
  - Create `apps/admin/src/app/features/chat/chat-window.component.html`
  - Inject `AgenticApiService`
  - Signal state:
    - `messages = signal<AgenticMessage[]>([])`
    - `userInput = signal<string>('')`
    - `sendingMessage = signal<boolean>(false)`
  - UI structure:
    - Message list (scrollable, display user_message + assistant_message)
    - Input box at bottom (textarea + "Send" button)
  - Send message flow:
    - Call `agenticService.quickChat(message)` (auto-creates conversation)
    - On response: append to messages array
    - Clear input, scroll to bottom
  - Use `runAdminAsync` for loading states
  - Simple styling: chat bubbles (user=right/blue, assistant=left/gray)

  **Must NOT do**:
  - Conversation list sidebar (not in MVP)
  - Citations display (not in MVP)
  - Conversation selection (not in MVP)
  - Complex error handling (basic toast only)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Chat UI, message display, styling
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (single task)
  - **Blocks**: None (final task)
  - **Blocked By**: Tasks 1, 2, 3

  **References**:
  - `apps/admin/src/app/services/agentic-api.service.ts` - Service to inject
  - `apps/admin/src/app/models/agentic.models.ts` - Models
  - `apps/admin/src/app/shared/async-state.ts:runAdminAsync` - Loading helper

  **Acceptance Criteria**:
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-window.component.ts`
  - [ ] File exists: `apps/admin/src/app/features/chat/chat-window.component.html`
  - [ ] Can send message and receive response
  - [ ] Message history displays correctly
  - [ ] Auto-scroll to bottom
  - [ ] Build passes
  - [ ] Route `/chat` accessible and renders component

  **QA Scenario (Basic Smoke Test)**:
  ```
  Manual Test:
    1. npm start (start dev server)
    2. Navigate to http://localhost:4200/chat
    3. Type message: "Hello"
    4. Click Send
    5. Verify: message appears as user bubble
    6. Wait for response
    7. Verify: AI response appears as assistant bubble
    8. Send another message
    9. Verify: history shows both previous + new messages
    Expected: Chat works end-to-end
  ```

  **Commit**: YES
  - Message: `feat(agentic): add basic chat window MVP`
  - Files: `features/chat/chat-window.component.ts`, `features/chat/chat-window.component.html`

---

## Commit Strategy

- **Wave 1**: `feat(agentic): add MVP foundation (models, service, route)`
- **Wave 2**: `feat(agentic): add basic chat window MVP`

---

## Success Criteria

### Verification Commands
```bash
npm run build           # Expected: SUCCESS
# Manual test: navigate to /chat, send message, verify response
```

### Final Checklist
- [ ] Route `/chat` accessible
- [ ] Can send message
- [ ] Receive AI response
- [ ] Message history displays
- [ ] Build passes
- [ ] No TypeScript errors

---

## Next Steps After MVP

**Phase 2 (Full Features) - separate plan:**
- Conversation list sidebar
- Citations display
- Chat page shell with layout
- Document management
- Unit tests & E2E tests

**To proceed with Phase 2, use full plan:** `.omo/plans/agentic-integration.md`
