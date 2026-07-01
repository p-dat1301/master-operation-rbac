# Backend Remaining API Timezone Standardization

## TL;DR

> **Quick Summary**: Standardize the remaining backend API timestamp behavior to explicit UTC-aware datetimes while preserving date-only business fields and reusing the already-proven patterns from attendance, tasks, notifications, audit logs, leaves, and leave-balances.
>
> **Deliverables**:
> - UTC-aware persistence and serialization plan for remaining backend API groups
> - Phased execution waves with per-API verification
> - Explicit migration, regression, and scope-control guardrails
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves + final verification
> **Critical Path**: 1 → 5 → 9 → 12 → F1-F4

---

## Context

### Original Request
Lên plan chi tiết để chuẩn hóa các API backend còn lại về xử lý thời gian/timezone sau khi các nhóm attendance, tasks, notifications, audit logs, leaves, và leave-balances đã được cập nhật và kiểm thử.

### Interview Summary
**Key Discussions**:
- Các API chính đã làm xong trước đó: attendance, tasks, notifications, audit logs, leaves, leave-balances.
- Phần còn lại cần chuẩn hóa gồm: users, roles, permissions, departments, menu sync, i18n sync.
- Chính sách mục tiêu: timestamp biểu diễn “instant” phải là UTC-aware; field business kiểu ngày phải tiếp tục là `date`.
- Mỗi nhóm API phải được kiểm thử ngay sau khi sửa xong.

**Research Findings**:
- Các model còn timestamp chưa explicit timezone sau các phase trước:
  - `app/infrastructure/database/models/role_model.py`
  - `app/infrastructure/database/models/menu_model.py`
  - `app/infrastructure/database/models/user_model.py`
  - `app/infrastructure/database/models/translation_model.py`
  - `app/infrastructure/database/models/department_model.py`
  - `app/infrastructure/database/models/permission_model.py`
- Branch hiện có blast radius cao do đã có nhiều thay đổi liên quan contract/timestamp từ các phase trước.
- Pattern tốt đã tồn tại trong codebase: attendance và các phase đã hoàn tất dùng UTC-aware timestamps và normalize repository output.

### Metis Review
**Identified Gaps** (addressed):
- Khóa chặt scope để không lan sang frontend hoặc các API đã sửa xong.
- Bắt buộc bảo toàn field `date` không biến thành `datetime`.
- Biến migration/backfill thành task/guardrail rõ ràng thay vì giả định ngầm.
- Yêu cầu verification rõ ràng sau từng nhóm API.

---

## Work Objectives

### Core Objective
Chuẩn hóa toàn bộ các API backend còn lại để mọi timestamp biểu diễn thời điểm thực (`created_at`, `updated_at`, và các trường tương tự) được lưu trữ/xử lý/trả về theo UTC-aware semantics nhất quán, trong khi mọi field business dạng ngày vẫn giữ nguyên semantics `date`.

### Concrete Deliverables
- Chuẩn hóa timezone cho nhóm users / roles / permissions / departments.
- Chuẩn hóa timezone cho nhóm menu sync / i18n sync.
- Kế hoạch migration/verification để bảo đảm DB model, repository, schema, và API response không lệch nhau.
- Ma trận kiểm thử theo từng phase API.

### Definition of Done
- [ ] Mọi model timestamp còn lại trong scope đều dùng explicit timezone-aware strategy.
- [ ] Mọi repository/serialization path thuộc scope trả timestamp UTC nhất quán.
- [ ] Mỗi nhóm API trong scope đều có diagnostics, compile, và live smoke test pass.
- [ ] `gitnexus_detect_changes()` cuối cùng chỉ ra blast radius phù hợp với scope còn lại.

### Must Have
- UTC-aware policy cho instant timestamps.
- Preserve `date`-only fields.
- Impact analysis trước mỗi chỉnh sửa symbol/route chính.
- Kiểm thử ngay sau mỗi nhóm API.
- Không làm lan scope sang frontend.

### Must NOT Have (Guardrails)
- Không sửa lại các API đã hoàn tất trừ khi shared helper bắt buộc.
- Không biến `hire_date` hay các field business date-only khác thành datetime.
- Không mở rộng thành global repo-wide datetime refactor.
- Không backfill dữ liệu lịch sử ngoài kế hoạch explicit.
- Không đổi response contract bằng cách thêm field timestamp mới nếu không cần.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: Existing backend diagnostics/compile + targeted live API smoke tests
- **If TDD**: Not selected for this plan; tests follow implementation per phase

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence/logs should be captured from diagnostics, compile output, and HTTP smoke results.

- **Backend/API**: Use Bash with `curl` or scripted HTTP client.
- **Static Verification**: Use `lsp_diagnostics` and `python -m compileall`.
- **Impact Verification**: Use `gitnexus_impact`, `gitnexus_api_impact` where route handlers change, and `gitnexus_detect_changes` before final handoff.
- **Timestamp Assertions**:
  - Instant timestamps must parse as ISO-8601 UTC (`Z` or `+00:00`, matching established backend output).
  - Date-only fields must remain `YYYY-MM-DD` with no time component.

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.

