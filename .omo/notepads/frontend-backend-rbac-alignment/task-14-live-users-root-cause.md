# Task 14 live users root cause

- Root cause: the live FastAPI route `/api/v1/users/` still calls `provide_list_users(db)` from `app/di/users.py`, and the running backend image was still serving the pre-fix code path that required `manage_org`, so manager and employee requests were rejected by `RBACService.require_permission(..., "manage_org")` with `PermissionDenied`.
- The application use case itself had already been updated in source to support admin all-users, manager subtree, manager-no-dept self, and employee self fallback, but the live server was not yet restarted/redeployed with that code.
- Filter confinement remains in the route layer: filters are applied after scope selection, so scoped users cannot escape scope via query params.
- Verification note: unit coverage for `ListUsersUseCase` passes locally; integration verification against the stale live server still returned 403 until the backend process is restarted with the updated code.
