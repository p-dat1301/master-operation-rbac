# Task 8 findings — backend task capability contract

## Source files reviewed
- `app/presentation/api/v1/tasks.py`
- `app/application/use_cases/task/create.py`
- `app/application/use_cases/task/assign.py`
- `app/application/use_cases/task/start.py`
- `app/application/use_cases/task/complete.py`
- `app/application/use_cases/task/cancel.py`
- `app/application/use_cases/task/update.py`
- `app/application/use_cases/task/delete.py`
- `app/application/use_cases/task/list_tasks.py`
- `app/application/use_cases/task/get_task.py`
- `app/domain/services/rbac_service.py`
- `app/infrastructure/database/seed.py`
- `apps/admin/src/app/features/tasks/tasks-page.component.ts`
- `apps/admin/src/app/services/task-api.service.ts`
- `apps/admin/src/app/app.routes.ts`
- unit/integration tests for task use cases and RBAC scenarios

## Endpoint coverage
Backend exposes all task actions required by the plan:
- `POST /api/v1/tasks/` → create
- `GET /api/v1/tasks/` → list
- `GET /api/v1/tasks/{id}` → detail
- `PUT /api/v1/tasks/{id}/assign` → assign
- `PUT /api/v1/tasks/{id}/start` → start
- `PUT /api/v1/tasks/{id}/complete` → complete
- `PUT /api/v1/tasks/{id}/cancel` → cancel
- `PUT /api/v1/tasks/{id}` → update
- `DELETE /api/v1/tasks/{id}` → delete

## Capability matrix

| Action | Admin | Manager | Employee | Assigner relation | Assignee relation | Backend rule type |
|---|---|---|---|---|---|---|
| List | `all` scope | `department` scope | `self` scope | n/a | n/a | permission/role scope via `get_task_scope()` |
| View detail | `all` scope | `department` scope | `self`, but allowed if task is assigned by or to actor | assigner allowed for self-scope | assignee allowed for self-scope | permission/role scope + relation fallback in `GetTaskUseCase` |
| Create | allowed via `create_task` | allowed via `create_task` | denied | creator becomes assigner | optional assignee set at creation | permission-string rule (`create_task`) |
| Assign | allowed via `assign_task` | allowed via `assign_task` | denied | assigner_id is written as actor.id | assignee is target user id | permission-string rule (`assign_task`) |
| Start | allowed when `manage_org` or assignee | allowed when assignee; manager can bypass only with `manage_org` | allowed only if assignee | no direct assigner check | must be assignee unless `manage_org` | relation-based rule with permission fallback |
| Complete | allowed via `manage_org`, `complete_task`, or if actor is assigner | allowed via `complete_task` or if actor is assigner | only if `complete_task` exists; otherwise denied | assigner can complete without permission | assignee alone is not enough unless permission grants it | mixed: relation-based + permission-string + admin/bod role bypass |
| Cancel | allowed via `manage_org` or if actor is assigner | allowed only if assigner or `manage_org` | denied | assigner can cancel | assignee has no special cancel right | mixed: relation-based + permission-string fallback |
| Update | allowed via `manage_org` | allowed via `manage_org` | denied | no special relation override | no special relation override | permission-string rule (`manage_org`) |
| Delete | allowed via `manage_org` | allowed via `manage_org` | denied | no special relation override | no special relation override | permission-string rule (`manage_org`) |

## Permission-string vs relation-based rules

### Permission-string rules
These are explicit permission checks on the actor:
- `create_task` → create
- `assign_task` → assign
- `complete_task` → complete (unless relation/admin/bod shortcut applies)
- `manage_org` → update/delete, and also bypasses some start/cancel checks

### Relation-based rules
These depend on who the actor is relative to the task:
- `assigner_id == actor.id` grants extra power for:
  - complete
  - cancel
- `assignee_id == actor.id` grants start permission
- `GetTaskUseCase` allows self-scope actors to view tasks if they are either assignee or assigner

### Role-scope rules
`RBACService.get_task_scope()` currently defines:
- `admin` and `bod` → `all`
- `manager` → `department`
- everyone else → `self`

This scope is used for list and detail retrieval, not for mutation endpoints except where the specific use case separately checks `manage_org` or actor relation.

## Backend intent confirmed for each role

### Admin
- Has `manage_org` by seed and bypasses permission checks in `RBACService.has_permission()`.
- Can create, assign, update, delete.
- Can start via `manage_org` bypass.
- Can complete via `admin/bod` bypass.
- Can cancel via `manage_org` bypass.
- Can list all and view all.

### Manager
- Seeded with `create_task`, `assign_task`, `approve_leave`, `view_attendance_dept` only; **not** `manage_org`.
- Can create and assign.
- Can start only when assignee; no generic manager override.
- Can complete if they are assigner or have `complete_task`.
- Can cancel if they are assigner.
- Cannot update or delete unless future permission changes grant `manage_org`.
- List scope is department, detail scope is department.

### Employee
- No explicit task permissions in seed.
- Can only list/view self-scoped tasks.
- Can start only as assignee.
- Cannot create/assign/update/delete/cancel/complete unless some explicit permission is added; relation alone is not enough except start/view, and complete/cancel still require assigner/permission/admin-bod.

## Frontend implications for Task 11/12
- `/tasks` route is currently protected by `create_task`, which is stricter than list/view behavior; backend list/detail already support broader read access, so frontend route gating should likely be aligned with a read-capability such as list/task scope rather than create-only.
- The tasks page currently renders only status-driven row actions (`start`, `complete`, `cancel`) and does **not** gate them by permission or actor relation; backend will reject unauthorized actions, so the UI should later mirror backend capability/ownership rules to avoid dead-end clicks.
- The admin task service already exposes `assignTask`, `startTask`, `completeTask`, `cancelTask`, `deleteTask`, and `getTask`, but the page component only uses `list/start/complete/cancel` today.
- No create-task UI exists in the inspected tasks page, so route protection and page affordance are currently mismatched.

## No-code-change conclusion
- For Task 8, backend contract is already explicit enough in use cases and tests; no code change is required to verify semantics.
- The only gap is frontend alignment, which should be addressed in later tasks, not here.