```
Wave 1 (Start Immediately - scope lock + shared verification foundation):
├── Task 1: Timestamp contract inventory + route/model map [quick]
├── Task 2: Migration/backfill decision scaffold [writing]
├── Task 3: Shared UTC verification checklist and smoke payload set [quick]
└── Task 4: API impact pre-check for user/RBAC/menu/i18n routes [quick]

Wave 2 (After Wave 1 - RBAC + people APIs):
├── Task 5: Users timestamp persistence + serialization [unspecified-high]
├── Task 6: Roles timestamp persistence + serialization [quick]
├── Task 7: Permissions timestamp persistence + serialization [quick]
└── Task 8: Departments timestamp persistence + serialization [quick]

Wave 3 (After Wave 2 - sync/admin metadata APIs, sequential by dependency):
├── Task 9: Menu sync timestamp persistence + serialization [unspecified-high]
├── Task 10: I18n sync timestamp persistence + serialization [unspecified-high]
└── Task 11: Shared regression sweep for cross-cutting UTC behavior [deep]

Wave 4 (After Wave 3 - integration + migration alignment, sequential by dependency):
├── Task 12: Alembic/schema alignment for remaining timestamp columns [deep]
├── Task 13: End-to-end backend smoke matrix for remaining APIs [unspecified-high]
└── Task 14: Branch scope/risk reconciliation with GitNexus [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA execution of plan scenarios (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: 1 → 5 → 9 → 12 → F1-F4
Parallel Speedup: ~55% faster than strict sequential
Max Concurrent: 4
```

### Dependency Matrix
- **1**: - - 4, 5-10, 11, 1
- **2**: - - 12, 2
- **3**: - - 13, 1
- **4**: 1 - 5-10, 1
- **5**: 1, 4 - 11, 13, 2
- **6**: 1, 4 - 11, 13, 2
- **7**: 1, 4 - 11, 13, 2
- **8**: 1, 4 - 11, 13, 2
- **9**: 1, 4, 5-8 - 11, 13, 3
- **10**: 1, 4, 5-8 - 11, 13, 3
- **11**: 5-10 - 12, 13, 3
- **12**: 2, 11 - 14, 4
- **13**: 3, 5-12 - 14, 4
- **14**: 12, 13 - F1-F4, 4

