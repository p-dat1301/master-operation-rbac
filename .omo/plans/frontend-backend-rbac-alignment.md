# Frontend-Backend RBAC Alignment

## TL;DR

> **Quick Summary**: Align frontend visibility, route guards, and action affordances with backend RBAC behavior, while fixing backend user-scope handling so managers can view department-subtree users and employees can view self only.
>
> **Deliverables**:
> - Backend RBAC/user-scope fixes for users listing and self access
> - Canonical permission mismatch fixes affecting audit/task behavior
> - Frontend route/nav/action alignment for users/tasks based on backend capabilities
> - Automated backend/frontend/e2e coverage for admin, manager, and employee
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Users scope rules → users API/use-case tests → frontend users gating → end-to-end RBAC verification

---

## Context

### Original Request
User reported that frontend permissions do not fully match backend RBAC. Example mismatches: manager cannot view department users and may not be able to create tasks. The requirement is to verify all relevant frontend role behavior against backend API behavior, with backend treated as the source of truth.

### Interview Summary
**Key Discussions**:
- Backend is the source of truth; frontend must mirror backend capabilities and scopes as UX, not replace backend enforcement.
- `UserRepository.list_by_department()` already exists and should be used rather than granting `manage_org` to manager.
- Manager users behavior: manager can view users in their department subtree only.
- Manager user-management action behavior: user explicitly chose manager is view-only on Users page; manager must not create, edit, reset password, activate, or deactivate users.
- Manager no-department behavior: user explicitly chose self-only fallback.
- Employee users behavior: employee can view self only.
- RBAC Roles/Permissions list mismatch stays out of scope for this plan.

**Research Findings**:
- `ListUsersUseCase` currently requires `manage_org` and always calls `find_all()`, so it does not use department-scoped listing.
- Frontend `/users` route and nav currently require `manage_org`, so manager is blocked in UI before backend is even reached.
- Frontend `/tasks` route is guarded by `create_task`, but task-page action gating is coarser than backend action rules.
- Backend permission mismatches exist: `audit:view` vs `view_audit_logs`, and `complete_task` is checked in backend logic but not seeded.

### Metis Review
**Identified Gaps** (addressed):
- Clarified exact manager users behavior as department subtree view only.
- Clarified employee users behavior as self only.
- Locked RBAC roles/permissions list mismatch out of scope to avoid scope creep.
- Chose tests-after strategy with mandatory agent-executed QA.

---

## Work Objectives

### Core Objective
Bring frontend RBAC behavior into alignment with backend authorization and scope rules for the targeted areas, while minimally extending backend user-list scope behavior to support manager department-subtree viewing and employee self-only access.

### Concrete Deliverables
- Updated backend user-listing scope logic and tests
- Canonicalized targeted permission-name mismatches affecting current flows
- Updated frontend route/nav/action gating for users/tasks where required
- Regression coverage for admin, manager, and employee behaviors

### Definition of Done
- [ ] Backend tests pass for admin/manager/employee user listing scope, audit permission naming, and any touched task permission behavior
- [ ] Frontend unit/integration checks pass for updated guards/gating
- [ ] Playwright scenarios pass for admin, manager, and employee RBAC flows
- [ ] No broad permission escalation such as granting `manage_org` to manager

### Must Have
- Manager can view users in department subtree only
- Manager is view-only on Users page and cannot create/edit/reset/activate/deactivate users
- Manager without department falls back to self-only users behavior
- Employee can view self only for user-detail/self behavior
- Frontend users visibility mirrors backend scope behavior
- Frontend task access/actions are reviewed against backend capability rules
- Targeted permission-string mismatches are resolved consistently

### Must NOT Have (Guardrails)
- Do not grant `manage_org` to manager to unlock users access
- Do not redesign the entire RBAC model
- Do not move authorization responsibility to frontend filtering
- Do not expand scope to RBAC roles/permissions list UX in this plan
- Do not weaken backend authorization to match current frontend behavior

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: pytest, Angular unit tests, Playwright
- **Agent-Executed QA**: REQUIRED for all tasks

### QA Policy
Evidence and outputs should be captured via:
- **Backend/API**: pytest + curl where useful
- **Frontend logic**: Angular unit tests and targeted guard/service tests
- **End-to-end**: Playwright role-based flows
- **Evidence location**: `.omo/evidence/task-{N}-{scenario-slug}.{ext}` where applicable during execution

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - authority + backend foundations):
├── Task 1: Canonical RBAC mismatch matrix and touched-symbol inventory [quick]
├── Task 2: Backend users scope design + tests specification [deep]
├── Task 3: Canonical permission-name alignment design for audit/task mismatches [quick]
└── Task 4: Frontend gating inventory for users/tasks against backend rules [quick]

