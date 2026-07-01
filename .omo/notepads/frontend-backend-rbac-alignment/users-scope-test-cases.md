# users-scope test-case findings

## Decision context
- Backend/users API is the authority for scope behavior.
- Current `ListUsersUseCase` still calls `find_all()` behind `manage_org`; the scope behavior described below is the target test design for the active plan, not an implementation claim.
- `UserRepository.list_by_department()` already exists and should be the repository primitive for department-scoped user lists.
- No-department manager behavior must be treated as **self-only fallback**.
- Filter behavior must never escape scope; filters only narrow the already-authorized result set.

## Concrete test-case list

### INTEG-USERS-01 — admin sees all users
- Actor: admin (`admin@company.vn`)
- Fixture setup:
  - existing seeded users: admin `id=1`, manager `id=2`, employee `id=3`
  - add one extra active employee in another department, e.g. `id=4`, `department_id=2`, `role_name="employee"`
- Request: `GET /api/v1/users/`
- Expected status: `200`
- Expected IDs: `[1, 2, 3, 4]`
- Expected exclusion: none

### INTEG-USERS-02 — manager with department sees department-subtree users
- Actor: manager (`manager@company.vn`, seeded `id=2`, `department_id=1`)
- Fixture setup:
  - department tree includes manager root department `1`
  - add descendant department `2` under `1`
  - users in scope: manager `id=2` dept `1`, employee `id=3` dept `1`, descendant employee `id=4` dept `2`
  - user out of scope: employee `id=5` dept `3` outside subtree
- Request: `GET /api/v1/users/`
- Expected status: `200`
- Expected IDs: `[2, 3, 4]`
- Expected exclusion: `5` is absent

### INTEG-USERS-03 — manager with no department falls back to self only
- Actor: manager with `id=6`, `department_id=None`, `role_name="manager"`
- Fixture setup:
  - seed no-department manager actor `id=6`
  - keep other users present: `id=1,2,3,4,5`
- Request: `GET /api/v1/users/`
- Expected status: `200`
- Expected IDs: `[6]`
- Expected exclusion: `[1, 2, 3, 4, 5]`
- Scope note: fallback is self-only, not all-users and not empty-by-default

### INTEG-USERS-04 — employee sees self only
- Actor: employee (`employee@company.vn`, seeded `id=3`, `department_id=1`)
- Fixture setup:
  - same-department manager `id=2`
  - same-department peer employee `id=4`
  - different-department employee `id=5`
- Request: `GET /api/v1/users/`
- Expected status: `200`
- Expected IDs: `[3]`
- Expected exclusion: `[2, 4, 5]`

### INTEG-USERS-05 — admin filters within full scope
- Actor: admin (`id=1`)
- Fixture setup:
  - users:
    - `id=3` employee dept `1` active `true`
    - `id=4` employee dept `2` active `true`
    - `id=5` employee dept `2` active `false`
    - `id=2` manager dept `1` active `true`
- Request: `GET /api/v1/users/?department_id=2&role_name=employee&is_active=true`
- Expected status: `200`
- Expected IDs: `[4]`
- Expected exclusion: `3` wrong dept, `5` inactive, `2` wrong role

### INTEG-USERS-06 — manager filters only within subtree scope
- Actor: manager (`id=2`, dept `1`)
- Fixture setup:
  - subtree users:
    - `id=3` employee dept `1` active `true`
    - `id=4` employee dept `2` active `true` where dept `2` is descendant of `1`
  - outside-subtree matching user:
    - `id=5` employee dept `3` active `true`
- Request: `GET /api/v1/users/?role_name=employee&is_active=true`
- Expected status: `200`
- Expected IDs: `[3, 4]`
- Expected exclusion: `5` absent even though it matches filters
- Scope note: confirms filter-escape prevention for manager scope

### INTEG-USERS-07 — no-department manager filters cannot escape self-only fallback
- Actor: no-department manager (`id=6`, `department_id=None`, `role_name="manager"`)
- Fixture setup:
  - actor `id=6` does **not** match `department_id=2` and does **not** have `role_name="employee"`
  - matching foreign users exist: `id=4` employee dept `2`, `id=5` employee dept `2`
- Request: `GET /api/v1/users/?department_id=2&role_name=employee`
- Expected status: `200`
- Expected IDs: `[]`
- Expected exclusion: `[4, 5]`
- Scope note: filter may narrow authorized self-only set to empty, but never expands beyond actor

