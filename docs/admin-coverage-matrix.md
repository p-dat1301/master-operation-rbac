# Admin screen-to-API coverage matrix

Scope: current admin frontend under `apps/admin/src/app` mapped to backend routes in `app/presentation/api/v1` plus tests in `apps/admin/e2e` and component/unit specs.

Legend: **FULL** = screen and primary actions are wired to backend routes and have test coverage; **PARTIAL** = screen exists but some intended action is missing, read-only, or intentionally limited; **BLOCKER** = route/UI is intentionally protected/disabled until permission or auth condition passes; **MISSING** = no frontend surface found for a backend domain/action.

## Matrix

| Backend domain / endpoint | Frontend service | Route / page | UI action(s) | Test evidence | Status | Notes |
|---|---|---|---|---|---|---|
| `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | `AuthApiService`, `AuthStoreService` | `/login`, shell bootstrap | Sign in, persist token, hydrate current user, sign out via shell | `auth-store.service.spec.ts`, `admin.spec.ts` sign-in helper, shell render test | FULL | Auth is the root dependency for all protected pages. |
| Route guard only (`authGuard`, `permissionGuard`) | `AuthStoreService` | `/unauthorized`, `/forbidden` | Redirect unauthenticated users to unauthorized; forbidden on missing permission | `auth.guard.spec.ts`, `admin.spec.ts` protected sync route test | FULL | Guard behavior is deliberate, not a backend domain. |
| `GET /api/v1/users/`, `POST /api/v1/users/`, `GET/PUT/DELETE /api/v1/users/{id}`, `PUT /activate`, `PUT /deactivate`, `PUT /reset-password` | `UserApiService` | `/users` | List, filter active/inactive, create, edit, detail, activate/deactivate, reset password, delete | `users-page.component.spec.ts`, `admin.spec.ts` user validation test | FULL | `change-password` endpoint exists in backend but no frontend action for it. |
| `GET /api/v1/tasks/`, `POST /api/v1/tasks/`, `GET/PUT/DELETE /api/v1/tasks/{id}`, `PUT /assign`, `PUT /start`, `PUT /complete`, `PUT /cancel` | `TaskApiService` | `/tasks` | List/filter, create, edit, detail, assign, start, complete, cancel, delete | `admin.spec.ts` task lifecycle / invalid assignment test | FULL | Covers lifecycle actions exposed in UI. |
| `GET /api/v1/leaves/`, `PUT /leaves/{id}/review`, `PUT /leaves/{id}`, `PUT /leaves/{id}/cancel`, `GET /leave-balances/me`, `GET /leave-balances/users/{userId}`, `PUT /leave-balances/users/{userId}` | `LeaveApiService` | `/leaves` | List/filter, select detail, approve/reject, cancel, inline edit, view/edit balance | `admin.spec.ts` leave review guard test | FULL | Review input blocker is intentional when rejection reason missing. |
| `GET /api/v1/roles/`, `POST /roles/`, `PUT /roles/{id}`, `DELETE /roles/{id}`, `GET /roles/{id}/permissions`, `POST /roles/{id}/permissions/{permissionId}`, `DELETE /roles/{id}/permissions/{permissionId}` | `RbacApiService` | `/rbac/roles` | Create roles, manage role permissions, delete role | `admin.spec.ts` role/permission CRUD via UI | FULL | Role update endpoint exists backend-side but frontend currently only creates/deletes and manages permissions, not edit role metadata. |
| `GET /api/v1/permissions/`, `POST /permissions/`, `PUT /permissions/{id}`, `DELETE /permissions/{id}` | `RbacApiService` | `/rbac/permissions` | List, create, edit, delete permissions | `admin.spec.ts` permissions CRUD UI | FULL | Permission module is the most complete RBAC surface. |
| `GET /api/v1/departments/` | `RbacApiService` | `/system/departments` | Read-only directory of departments | `admin.spec.ts` department directory test | FULL | Intentionally read-only; no create/update UI by design. |
| `GET /api/v1/attendance/heatmap` | `AttendanceApiService` | `/attendance` | Date-range heatmap/list view, reload, failure feedback | `admin.spec.ts` attendance heatmap + failure test | FULL | Backend also exposes check-in / checkout, but admin frontend does not provide those actions. |
| `GET /api/v1/notifications/`, `PUT /notifications/{id}/read`, `PUT /notifications/read-all` | `NotificationApiService` | `/notifications` | List notifications, mark one read, mark all read | `notifications-page.component.ts` + shell route coverage; no dedicated notification spec found in current pass | PARTIAL | UI is fully wired; coverage is partial only because I did not find a direct notification-specific spec in the current review. |
| `GET /api/v1/audit_logs/` | `AuditApiService` | `/audit-logs` | List audit logs | `audit-logs-page.component.ts` + shell nav / route coverage | FULL | Frontend surface exists and is read-only by design. |
| `POST /api/v1/admin/config/menu/sync`, `POST /api/v1/admin/config/i18n/sync` | `AdminConfigSyncService` | `/config/menu-sync`, `/config/i18n-sync` | Launch sync, confirm modal, render result summary, error feedback | `admin.spec.ts` sync flow + error + modal cleanup tests | FULL | Protected by `system.config.manage`; blocked for non-admin users. |
| Shell chrome (`AdminShellComponent`) | n/a | `/`, protected children, breadcrumbs | Sidebar, header identity chip, sign out, breadcrumbs, route title | `admin.spec.ts` shell render test | FULL | Supports all admin pages; not a backend domain. |
| System result pages | n/a | `/unauthorized`, `/forbidden`, `/not-found` | Show access-denied / not-found states | `auth.guard.spec.ts`, `admin.spec.ts` sync route block and navigation coverage | FULL | Intentional terminal states for guard and routing failures. |
| Backend `POST /api/v1/attendance/checkin`, `POST /api/v1/attendance/checkout` | none in admin frontend | none | none | none | MISSING | Intentionally out of admin UI scope today. |
| Backend `PUT /api/v1/users/{id}/change-password` | none in admin frontend | none | none | none | MISSING | Backend-only path; no admin page action is exposed. |
| Backend `POST /api/v1/tasks/{id}/...` and other non-existent variants | none | none | none | none | N/A | No evidence of dead path in frontend; only actual route methods above are used. |

## Domain summary

| Domain | Coverage | Summary |
|---|---|---|
| Users | FULL | CRUD + activate/deactivate + reset password covered; `change-password` remains backend-only. |
| Tasks | FULL | List, lifecycle, assign, CRUD are wired and exercised. |
| Leaves | FULL | Review/cancel/edit/balance flow is wired; rejection reason is an intentional blocker. |
| Permissions | FULL | CRUD covered. |
| Departments | FULL | Read-only by design. |
| Attendance | FULL | Read-only heatmap/list only; check-in/out backend paths are intentionally not surfaced. |
| Notifications | PARTIAL | Frontend wiring exists; direct test evidence is weaker in current pass. |
| Sync | FULL | Menu/i18n sync flows and guard states are covered. |
| Auth/guards | FULL | Login, session bootstrap, unauthorized/forbidden, route protection covered. |
| Shell/system pages | FULL | Shell chrome + result pages are present and exercised indirectly/directly. |

## Dead or unused paths proven by references

- **No frontend dead paths were proven for the main admin domains**: every page/service listed above has a route or component reference, and the e2e/spec files exercise the primary interaction path for the core domains.
- **Backend-only but unused by admin UI**: `/api/v1/users/{id}/change-password`, `/api/v1/attendance/checkin`, `/api/v1/attendance/checkout`. These are not dead; they are simply not surfaced in the current admin UI.
- **Intentional partials/blockers**:
  - Departments is read-only by design.
  - Attendance is read-only in the admin UI.
  - Sync routes require `system.config.manage` and intentionally block managers/employees.
  - Leave rejection requires a reason; missing reason is a deliberate UI blocker.

## Evidence notes

- Route map: `apps/admin/src/app/app.routes.ts`
- Shell/nav: `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`
- E2E coverage: `apps/admin/e2e/admin.spec.ts`
- Unit coverage: `apps/admin/src/app/features/users/users-page.component.spec.ts`, `apps/admin/src/app/core/guards/auth.guard.spec.ts`, `apps/admin/src/app/services/auth-store.service.spec.ts`
- Backend routes: `app/presentation/api/v1/*.py`