Wave 2 (After Wave 1 - backend implementation, max parallel):
├── Task 5: Implement backend users scope behavior in use case/API path [deep]
├── Task 6: Add/adjust backend tests for users scope and self-access [unspecified-high]
├── Task 7: Fix targeted backend permission-name mismatch handling [unspecified-high]
└── Task 8: Verify task permission semantics and decide minimal frontend-facing contract updates [deep]

Wave 3 (After Wave 2 - frontend alignment):
├── Task 9: Update frontend users route/nav gating to mirror backend users scope [visual-engineering]
├── Task 10: Update frontend users page behavior for manager/employee scope [unspecified-high]
├── Task 11: Update frontend task affordances/gating to reflect backend capabilities [unspecified-high]
└── Task 12: Add/update frontend tests for guards and permission-driven visibility [quick]

Wave 4 (After Wave 3 - integration and verification):
├── Task 13: Add/adjust Playwright admin-manager-employee RBAC scenarios [unspecified-high]
├── Task 14: Add direct API verification scenarios for role-based access [quick]
└── Task 15: Run full regression and resolve alignment defects [deep]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real QA execution (unspecified-high)
└── Task F4: Scope fidelity check (deep)
```

### Dependency Matrix
- **1**: - - 5, 7, 9, 1
- **2**: - - 5, 6, 2
- **3**: - - 7, 3
- **4**: - - 9, 10, 11, 4
- **5**: 1, 2 - 9, 10, 13, 5
- **6**: 2, 5 - 15, 6
- **7**: 1, 3 - 11, 13, 7
- **8**: 4 - 11, 12, 8
- **9**: 4, 5 - 13, 15, 9
- **10**: 4, 5 - 13, 15, 10
- **11**: 4, 7, 8 - 13, 15, 11
- **12**: 8, 9, 11 - 15, 12
- **13**: 5, 7, 9, 10, 11 - 15, 13
- **14**: 5, 7 - 15, 14
- **15**: 6, 9, 10, 11, 12, 13, 14 - F1-F4, 15

### Agent Dispatch Summary
- **1**: **4** - T1 → `quick`, T2 → `deep`, T3 → `quick`, T4 → `quick`
- **2**: **4** - T5 → `deep`, T6 → `unspecified-high`, T7 → `unspecified-high`, T8 → `deep`
- **3**: **4** - T9 → `visual-engineering`, T10 → `unspecified-high`, T11 → `unspecified-high`, T12 → `quick`
- **4**: **3** - T13 → `unspecified-high`, T14 → `quick`, T15 → `deep`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Build canonical RBAC mismatch matrix

  **What to do**:
  - Compare backend seed permissions, backend use-case checks, API route behavior, and frontend route/nav/action guards.
  - Produce a concise matrix for Users, Tasks, Leaves, Audit, Config Sync, and RBAC list pages.
  - Mark RBAC Roles/Permissions list mismatch as explicitly out-of-scope per user decision.

  **Must NOT do**:
  - Do not change code in this task.
  - Do not broaden manager permissions.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Read-only synthesis from known files and prior findings.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Use process/symbol relationships for endpoint and guard mapping.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: No edits in this task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 7, 9
  - **Blocked By**: None

  **References**:
  - `app/infrastructure/database/seed.py` - Role and permission seed source.
  - `app/domain/services/rbac_service.py` - Backend role/scope logic.
  - `app/application/use_cases/user/list_users.py` - Current users list mismatch.
  - `apps/admin/src/app/app.routes.ts` - Frontend route permission gates.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Frontend nav visibility gates.

  **Acceptance Criteria**:
  - [ ] Matrix lists backend requirement, frontend behavior, mismatch, and planned action for each in-scope feature.
  - [ ] Matrix explicitly states manager users = department subtree view only, employee users = self only.

  **QA Scenarios**:
  ```
  Scenario: Matrix includes in-scope feature rows
    Tool: Bash
    Preconditions: Repo checked out with plan available.
    Steps:
      1. Inspect generated matrix artifact or task output.
      2. Confirm rows exist for Users, Tasks, Leaves, Audit, Config Sync.
      3. Confirm RBAC Roles/Permissions list is marked out-of-scope.
    Expected Result: All rows present with no TBD decision markers.
    Failure Indicators: Missing feature row or unresolved scope question.
    Evidence: .omo/evidence/task-1-rbac-matrix.txt
  ```

  **Commit**: NO

- [x] 2. Specify backend users scope tests

  **What to do**:
  - Define test cases before implementation for admin all-users, manager department-subtree users, employee self-only behavior, manager no-department behavior, and filter-within-scope behavior.
  - Locate existing test patterns and choose the smallest test files to extend.

  **Must NOT do**:
  - Do not implement user scope logic here unless paired with Task 6 by same executor.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires backend RBAC semantics and edge-case coverage.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Locate current test/use-case execution flows.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Backend test design only.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 6
  - **Blocked By**: None

  **References**:
  - `app/application/use_cases/user/list_users.py` - Target behavior under test.
  - `app/domain/repositories/user_repository.py:list_by_department()` - Repository capability.
  - `app/infrastructure/database/repositories/sqlalchemy_user_repo.py:list_by_department()` - SQLAlchemy implementation.
  - `app/domain/services/rbac_service.py` - Existing scope helper style for tasks/leaves/attendance.
  - `tests/unit/domain/test_rbac_service.py` - RBAC service test style.

  **Acceptance Criteria**:
  - [ ] Test cases specify exact expected users for admin, manager, and employee.
  - [ ] Tests define behavior for manager with `department_id=None` as self-only fallback.
  - [ ] Tests verify filters cannot escape authorized scope.

  **QA Scenarios**:
  ```
  Scenario: Users scope test plan is executable
    Tool: Bash
    Preconditions: Test case list completed.
    Steps:
      1. Inspect test case list.
      2. Verify each case names actor role, department setup, request/filter, and expected IDs/status.
    Expected Result: Every backend users scope case has concrete data and expected output.
    Failure Indicators: Vague case like "manager sees department" without IDs or status.
    Evidence: .omo/evidence/task-2-users-scope-tests.txt
  ```

  **Commit**: NO

- [x] 3. Choose canonical permission names for targeted mismatches

  **What to do**:
  - Decide the smallest canonical fix for `audit:view` vs `view_audit_logs`.
  - Decide whether `complete_task` should be seeded, removed from check, or replaced by assigner/status semantics.
  - Update the matrix with the chosen action and tests required.

  **Must NOT do**:
  - Do not redesign permission taxonomy.
  - Do not touch RBAC roles/permissions list endpoint policy.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small permission vocabulary alignment task.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Find all references before specifying changes.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Only needed if executing a symbol rename.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - `app/infrastructure/database/seed.py` - Seeded permission strings.
  - `app/application/use_cases/audit_log/list_audit_logs.py` - Backend audit permission check.
  - `app/application/use_cases/task/complete.py` - Backend `complete_task` reference.
  - `apps/admin/src/app/app.routes.ts` - Frontend audit route permission string.

  **Acceptance Criteria**:
  - [ ] Canonical audit permission choice is documented with all references to change.
  - [ ] `complete_task` handling choice is documented with backend and frontend implications.

  **QA Scenarios**:
  ```
  Scenario: Permission mismatch references are complete
    Tool: Bash
    Preconditions: Reference scan completed.
    Steps:
      1. Search codebase for `audit:view`, `view_audit_logs`, and `complete_task`.
      2. Compare search results with task output.
    Expected Result: Task output accounts for every occurrence.
    Failure Indicators: Occurrence found but not listed in planned action.
    Evidence: .omo/evidence/task-3-permission-scan.txt
  ```

  **Commit**: NO

- [x] 4. Inventory frontend users/tasks gating against backend rules

  **What to do**:
  - Map current `/users` and `/tasks` route/nav/button visibility to backend behavior.
  - Identify exact frontend changes required for admin, manager, and employee.
  - Confirm whether task create UI exists or manager task failure is a missing-UI/API-contract issue.

  **Must NOT do**:
  - Do not implement broad frontend policy framework unless existing patterns demand it.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Focused frontend code inspection.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Use indexed symbols and route relationships.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: This is permission behavior, not visual redesign.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 9, 10, 11
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/app.routes.ts` - Route guard source.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Nav gating source.
  - `apps/admin/src/app/features/users/users-page.component.ts` - Users actions and table behavior.
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts` - Task actions and missing create UI check.
  - `apps/admin/src/app/services/auth-store.service.ts` - `hasPermission()` and `/me` state.

  **Acceptance Criteria**:
  - [ ] Output lists exact route/nav/action conditions to change.
  - [ ] Output distinguishes missing create-task UI from RBAC denial if applicable.

  **QA Scenarios**:
  ```
  Scenario: Frontend gating inventory matches source
    Tool: Bash
    Preconditions: Inventory completed.
    Steps:
      1. Search frontend for permission strings `manage_org`, `create_task`, `assign_task`, `approve_leave`, `audit:view`.
      2. Confirm every users/tasks occurrence appears in inventory.
    Expected Result: No users/tasks gating occurrence is omitted.
    Failure Indicators: A permission string appears in source but not in inventory.
    Evidence: .omo/evidence/task-4-frontend-gating.txt
  ```

  **Commit**: NO

- [x] 5. Implement backend users scope behavior

  **What to do**:
  - Run GitNexus impact on `ListUsersUseCase.execute` before edits.
  - Add user scope logic so admin/super-admin sees all users, manager sees department subtree users, and employee receives self-only behavior.
  - Use repository scoping and department tree support where available; do not authorize by API-side post-filtering.
  - Preserve existing query filters by applying them only after authorized scope is established, or move filter support into repository if existing patterns support it.

  **Must NOT do**:
  - Do not grant `manage_org` to manager.
  - Do not return out-of-scope users then rely on frontend filtering.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core backend authorization behavior with security impact.
  - **Skills**: [`gitnexus-impact-analysis`, `gitnexus-exploring`]
    - `gitnexus-impact-analysis`: Required before editing use case symbols.
    - `gitnexus-exploring`: Trace repository/use-case/API patterns.
  - **Skills Evaluated but Omitted**:
    - `security-research`: Scope is targeted RBAC alignment, not full audit.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 6, 9, 10, 13, 14
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `app/application/use_cases/user/list_users.py:ListUsersUseCase.execute` - Primary target.
  - `app/domain/repositories/user_repository.py:list_by_department()` - Existing abstraction.
  - `app/infrastructure/database/repositories/sqlalchemy_user_repo.py:list_by_department()` - Existing implementation.
  - `app/application/use_cases/leave_request/list_leave_request.py` - Department subtree scope pattern.
  - `app/domain/services/rbac_service.py` - Existing scope helper patterns.
  - `app/presentation/api/v1/users.py:list_users` - API path and filters.

  **Acceptance Criteria**:
  - [ ] Manager with department sees only users in department subtree.
  - [ ] Manager without department falls back to self-only behavior.
  - [ ] Manager cannot obtain users outside department subtree via filters.
  - [ ] Employee gets self-only users behavior as decided.
  - [ ] Admin still sees all users.

  **QA Scenarios**:
  ```
  Scenario: Manager users scope is department subtree
    Tool: Bash (pytest)
    Preconditions: Test fixtures include manager department, child department user, and outside department user.
    Steps:
      1. Run targeted users scope tests.
      2. Inspect assertion output for manager result IDs.
    Expected Result: Manager result contains same-department and child-department users, excludes outside-department users.
    Failure Indicators: Outside-department user appears, or child-department user is missing.
    Evidence: .omo/evidence/task-5-manager-users-scope.txt

  Scenario: Employee users scope is self only
    Tool: Bash (pytest)
    Preconditions: Test fixtures include employee and at least one other user.
    Steps:
      1. Run targeted users scope tests.
      2. Inspect employee result IDs.
    Expected Result: Employee receives only their own user record or the agreed self-only response shape.
    Failure Indicators: Employee sees another user or receives unexpected 403 if self-only endpoint behavior is implemented as list.
    Evidence: .omo/evidence/task-5-employee-self-users.txt
  ```

  **Commit**: YES
  - Message: `fix(rbac): scope user listing by role`

- [x] 6. Add backend tests for users scope and filters

  **What to do**:
  - Add unit/integration tests covering admin, manager department subtree, manager no-department, employee self-only, and filter-within-scope behavior.
  - Include direct API tests if existing integration patterns support authenticated role fixtures.

  **Must NOT do**:
  - Do not test by asserting frontend behavior only; backend authorization must be proven directly.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Test-heavy backend work across fixtures and use cases.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Locate existing test fixture and auth patterns.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Backend tests only.

  **Parallelization**:
  - **Can Run In Parallel**: YES after Task 5 interface is clear
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 2, 5

  **References**:
  - `tests/integration/test_auth.py` - Authenticated test style.
  - `tests/unit/domain/test_rbac_service.py` - RBAC test style.
  - `app/application/use_cases/user/list_users.py` - Behavior under test.
  - `app/presentation/api/v1/users.py` - API behavior under test.

  **Acceptance Criteria**:
  - [ ] Tests fail against old `manage_org`-only implementation and pass after Task 5.
  - [ ] Tests explicitly prove filters cannot escape scope.
  - [ ] Tests document manager no-department self-only fallback behavior.

  **QA Scenarios**:
  ```
  Scenario: Backend users scope regression suite passes
    Tool: Bash
    Preconditions: Task 5 implementation complete.
    Steps:
      1. Run targeted pytest file(s) for user listing scope.
      2. Run broader relevant backend RBAC/user tests.
    Expected Result: All targeted tests pass and include admin, manager, employee, filter escape, and no-department cases.
    Failure Indicators: Missing role case or test failure.
    Evidence: .omo/evidence/task-6-users-scope-pytest.txt
  ```

  **Commit**: YES
  - Message: `test(rbac): cover scoped user listing`

- [x] 7. Fix targeted backend permission-name mismatches

  **What to do**:
  - Align audit permission naming so seeded data, backend checks, and frontend guards use one canonical string.
  - Resolve `complete_task` mismatch by either seeding it or removing/replacing the check according to intended backend semantics.
  - Update any impacted tests and fixtures.

  **Must NOT do**:
  - Do not rename permissions ad hoc without updating all references.
  - Do not expand into unrelated permission cleanup beyond the targeted mismatches.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-layer permission vocabulary fix with behavior impact.
  - **Skills**: [`gitnexus-impact-analysis`, `gitnexus-exploring`]
    - `gitnexus-impact-analysis`: Required before editing target symbols.
    - `gitnexus-exploring`: Find all references across backend/frontend/tests.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Helpful for rename-like changes, but only if symbol-safe rename is needed during execution.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 11, 13, 14
  - **Blocked By**: Tasks 1, 3

  **References**:
  - `app/infrastructure/database/seed.py` - Seed permission names.
  - `app/application/use_cases/audit_log/list_audit_logs.py` - Audit permission check target.
  - `app/application/use_cases/task/complete.py` - `complete_task` behavior target.
  - `apps/admin/src/app/app.routes.ts` - Frontend audit permission usage.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Frontend audit nav permission usage.

  **Acceptance Criteria**:
  - [ ] Seed data and backend checks use canonical audit permission naming consistently.
  - [ ] No backend path checks `complete_task` without a documented permission source or intended alternative rule.
  - [ ] Frontend audit route/nav permission matches backend canonical string.

  **QA Scenarios**:
  ```
  Scenario: Audit permission is canonical end-to-end
    Tool: Bash
    Preconditions: Permission-name fix implemented.
    Steps:
      1. Search backend/frontend/tests for old and new audit permission strings.
      2. Run targeted audit authorization tests.
    Expected Result: Only canonical audit permission remains in active code paths and tests pass.
    Failure Indicators: Mixed permission strings remain or authorized user still gets 403.
    Evidence: .omo/evidence/task-7-audit-permission.txt
  ```

  **Commit**: YES
  - Message: `fix(rbac): align permission identifiers`

- [x] 8. Verify backend task capability contract for frontend alignment

  **What to do**:
  - Confirm the intended backend contract for task create/assign/complete/start/cancel/update/delete relative to admin, manager, employee, assigner, and assignee.
  - Identify the minimal frontend-facing capability matrix needed so UI mirrors backend without over-restricting.
  - If needed, add or update backend tests to document current intended semantics before frontend changes.

  **Must NOT do**:
  - Do not redesign task workflow or statuses.
  - Do not hide actions in frontend that backend explicitly intends to allow.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Cross-role business rule interpretation.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Trace task use cases and repo/API flows.
  - **Skills Evaluated but Omitted**:
    - `security-research`: Overkill for bounded RBAC contract confirmation.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 11, 12
  - **Blocked By**: Task 4

  **References**:
  - `app/application/use_cases/task/create.py`
  - `app/application/use_cases/task/assign.py`
  - `app/application/use_cases/task/complete.py`
  - `app/application/use_cases/task/start.py`
  - `app/application/use_cases/task/cancel.py`
  - `app/application/use_cases/task/list_tasks.py`
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts`

  **Acceptance Criteria**:
  - [ ] Capability matrix explicitly states who can create, assign, start, complete, cancel, update, and delete tasks.
  - [ ] Matrix distinguishes permission-based vs relation-based rules (assigner/assignee).

  **QA Scenarios**:
  ```
  Scenario: Task capability matrix covers all task actions
    Tool: Bash
    Preconditions: Matrix completed.
    Steps:
      1. Compare matrix rows with all task use case files.
      2. Verify every task action endpoint is represented.
    Expected Result: No task endpoint/action is omitted.
    Failure Indicators: Missing action or ambiguous actor rule.
    Evidence: .omo/evidence/task-8-task-capability-matrix.txt
  ```

  **Commit**: NO