### INTEG-USERS-08 — employee filters cannot escape self-only scope
- Actor: employee (`id=3`, `department_id=1`, `role_name="employee"`)
- Fixture setup:
  - same-role peer in same department `id=4`
  - same-role peer in another department `id=5`
- Request A: `GET /api/v1/users/?department_id=1&role_name=employee`
- Expected status A: `200`
- Expected IDs A: `[3]`
- Request B: `GET /api/v1/users/?department_id=2&role_name=employee`
- Expected status B: `200`
- Expected IDs B: `[]`
- Expected exclusion: peers `4` and `5` never appear

## Implementation notes for pytest/integration
- Follow `tests/integration/test_rbac_scenarios.py` style: one async scenario per test using `httpx.AsyncClient` and bearer-token fixtures.
- Exact assertion pattern should compare sorted IDs from `resp.json()`:
  - `assert sorted([u["id"] for u in resp.json()]) == [...]`
- For escape-prevention cases, also assert the forbidden matching IDs are absent explicitly.
- If extra users/departments are needed beyond global seed, create them in test-local setup helpers/fixtures so IDs remain deterministic.

## 2026-06-11 implementation findings
- Implemented backend-as-source-of-truth scope in `app/application/use_cases/user/list_users.py`.
- `admin`, `bod`, and any actor with `manage_org` still use `user_repo.find_all()`.
- `manager` with `department_id` now resolves authorized scope via `DepartmentTreeService.get_dept_and_descendants()` and reuses `UserRepository.list_by_department()` for each authorized department.
- `manager` without `department_id` falls back to self-only by returning `[actor]`.
- `employee` falls back to self-only by returning `[actor]`.
- API filter behavior in `app/presentation/api/v1/users.py` remains post-scope narrowing only; no widening path was added.
- DI updated in `app/di/users.py` to inject `DepartmentRepository` and `DepartmentTreeService` into `ListUsersUseCase`.
- Unit coverage updated in `tests/unit/application/test_list_users_use_case.py` for admin-all, manager-subtree, manager-no-department-self-only, and employee-self-only.

## 2026-06-11 Task 6 backend test findings
- Added direct backend route-level regression coverage in `tests/unit/presentation/test_users_route.py` for post-scope users filters.
- Covered admin full-scope filtering, manager subtree filtering, no-department manager self-only filtering to empty, and employee self-only filtering to own row/empty outside-scope result.
- Existing use-case tests in `tests/unit/application/test_list_users_use_case.py` continue to prove the scope source set: admin all-users, manager department subtree, manager no-department self-only, and employee self-only.
- Targeted verification passed: `pytest tests/unit/application/test_list_users_use_case.py tests/unit/presentation/test_users_route.py -q --disable-warnings` -> 8 passed.
- Broader external integration attempt against `tests/integration/test_rbac_scenarios.py` hit the running server's pre-Task-5 `/api/v1/users/` behavior (`403` for manager/employee), so Task 6 coverage was kept at direct backend route/use-case level rather than depending on that stale server process.

## 2026-06-11 frontend route/nav alignment findings
- Updated `apps/admin/src/app/app.routes.ts` so `/users` now uses a dedicated role gate instead of `manage_org`.
- Frontend `/users` route now allows only authenticated users whose `currentUser().role_name` is `admin` or `manager`.
- Employee access to `/users` is still denied at the route layer and redirects to `/forbidden`.
- Updated `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` so the `Người dùng` nav item is shown for `admin` and `manager` via role gating, without granting `manage_org`.
- Existing RBAC/admin-only nav items (`Roles`, `Permissions`) remain permission-gated by `manage_org`; this task did not widen them.
- Added targeted frontend unit coverage for `/users` route guard behavior and admin-shell Users nav visibility by role.

## 2026-06-11 frontend users page alignment findings
- `apps/admin/src/app/features/users/users-page.component.ts` now treats the backend list as authoritative and only adjusts presentation around the returned scope.
- Manager and employee users are rendered in view-only mode: create/reset/activate/deactivate controls are hidden and guarded.
- Manager messaging now states the list is backend-scoped, including a clean self-only fallback when no department exists.
- Employee messaging now stays self-only and avoids implying org-wide users-page authority.
- Added focused component coverage in `apps/admin/src/app/features/users/users-page.component.spec.ts` for manager view-only behavior, employee self-only behavior, and admin management access.
- Verification recorded: `npm run test:unit -- --include src/app/features/users/users-page.component.spec.ts` passed locally; `npm run build` passed locally.
- Diagnostics note: TypeScript LSP diagnostics could not be collected in this environment because `typescript-language-server` is not installed.