### Agent Dispatch Summary
- **1**: **4** - 1 → `quick`, 2 → `writing`, 3 → `quick`, 4 → `quick`
- **2**: **4** - 5 → `unspecified-high`, 6 → `quick`, 7 → `quick`, 8 → `quick`
- **3**: **3** - 9 → `unspecified-high`, 10 → `unspecified-high`, 11 → `deep`
- **4**: **3** - 12 → `deep`, 13 → `unspecified-high`, 14 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. Inventory remaining backend timezone contracts across users, roles, permissions, departments, menu sync, and i18n sync

  **What to do**:
  - Read the remaining API routes, DTOs, schemas, entities, models, and repositories to confirm exactly where instant timestamps are created, stored, and serialized.
  - Build a file-level map of every remaining `created_at`, `updated_at`, `last_*_at`, or equivalent instant timestamp field in scope.
  - Confirm which fields are date-only and must remain `date`.

  **Must NOT do**:
  - Do not edit code in this task.
  - Do not expand scope to already-completed APIs unless a shared symbol forces it.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is discovery and mapping only, with no code changes.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Needed to map the codebase execution flows and current time-related patterns.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Not needed because this task is inspection only.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Tasks 5-13
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `app/presentation/api/v1/tasks.py` - Example of timestamp-bearing API response flow already stabilized.
  - `app/presentation/api/v1/leaves.py` - Example of date-only business fields plus UTC timestamp metadata.
  - `app/presentation/api/v1/attendance.py` - Existing UTC-aware implementation pattern to mirror.

  **API/Type References** (contracts to implement against):
  - `app/presentation/schemas/user_schema.py:UserResponse` - User API response contract.
  - `app/presentation/schemas/task_schema.py:TaskResponse` - Reference for existing timestamp serialization style.
  - `app/presentation/schemas/leave_schema.py:LeaveResponse` - Reference for date-only vs timestamp split.

  **Test References** (testing patterns to follow):
  - `tests/integration/test_rbac_scenarios.py` - Existing API integration style and auth setup.
  - `scripts/run_api_tests.py` - Existing smoke-test payload conventions.

  **External References**:
  - None required.

  **WHY Each Reference Matters**:
  - `tasks.py`, `leaves.py`, `attendance.py`: show the already-proven time contract pattern to copy.
  - `UserResponse`, `TaskResponse`, `LeaveResponse`: define what the API currently exposes and where timestamp fields appear.
  - `test_rbac_scenarios.py`, `run_api_tests.py`: provide test style and payload shape for the remaining smoke tests.

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  - [ ] Inventory document (in agent output) lists all remaining timestamp-bearing models/routes in scope.
  - [ ] Date-only fields are explicitly separated from instant timestamps.
  - [ ] No code files are modified.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Map remaining API time contracts
    Tool: Bash (read/search)
    Preconditions: Repository checked out at current branch.
    Steps:
      1. Search remaining backend files for timestamp fields and datetime constructors.
      2. Inspect the matching route/schema/model/repository files.
      3. Record the file paths and timestamp semantics.
    Expected Result: A complete file-level inventory of remaining backend time contracts.
    Failure Indicators: Missing route/model pairings or accidental inclusion of already-completed APIs.
    Evidence: .omo/evidence/task-1-time-contract-inventory.txt

  Scenario: Confirm date-only fields remain date-only
    Tool: Bash (read/search)
    Preconditions: Same repository state.
    Steps:
      1. Inspect user, leave, and task contracts for date-only fields.
      2. Confirm they are typed as `date`, not `datetime`.
      3. Capture the exact fields that must not be changed.
    Expected Result: Date-only fields are explicitly documented and remain untouched.
    Evidence: .omo/evidence/task-1-date-only-inventory.txt
  ```

  **Evidence to Capture**:
  - [ ] Inventory notes saved in agent output or evidence file.
  - [ ] Search output showing matched files.

  **Commit**: NO

- [ ] 2. Decide and document migration/backfill policy for remaining timestamp columns

  **What to do**:
  - Determine whether remaining models need schema migrations, data backfill, or read-side normalization only.
  - Define the canonical UTC response format (`Z` or `+00:00`) used for the rest of the plan.
  - Write the migration/backfill decision into the plan so later tasks follow the same rule.

  **Must NOT do**:
  - Do not touch application code in this task.
  - Do not introduce a new timezone abstraction.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `writing`
    - Reason: This task produces policy/decision text for the plan.
  - **Skills**: [`gitnexus-guide`]
    - `gitnexus-guide`: Helpful for understanding the code intelligence workflow and how to reference plan decisions.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: Not needed until actual symbols are edited.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Tasks 5-13
  - **Blocked By**: None (can start immediately)

  **References**:
  - `alembic/versions/*` - Existing migration style and schema-change patterns.
  - `app/infrastructure/database/models/attendance_model.py` - Reference for timezone-aware column declaration.
  - `app/infrastructure/database/repositories/sqlalchemy_attendance_repo.py` - Reference for UTC normalization rules.

  **Why they matter**:
  - They anchor the migration/backfill decision to concrete repo patterns already proven in earlier phases.

  **Acceptance Criteria**:
  - [ ] Canonical timezone format is explicitly recorded in the plan.
  - [ ] Migration/backfill policy is explicit (migrate, normalize on read, or code-only).
  - [ ] No code files are modified.

  **QA Scenarios**:
  ```
  Scenario: Record migration policy
    Tool: Bash (write/read plan only)
    Preconditions: Plan file exists.
    Steps:
      1. Add the migration/backfill decision section to the plan.
      2. Verify the section states the canonical UTC response format and data policy.
    Expected Result: The plan contains a single explicit policy for the remaining APIs.
    Evidence: .omo/evidence/task-2-policy-text.txt

  Scenario: Verify no code changes
    Tool: git status
    Preconditions: Same working tree.
    Steps:
      1. Inspect the working tree after this task.
      2. Confirm only the plan/draft changed.
    Expected Result: No source-code file modified by this task.
    Evidence: .omo/evidence/task-2-git-status.txt
  ```

  **Commit**: NO

- [ ] 3. Define shared smoke-test matrix and UTC assertion helpers for remaining APIs

  **What to do**:
  - Specify the exact smoke-test payloads and expected UTC assertions for each remaining API group.
  - Reuse the same assertion style used in earlier phases so tests stay consistent.
  - Capture happy-path and failure/edge-case checks for each endpoint group.

  **Must NOT do**:
  - Do not implement test code yet.
  - Do not change application files.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This is test-planning and checklist drafting only.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Needed to understand existing smoke-test patterns and payloads.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Not relevant to planning tests.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Tasks 5-13
  - **Blocked By**: None

  **References**:
  - `scripts/run_api_tests.py` - Existing smoke-test payload and date helper patterns.
  - `tests/integration/test_rbac_scenarios.py` - Existing authenticated API test setup.
  - `app/presentation/api/v1/attendance.py` - Pattern for precise timestamp assertions.

  **Acceptance Criteria**:
  - [ ] A smoke-test matrix exists in the plan for every remaining API group.
  - [ ] Each matrix entry includes a happy path and an edge/failure case.
  - [ ] Each assertion states the exact UTC/date format expected.

  **QA Scenarios**:
  ```
  Scenario: Draft smoke-test matrix
    Tool: Bash (plan edit only)
    Preconditions: Plan file exists.
    Steps:
      1. Add endpoint-by-endpoint assertions to the plan.
      2. Verify each remaining API group has happy-path and edge-case checks.
    Expected Result: A complete smoke-test matrix is documented.
    Evidence: .omo/evidence/task-3-smoke-matrix.txt
  ```

  **Commit**: NO

- [ ] 4. Run GitNexus impact analysis for remaining route handlers and timestamp models before edits

  **What to do**:
  - Analyze impact for the remaining model classes and route handlers that will be modified in later waves.
  - Call out direct callers/importers and any medium/high risk areas in the plan.
  - Note which route handlers require extra caution before edits.

  **Must NOT do**:
  - Do not edit source files.
  - Do not skip any high-risk symbol.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: This task is impact analysis and documentation.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required to evaluate blast radius before code changes.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No edits yet.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Tasks 5-13
  - **Blocked By**: None

  **References**:
  - Remaining model files in scope (`role_model.py`, `menu_model.py`, `user_model.py`, `translation_model.py`, `department_model.py`, `permission_model.py`).
  - Remaining route handlers in scope (`users.py`, `roles.py`, `permissions.py`, `departments.py`, `menu_sync.py`, `i18n_sync.py`).

  **Acceptance Criteria**:
  - [ ] Impact findings for every remaining symbol/route are reflected in the plan.
  - [ ] High/critical risks are clearly marked.
  - [ ] No code files are modified.

  **QA Scenarios**:
  ```
  Scenario: Document impact findings
    Tool: GitNexus impact
    Preconditions: Repository indexed and available.
    Steps:
      1. Run impact analysis on the remaining model symbols.
      2. Record direct callers and risk levels.
    Expected Result: Plan includes a clear blast-radius summary for remaining APIs.
    Evidence: .omo/evidence/task-4-impact-summary.txt
  ```

  **Commit**: NO

- [ ] 5. Standardize Users API timestamp handling while preserving user date-only fields

  **What to do**:
  - Update `UserModel.created_at` and any exposed user instant timestamp fields to the chosen timezone-aware strategy.
  - Add repository read normalization only for fields exposed or consumed by user APIs.
  - Keep `hire_date` as a date-only field.
  - Run diagnostics, compile, and live smoke tests for user endpoints before moving on.

  **Must NOT do**:
  - Do not change password/auth token logic.
  - Do not convert `hire_date` to datetime.
  - Do not alter role/permission relationship loading behavior.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: User model has wider fan-out and touches auth/RBAC-adjacent paths.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before modifying a medium-risk shared model.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Not needed unless tests fail.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8)
  - **Blocks**: Tasks 9, 10, 11, 13
  - **Blocked By**: Tasks 1, 4

  **References**:
  - `app/infrastructure/database/models/user_model.py:UserModel.created_at` - Timestamp column to standardize.
  - `app/infrastructure/database/repositories/sqlalchemy_user_repo.py:SQLAlchemyUserRepository._to_entity()` - User mapping path; avoid breaking eager role/permission loading.
  - `app/presentation/api/v1/users.py` - User API route behavior to smoke test.
  - `app/presentation/schemas/user_schema.py:UserResponse` - User response contract.

  **Acceptance Criteria**:
  - [ ] `created_at` or equivalent user instant timestamps use the approved UTC-aware strategy if exposed or persisted.
  - [ ] `hire_date` remains date-only and serializes as `YYYY-MM-DD` when present.
  - [ ] User list/detail/create/update smoke tests pass.
  - [ ] Role/permission relationship fields still appear correctly.

  **QA Scenarios**:
  ```
  Scenario: Users API happy path preserves relationships and UTC timestamps
    Tool: Bash (HTTP client)
    Preconditions: API server running on 127.0.0.1:8010; admin credentials available.
    Steps:
      1. Login with admin@company.vn / Admin@123 (see `tests/integration/conftest.py:18-24`).
      2. GET /api/v1/users/ with bearer token.
      3. Assert HTTP 200.
      4. Assert user identity fields and permissions/role data remain present.
      5. If timestamp fields are returned, assert they are UTC-explicit.
    Expected Result: Users API returns valid data with no timezone-naive timestamps.
    Evidence: .omo/evidence/task-5-users-list.json

  Scenario: User date-only field remains date-only
    Tool: Bash (HTTP client)
    Preconditions: User create/update endpoint available with a test payload using hire_date "2026-01-15".
    Steps:
      1. Create or update a test user with hire_date "2026-01-15".
      2. Fetch the user back.
      3. Assert hire_date equals "2026-01-15" and does not contain "T".
    Expected Result: Date-only user fields remain pure date strings.
    Evidence: .omo/evidence/task-5-users-date-only.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize user timestamp handling`
  - Files: user model/repository/schema/test files only
  - Pre-commit: diagnostics + compile + user API smoke

- [ ] 6. Standardize Roles API timestamp handling

  **What to do**:
  - Update role timestamp persistence and any role response serialization paths to UTC-aware behavior.
  - Verify role-permission associations remain unchanged.
  - Test role list/detail/mutation if supported.

  **Must NOT do**:
  - Do not change permission assignment semantics.
  - Do not alter RBAC checks.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Small model/API group with clear timestamp-only scope.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before modifying role model/route symbols.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: No broad refactor expected.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7, 8)
  - **Blocks**: Tasks 9, 11, 13
  - **Blocked By**: Tasks 1, 4

  **References**:
  - `app/infrastructure/database/models/role_model.py` - Role timestamp model.
  - `app/presentation/api/v1/roles.py` - Role API behavior.
  - `app/infrastructure/database/repositories/sqlalchemy_role_repo.py` - Role persistence mapping.
  - `app/presentation/schemas/role_schema.py` - Role response contract.

  **Acceptance Criteria**:
  - [ ] Role instant timestamps use UTC-aware handling.
  - [ ] Role permissions remain unchanged after timestamp update.
  - [ ] Role API smoke tests pass.

  **QA Scenarios**:
  ```
  Scenario: Roles API list remains stable
    Tool: Bash (HTTP client)
    Preconditions: API server running and admin token available.
    Steps:
      1. GET /api/v1/roles/.
      2. Assert HTTP 200.
      3. Assert role names/permissions still serialize.
      4. If created_at is returned, assert it is UTC-explicit.
    Expected Result: Roles API behavior unchanged except UTC-safe timestamps.
    Evidence: .omo/evidence/task-6-roles-list.json

  Scenario: Role permission associations are unchanged
    Tool: Bash (HTTP client)
    Preconditions: Existing seeded roles with permissions.
    Steps:
      1. Fetch roles before and after the change.
      2. Compare role permission keys for seeded roles `admin` and `manager` from `app/infrastructure/database/seed.py:31-53`.
    Expected Result: Permission associations are not altered by timestamp work.
    Evidence: .omo/evidence/task-6-role-permissions.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize role timestamp handling`
  - Files: role model/repository/schema/test files only
  - Pre-commit: diagnostics + compile + role API smoke

- [ ] 7. Standardize Permissions API timestamp handling

  **What to do**:
  - Update permission model timestamp columns and repository/schema serialization if returned.
  - Verify permission code/name/action fields are unchanged.
  - Run permissions API smoke test.

  **Must NOT do**:
  - Do not rename permissions.
  - Do not modify RBAC policy decisions.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Focused timestamp-only change.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before modifying permission model or handlers.
  - **Skills Evaluated but Omitted**:
    - `security-research`: Not needed because this is not a security audit.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 8)
  - **Blocks**: Tasks 9, 11, 13
  - **Blocked By**: Tasks 1, 4

  **References**:
  - `app/infrastructure/database/models/permission_model.py` - Permission timestamp model.
  - `app/infrastructure/database/repositories/sqlalchemy_permission_repo.py` - Permission mapping.
  - `app/presentation/api/v1/permissions.py` - Permissions route behavior.
  - `app/presentation/schemas/permission_schema.py` - API schema contract.

  **Acceptance Criteria**:
  - [ ] Permission instant timestamps use UTC-aware handling.
  - [ ] Permission identifiers and RBAC behavior remain unchanged.
  - [ ] Permissions API smoke tests pass.

  **QA Scenarios**:
  ```
  Scenario: Permissions API list remains stable
    Tool: Bash (HTTP client)
    Preconditions: API server running and admin token available.
    Steps:
      1. GET /api/v1/permissions/.
      2. Assert HTTP 200.
      3. Assert known permission codes are present.
      4. If timestamp fields are returned, assert they are UTC-explicit.
    Expected Result: Permissions API returns the same permission business fields with UTC-safe timestamps.
    Evidence: .omo/evidence/task-7-permissions-list.json

  Scenario: Unauthorized permission access still fails
    Tool: Bash (HTTP client)
    Preconditions: Non-admin token available.
    Steps:
      1. Call a restricted permissions endpoint with employee token.
      2. Assert the same expected forbidden/unauthorized status as before.
    Expected Result: Timestamp work does not weaken RBAC behavior.
    Evidence: .omo/evidence/task-7-permissions-rbac-error.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize permission timestamp handling`
  - Files: permission model/repository/schema/test files only
  - Pre-commit: diagnostics + compile + permissions API smoke

- [ ] 8. Standardize Departments API timestamp handling

  **What to do**:
  - Update department timestamp persistence and serialization to the UTC-aware pattern.
  - Verify department hierarchy/manager fields are unaffected.
  - Run departments API smoke test.

  **Must NOT do**:
  - Do not alter department hierarchy or manager assignment semantics.
  - Do not touch user relationship logic beyond timestamp needs.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Focused model/API timestamp standardization.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before modifying department model/route symbols.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Only needed if smoke tests fail.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7)
  - **Blocks**: Tasks 11, 13
  - **Blocked By**: Tasks 1, 4

  **References**:
  - `app/infrastructure/database/models/department_model.py` - Department timestamp model.
  - `app/infrastructure/database/repositories/sqlalchemy_department_repo.py` - Department persistence mapping.
  - `app/presentation/api/v1/departments.py` - Department route behavior.

  **Acceptance Criteria**:
  - [ ] Department instant timestamps use UTC-aware handling.
  - [ ] Department hierarchy fields remain unchanged.
  - [ ] Departments API smoke tests pass.

  **QA Scenarios**:
  ```
  Scenario: Departments API list remains stable
    Tool: Bash (HTTP client)
    Preconditions: API server running and admin token available.
    Steps:
      1. GET /api/v1/departments/.
      2. Assert HTTP 200.
      3. Assert department identity/hierarchy fields remain present.
      4. If timestamp fields are returned, assert they are UTC-explicit.
    Expected Result: Departments API remains stable with UTC-safe timestamp behavior.
    Evidence: .omo/evidence/task-8-departments-list.json

  Scenario: Department date/time null handling
    Tool: Bash (HTTP client)
    Preconditions: Existing department without optional timestamp fields.
    Steps:
      1. Fetch departments.
      2. Assert optional timestamp fields remain null when absent.
    Expected Result: Null timestamp fields are not replaced with current time.
    Evidence: .omo/evidence/task-8-departments-null-timestamps.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize department timestamp handling`
  - Files: department model/repository/schema/test files only
  - Pre-commit: diagnostics + compile + departments API smoke

- [ ] 9. Standardize Menu Sync API timestamp handling and persistence

  **What to do**:
  - Update `menu_model.py` timestamps and any repository/service path that reads/writes menu sync metadata.
  - Verify sync result payloads and persisted menu rows follow the UTC-aware pattern.
  - Smoke test menu sync trigger and follow-up reads.

  **Must NOT do**:
  - Do not change menu hierarchy, routing keys, order, or permission bindings.
  - Do not alter sync semantics beyond timestamp behavior.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Sync flows can touch multiple rows and indirect persistence paths.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before editing sync-related models and routes.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Not needed unless the sync path is structurally broken.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Tasks 1, 4, 5-8
  - **Blocks**: Tasks 10, 11, 12, 13
  - **Blocked By**: Tasks 1, 4, 5-8

  **References**:
  - `app/infrastructure/database/models/menu_model.py` - Menu timestamp columns.
  - `app/presentation/api/v1/menu_sync.py` - Menu sync route behavior.
  - `app/di/menu_sync.py` and any sync repository/service files - Wiring and persistence path.

  **Acceptance Criteria**:
  - [ ] Menu sync persistence timestamps use UTC-aware handling.
  - [ ] Menu hierarchy/order/permission fields are unchanged.
  - [ ] Menu sync API smoke tests pass.

  **QA Scenarios**:
  ```
  Scenario: Menu sync happy path
    Tool: Bash (HTTP client)
    Preconditions: API server running and admin token available; capture the current menu list from `GET /api/v1/admin/config/menu` or the closest existing menu listing route in the codebase before sync.
    Steps:
      1. Trigger `POST /api/v1/admin/config/menu/sync` with the normal supported request.
      2. Assert HTTP success status.
      3. Fetch menu data or sync result payload.
      4. Assert any returned timestamps are UTC-explicit.
    Expected Result: Sync succeeds and timestamps are UTC-safe without changing menu semantics.
    Evidence: .omo/evidence/task-9-menu-sync.json

  Scenario: Menu hierarchy remains intact after sync
    Tool: Bash (HTTP client)
    Preconditions: API server running and menu data discoverable via the backend before sync.
    Steps:
      1. Capture menu hierarchy before sync using the live menu list exposed by the backend and the route wiring from `app/presentation/api/v1/menu_sync.py:14-31`.
      2. Run sync.
      3. Capture hierarchy after sync.
      4. Assert keys/parents/order are unchanged except intended sync updates.
    Expected Result: Timestamp work does not corrupt menu structure.
    Evidence: .omo/evidence/task-9-menu-hierarchy-compare.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize menu sync timestamps`
  - Files: menu model/repository/sync route files only
  - Pre-commit: diagnostics + compile + menu sync smoke

- [ ] 10. Standardize I18n Sync API timestamp handling and persistence

  **What to do**:
  - Update `translation_model.py` timestamps and the translation sync persistence path.
  - Verify locale/key/value fields remain unchanged while timestamps become UTC-aware.
  - Smoke test i18n sync and follow-up reads.

  **Must NOT do**:
  - Do not change translation content semantics.
  - Do not rewrite unrelated i18n import/export logic.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Sync flows may touch many translation rows and need careful regression testing.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Required before changing translation sync paths.
  - **Skills Evaluated but Omitted**:
    - `writing`: Not sufficient because this is implementation planning with behavior constraints.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Task 9 and before Task 11
  - **Blocks**: Tasks 11, 12, 13
  - **Blocked By**: Tasks 1, 4, 5-8, 9

  **References**:
  - `app/infrastructure/database/models/translation_model.py` - Translation timestamp columns.
  - `app/presentation/api/v1/i18n_sync.py` - I18n sync route behavior.
  - `app/infrastructure/database/repositories/sqlalchemy_translation_repo.py` - Translation persistence mapping.
  - `app/presentation/schemas/i18n_sync_schema.py` - Sync response/request contract.

  **Acceptance Criteria**:
  - [ ] Translation sync timestamps use UTC-aware handling.
  - [ ] Locale/key/value semantics remain unchanged.
  - [ ] I18n sync API smoke tests pass.

  **QA Scenarios**:
  ```
  Scenario: I18n sync happy path
    Tool: Bash (HTTP client)
    Preconditions: API server running and admin token available; capture the current translation list or keys from the closest existing translation/i18n listing route before sync.
    Steps:
      1. Trigger `POST /api/v1/admin/config/i18n/sync` with a known safe payload or default sync request.
      2. Assert HTTP success status.
      3. Fetch synced translation data if the API exposes it.
      4. Assert any instant timestamps are UTC-explicit.
    Expected Result: I18n sync succeeds with UTC-safe timestamps.
    Evidence: .omo/evidence/task-10-i18n-sync.json

  Scenario: Translation content remains unchanged except intended sync updates
    Tool: Bash (HTTP client)
    Preconditions: API server running and at least one translation key discoverable via the backend before sync.
    Steps:
      1. Capture locale/key/value before sync using the live translation list exposed by the backend and the sync route in `app/presentation/api/v1/i18n_sync.py:14-31`.
      2. Run sync.
      3. Capture locale/key/value after sync.
      4. Assert values only change if the sync payload intends it.
    Expected Result: Timestamp work does not mutate translation content unexpectedly.
    Evidence: .omo/evidence/task-10-i18n-content-compare.json
  ```

  **Commit**: YES
  - Message: `fix(api): standardize i18n sync timestamps`
  - Files: translation model/repository/i18n sync route files only
  - Pre-commit: diagnostics + compile + i18n sync smoke

- [ ] 11. Run a shared regression sweep for UTC behavior across all remaining API groups

  **What to do**:
  - Re-run list/detail/mutation smoke tests across users, roles, permissions, departments, menu sync, and i18n sync after Waves 2-3 complete.
  - Verify UTC timestamps serialize consistently and date-only fields remain date-only.
  - Look specifically for any aware/naive comparison failures.

  **Must NOT do**:
  - Do not add unrelated feature work.
  - Do not skip negative scenarios.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: This is a cross-cutting regression sweep across multiple API groups.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Helps map all changed flows and confirm which endpoints to sweep.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: This task verifies, not restructures.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Tasks 9-10
  - **Blocks**: Tasks 12, 13
  - **Blocked By**: Tasks 5-10

  **References**:
  - All route/schema/model/repository files touched in Tasks 5-10.
  - `scripts/run_api_tests.py` - Existing smoke script style.

  **Acceptance Criteria**:
  - [ ] All remaining API groups have at least one passing happy-path smoke test.
  - [ ] All negative/date-only checks pass.
  - [ ] No aware/naive runtime errors occur.

  **QA Scenarios**:
  ```
  Scenario: Cross-group UTC regression sweep
    Tool: Bash (HTTP client)
    Preconditions: API server running with test credentials.
    Steps:
      1. Run the documented smoke requests for users, roles, permissions, departments, menu sync, and i18n sync.
      2. Parse responses and inspect timestamp fields.
      3. Assert instant timestamps are UTC-explicit and date-only fields contain no time component.
    Expected Result: All remaining API groups follow the same time contract.
    Evidence: .omo/evidence/task-11-cross-group-regression.json

  Scenario: No naive/aware comparison failures
    Tool: Bash (server log + HTTP client)
    Preconditions: Same API server.
    Steps:
      1. Execute endpoints that create/update and then read back data.
      2. Inspect responses and server log output for TypeError or datetime comparison failures.
    Expected Result: No runtime errors related to mixing aware and naive datetimes.
    Evidence: .omo/evidence/task-11-runtime-log.txt
  ```

  **Commit**: NO

- [ ] 12. Align Alembic/schema changes for the remaining timestamp columns

  **What to do**:
  - Create or update the migration plan needed to keep DB schema aligned with the remaining model changes.
  - Ensure the migration strategy matches the policy from Task 2.
  - Verify migration commands against the project’s current Alembic setup.

  **Must NOT do**:
  - Do not silently backfill historical data unless explicitly included.
  - Do not bundle unrelated schema changes.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: Schema alignment is high-impact and needs deliberate sequencing.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Helps constrain schema changes to the intended remaining models.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Not needed unless migration execution fails.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 2, 11

  **References**:
  - `alembic/env.py` - Migration environment wiring.
  - Existing timezone-related migration for attendance - pattern reference for schema alignment.
  - Remaining model files from Tasks 5-10.

  **Acceptance Criteria**:
  - [ ] Migration plan or migration files cover every remaining timestamp column changed in scope.
  - [ ] Migration scope is limited to planned models.
  - [ ] Alembic validation command or review passes.

  **QA Scenarios**:
  ```
  Scenario: Migration alignment review
    Tool: Bash (alembic commands)
    Preconditions: Alembic configured for local DB.
    Steps:
      1. Review or generate the migration for remaining timestamp columns.
      2. Run alembic validation command or inspect generated DDL.
      3. Confirm only intended columns are changed.
    Expected Result: Schema alignment is explicit and limited to plan scope.
    Evidence: .omo/evidence/task-12-migration-review.txt
  ```

  **Commit**: YES
  - Message: `fix(db): align remaining timezone-aware timestamp columns`
  - Files: alembic migration + intended models only
  - Pre-commit: alembic review + compile

- [ ] 13. Execute full remaining-backend smoke matrix and document results

  **What to do**:
  - Run the complete smoke matrix defined earlier against all remaining API groups.
  - Record the outputs and note any residual inconsistency.
  - Confirm the remaining scope is done before the final GitNexus sweep.

  **Must NOT do**:
  - Do not leave any API group untested.
  - Do not rely on manual inspection only.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: This is a full validation pass across all remaining APIs.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Helps ensure all intended endpoints are covered.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed because these are backend APIs, not browser UIs.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 3, 5-12

  **References**:
  - The smoke matrix from Task 3.
  - All remaining route handler files.
  - Existing auth credentials and local server pattern from previous phases.

  **Acceptance Criteria**:
  - [ ] Every remaining API group is exercised by at least one live smoke test.
  - [ ] UTC/date-only assertions pass everywhere in scope.
  - [ ] Results are recorded for handoff.

  **QA Scenarios**:
  ```
  Scenario: Full remaining API smoke matrix
    Tool: Bash (HTTP client)
    Preconditions: Local API server up and seeded credentials valid.
    Steps:
      1. Execute the planned requests for users, roles, permissions, departments, menu sync, and i18n sync.
      2. Capture status codes and response bodies.
      3. Assert all timestamp/date invariants.
    Expected Result: All remaining backend APIs pass the documented contract.
    Evidence: .omo/evidence/task-13-full-smoke-matrix.json
  ```

  **Commit**: NO

- [ ] 14. Reconcile branch scope and residual risks with GitNexus before handoff

  **What to do**:
  - Run `gitnexus_detect_changes()` and compare changed symbols/processes to the intended remaining API scope.
  - Document any extra touched symbols or residual risks.
  - Prepare the final execution notes for the final verification wave.

  **Must NOT do**:
  - Do not ignore HIGH or CRITICAL findings.
  - Do not declare completion if the diff includes unplanned spillover.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Final scope/risk review is focused and tool-driven.
  - **Skills**: [`gitnexus-impact-analysis`]
    - `gitnexus-impact-analysis`: Needed to interpret final blast radius and changed flows.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-pr-review`: Not needed unless preparing a PR review artifact.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 12, 13

  **References**:
  - `gitnexus_detect_changes()` output.
  - The scoped model and route list from Task 1.
  - The impact notes from Task 4.

  **Acceptance Criteria**:
  - [ ] Final change scope matches the planned remaining API/model area.
  - [ ] Residual risks are explicitly documented.
  - [ ] Any accidental spillover is identified before final review.

  **QA Scenarios**:
  ```
  Scenario: Final GitNexus scope check
    Tool: GitNexus detect_changes
    Preconditions: All planned code changes are present.
    Steps:
      1. Run detect_changes across the full working tree.
      2. Compare changed symbols and affected processes to the plan scope.
      3. Record any out-of-scope changes.
    Expected Result: Final diff is explainable and limited to the intended remaining API standardization work.
    Evidence: .omo/evidence/task-14-gitnexus-scope.txt
  ```

  **Commit**: NO

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit approval before completing execution.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify every Must Have / Must NOT Have against implementation and evidence.

  **Acceptance Criteria**:
  - [ ] Every Must Have is satisfied with evidence references.
  - [ ] Every Must NOT Have is absent from the diff.
  - [ ] Every task has corresponding evidence output.
  - [ ] Verdict is `APPROVE`.

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run diagnostics, compile, lint/tests if available, and inspect changed files for sloppy timezone handling or unintended refactors.

  **Acceptance Criteria**:
  - [ ] `python -m compileall` passes for all touched backend files.
  - [ ] `lsp_diagnostics` reports no new errors on touched files.
  - [ ] No new naive datetime writes are introduced in scoped files.
  - [ ] Verdict is `APPROVE`.

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute all API smoke scenarios for remaining backend groups and confirm UTC/date-only behavior.

  **Acceptance Criteria**:
  - [ ] Users API smoke scenarios pass.
  - [ ] Roles API smoke scenarios pass.
  - [ ] Permissions API smoke scenarios pass.
  - [ ] Departments API smoke scenarios pass.
  - [ ] Menu sync API smoke scenarios pass.
  - [ ] I18n sync API smoke scenarios pass.
  - [ ] All timestamp assertions are UTC-explicit and all date-only assertions remain date-only.
  - [ ] Verdict is `APPROVE`.

- [ ] F4. **Scope Fidelity Check** — `deep`
  Confirm final diff only contains planned timestamp/API scope and no frontend or unrelated business-logic creep.

  **Acceptance Criteria**:
  - [ ] Final `gitnexus_detect_changes()` output is reviewed.
  - [ ] Changed files match the planned remaining API/model scope or are explicitly justified.
  - [ ] No frontend changes are included for this plan.
  - [ ] No already-completed API group is modified except for approved shared utility/test reuse.
  - [ ] Verdict is `APPROVE`.

---

## Commit Strategy

- Group commits by wave/API group.
- Suggested pattern: `fix(api): standardize utc timestamps for <group>`
- Run `gitnexus_detect_changes()` before any commit.

---

## Success Criteria

### Verification Commands
```bash
python -m compileall <touched-files>   # Expected: all compiled successfully
# plus per-phase HTTP smoke scripts and GitNexus checks defined in tasks
```

### Final Checklist
- [ ] All remaining API groups in scope return UTC-consistent instant timestamps.
- [ ] All date-only fields remain date-only.
- [ ] All per-phase diagnostics and smoke tests pass.
- [ ] Final GitNexus change detection matches intended scope.