- [x] 9. Update frontend users route and nav gating

  **What to do**:
  - Run GitNexus impact on the relevant guard/nav symbols before edits.
  - Replace `manage_org`-only users access gating with logic that mirrors backend users access policy for admin and manager department-subtree viewing.
  - Ensure employees do not gain `/users` list-page access unless the chosen self-only UX requires a separate self path.

  **Must NOT do**:
  - Do not expose `/users` to all authenticated users.
  - Do not derive access from unrelated permissions like attendance unless explicitly implemented in backend too.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Frontend route/nav behavior with user-facing visibility changes.
  - **Skills**: [`gitnexus-impact-analysis`, `gitnexus-exploring`]
    - `gitnexus-impact-analysis`: Required before editing guard/nav symbols.
    - `gitnexus-exploring`: Find current route/nav patterns.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No redesign required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 13, 15
  - **Blocked By**: Tasks 4, 5

  **References**:
  - `apps/admin/src/app/app.routes.ts`
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`
  - `apps/admin/src/app/core/guards/permission.guard.ts`
  - `apps/admin/src/app/services/auth-store.service.ts`

  **Acceptance Criteria**:
  - [ ] Admin sees Users nav and can access `/users`.
  - [ ] Manager sees Users nav and can access `/users`.
  - [ ] Employee does not see Users nav and cannot access `/users` list page.

  **QA Scenarios**:
  ```
  Scenario: Users nav visibility matches role
    Tool: Playwright
    Preconditions: Seeded admin, manager, employee accounts available.
    Steps:
      1. Sign in as admin and confirm Users nav is visible.
      2. Sign in as manager and confirm Users nav is visible.
      3. Sign in as employee and confirm Users nav is absent.
      4. Directly navigate employee to `/users`.
    Expected Result: Admin/manager can navigate; employee nav hidden and direct route denied or redirected per app policy.
    Failure Indicators: Manager nav missing or employee gains list-page access.
    Evidence: .omo/evidence/task-9-users-nav-visibility.png
  ```

  **Commit**: YES
  - Message: `fix(admin): align users access gating`

- [x] 10. Update frontend users page behavior for scoped data

  **What to do**:
  - Ensure users page works correctly for manager scoped list and employee self-only policy.
  - Hide management actions from manager because manager users behavior is view-only for department subtree.
  - Ensure page messaging/empty states do not imply org-wide access.

  **Must NOT do**:
  - Do not let manager create/reset/deactivate users if backend behavior does not allow it.
  - Do not fake subtree filtering in frontend if backend API is authoritative.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Frontend page logic plus behavior-sensitive action visibility.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Locate page/action patterns.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Used for verification, not implementation.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 13, 15
  - **Blocked By**: Tasks 4, 5

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts`
  - `app/presentation/api/v1/users.py`
  - `app/application/use_cases/user/list_users.py`
  - Any existing frontend current-user/self display patterns

  **Acceptance Criteria**:
  - [ ] Manager sees scoped department-subtree users only.
  - [ ] Manager without department receives self-only fallback behavior.
  - [ ] Manager does not see user-management actions because users access is view-only for manager.
  - [ ] Employee self-only behavior is represented through correct UX/path without opening org-wide users page.

  **QA Scenarios**:
  ```
  Scenario: Manager users page is view-only and scoped
    Tool: Playwright
    Preconditions: Backend users scope fix complete and manager account seeded.
    Steps:
      1. Sign in as manager.
      2. Open `/users`.
      3. Verify same-department and child-department users appear.
      4. Verify create/reset/deactivate controls are absent if manager is view-only.
    Expected Result: Scoped visibility with no forbidden management actions.
    Failure Indicators: Cross-department user shown or management actions exposed incorrectly.
    Evidence: .omo/evidence/task-10-manager-users-page.png
  ```

  **Commit**: YES
  - Message: `fix(admin): scope users page by role`

- [x] 11. Update frontend task affordances to mirror backend capabilities

  **What to do**:
  - Adjust task route/action visibility so create access and per-task actions reflect backend permission and relation rules as closely as feasible.
  - If create-task UI is missing, add or expose only the minimal existing flow required for users with `create_task`.
  - Ensure unauthorized backend responses are handled clearly without stale UI state.

  **Must NOT do**:
  - Do not invent new task permissions in frontend.
  - Do not expose admin-only task controls to manager/employee.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Mixed frontend logic and API behavior alignment.
  - **Skills**: [`gitnexus-impact-analysis`, `gitnexus-exploring`]
    - `gitnexus-impact-analysis`: Required before editing task page symbols.
    - `gitnexus-exploring`: Map existing task API/UI wiring.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: This is policy alignment, not visual enhancement.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 13, 15
  - **Blocked By**: Tasks 4, 7, 8

  **References**:
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts`
  - `apps/admin/src/app/services/task-api.service.ts`
  - `app/application/use_cases/task/*.py`
  - Existing e2e/task API tests if present

  **Acceptance Criteria**:
  - [ ] Manager with `create_task` can access the task creation flow if backend allows it.
  - [ ] Task action buttons are not shown purely by status when backend requires stronger conditions.
  - [ ] Frontend handles 403/validation errors from task actions clearly.

  **QA Scenarios**:
  ```
  Scenario: Manager can create task when backend allows it
    Tool: Playwright
    Preconditions: Manager account has `create_task`; task create flow exists.
    Steps:
      1. Sign in as manager.
      2. Open `/tasks`.
      3. Create a task with concrete payload for a same-department assignee.
      4. Verify success feedback and visible new task row.
    Expected Result: Manager can complete create flow successfully.
    Failure Indicators: Missing create affordance, 403, or failed payload handling.
    Evidence: .omo/evidence/task-11-manager-create-task.png

  Scenario: Unauthorized task action is blocked in UI and backend
    Tool: Playwright + Bash (curl)
    Preconditions: Seeded user without relevant permission/relation.
    Steps:
      1. Sign in as restricted actor and inspect task action buttons.
      2. Attempt direct API call for forbidden action.
    Expected Result: UI does not expose action incorrectly and backend returns 403 on direct call.
    Evidence: .omo/evidence/task-11-task-action-denial.txt
  ```

  **Commit**: YES
  - Message: `fix(admin): align task affordances with rbac`

- [x] 12. Add frontend tests for guards and permission visibility

  **What to do**:
  - Add/update Angular tests for auth store permission handling, route guards, and nav/page visibility logic touched by the changes.
  - Lock the users/tasks gating behavior for admin, manager, and employee.

  **Must NOT do**:
  - Do not rely only on e2e tests; unit-level guard checks must remain fast.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small targeted frontend tests.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Locate current spec structure and mocks.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Reserved for full-flow verification.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 8, 9, 11

  **References**:
  - `apps/admin/src/app/core/guards/auth.guard.spec.ts`
  - `apps/admin/src/app/services/auth-store.service.spec.ts`
  - Any task/users page specs added or existing patterns in repo

  **Acceptance Criteria**:
  - [ ] Tests cover users nav/route visibility for admin/manager/employee.
  - [ ] Tests cover any task create/action visibility rules added.

  **QA Scenarios**:
  ```
  Scenario: Frontend permission tests pass
    Tool: Bash
    Preconditions: Specs added/updated.
    Steps:
      1. Run Angular unit tests.
      2. Inspect output for updated users/tasks guard/visibility specs.
    Expected Result: All relevant frontend permission specs pass.
    Failure Indicators: Missing spec or failed visibility assertion.
    Evidence: .omo/evidence/task-12-frontend-permission-tests.txt
  ```

  **Commit**: YES
  - Message: `test(admin): lock rbac visibility rules`

- [x] 13. Add end-to-end admin-manager-employee RBAC scenarios

  **What to do**:
  - Extend Playwright coverage to verify role-based behavior for users and tasks.
  - Use seeded accounts and at least two departments so subtree scope is provable.

  **Must NOT do**:
  - Do not rely on a single admin-path e2e only.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-stack behavior verification.
  - **Skills**: [`playwright`]
    - `playwright`: Required for browser role-flow verification.
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Behavioral e2e, not design work.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 5, 7, 9, 10, 11

  **References**:
  - `apps/admin/e2e/admin.spec.ts`
  - `apps/admin/playwright.config.ts`
  - Seeded credentials from repo runbook/seed data

  **Acceptance Criteria**:
  - [ ] Admin users/tasks behavior covered.
  - [ ] Manager users subtree visibility and task creation behavior covered.
  - [ ] Employee restricted users behavior covered.

  **QA Scenarios**:
  ```
  Scenario: Playwright RBAC role flows pass
    Tool: Bash (Playwright)
    Preconditions: Backend and frontend test servers available.
    Steps:
      1. Run targeted Playwright spec(s).
      2. Confirm separate assertions for admin, manager, employee.
    Expected Result: All role-flow scenarios pass.
    Failure Indicators: Missing manager subtree assertion or employee restriction check.
    Evidence: .omo/evidence/task-13-playwright-rbac.txt
  ```

  **Commit**: YES
  - Message: `test(e2e): cover rbac role flows`

- [x] 14. Add direct API verification for role-based access

  **What to do**:
  - Script or document direct API checks using seeded/admin-manager-employee auth tokens.
  - Verify users/tasks endpoints return exact expected status and scoped data.

  **Must NOT do**:
  - Do not leave API verification implicit behind UI-only tests.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small direct API verification task.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Direct HTTP verification is simpler here.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 5, 7

  **References**:
  - `app/presentation/api/v1/users.py`
  - `app/presentation/api/v1/tasks.py`
  - Auth login endpoint and seed credentials

  **Acceptance Criteria**:
  - [ ] API checks prove admin, manager, employee users access behavior.
  - [ ] API checks prove manager task create behavior if backend allows it.

  **QA Scenarios**:
  ```
  Scenario: Direct API role checks return expected status/data
    Tool: Bash (curl)
    Preconditions: Tokens for admin, manager, employee available.
    Steps:
      1. Call users list endpoint as admin, manager, employee.
      2. Call task create endpoint as manager with valid payload.
      3. Call at least one forbidden endpoint as employee.
    Expected Result: Status codes and response shapes match the role matrix exactly.
    Failure Indicators: Manager denied incorrectly, employee over-authorized, or scope leakage in returned data.
    Evidence: .omo/evidence/task-14-api-role-checks.json
  ```

  **Commit**: NO

- [x] 15. Run regression and resolve residual alignment defects

  **What to do**:
  - Run backend tests, frontend unit tests, Playwright e2e, and build checks.
  - Fix any remaining RBAC mismatches or test regressions discovered by prior tasks.
  - Re-run until the targeted role matrix is green.

  **Must NOT do**:
  - Do not merge unresolved role mismatch findings into “known issue” without explicit approval.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Integration/debugging across backend and frontend.
  - **Skills**: [`playwright`]
    - `playwright`: Needed for end-to-end re-verification when debugging UI flows.
  - **Skills Evaluated but Omitted**:
    - `debugging`: Only escalate if regressions become non-trivial.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential integration
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 6, 9, 10, 11, 12, 13, 14

  **References**:
  - All test files and touched implementation files from Tasks 5-14
  - `apps/admin/README.md` - Local run/test guidance if needed

  **Acceptance Criteria**:
  - [ ] `pytest` passes for touched backend areas.
  - [ ] `npm run test:unit` passes in `apps/admin`.
  - [ ] `npm run e2e` passes in `apps/admin`.
  - [ ] `npm run build` passes in `apps/admin`.

  **QA Scenarios**:
  ```
  Scenario: Full regression suite passes
    Tool: Bash
    Preconditions: All implementation and tests complete.
    Steps:
      1. Run backend tests.
      2. Run frontend unit tests.
      3. Run Playwright e2e.
      4. Run production build.
    Expected Result: All commands exit 0.
    Failure Indicators: Any non-zero exit, flaky manager/employee flow, or build regression.
    Evidence: .omo/evidence/task-15-full-regression.txt
  ```

  **Commit**: YES
  - Message: `fix(rbac): align frontend and backend behavior`

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end and verify all Must Have / Must NOT Have items are reflected in the implementation and evidence.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run backend/frontend quality gates and inspect changed files for permission drift, dead conditions, and unauthorized scope broadening.

- [x] F3. **Real QA Execution** — `unspecified-high`
  Execute all backend/API/frontend/e2e scenarios for admin, manager, and employee.

- [x] F4. **Scope Fidelity Check** — `deep`
  Confirm only in-scope RBAC alignment work was changed and no broad role model redesign slipped in.

---

## Commit Strategy

- Group backend RBAC scope fixes separately from frontend gating updates if commit boundaries remain clean.
- Ensure each commit has matching test coverage and verification commands.

---

## Success Criteria

### Verification Commands
```bash
pytest
cd apps/admin && npm run test:unit
cd apps/admin && npm run e2e
cd apps/admin && npm run build
```

### Final Checklist
- [ ] Manager can view users in department subtree only
- [ ] Employee self-only users behavior is enforced
- [ ] Frontend users/tasks gating mirrors backend source of truth
- [ ] Targeted permission-name mismatches are resolved consistently
- [ ] Automated backend/frontend/e2e verification passes
