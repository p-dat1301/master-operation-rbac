# issues.md

## 2026-06-22 — Tasks page: assignee/department dropdowns + permission gating

### Status: ✅ No issues found

- `TasksPageComponent` template already had `nz-select` for assignee/department with proper API loading (lines 86-87)
- Create/delete permission gating already implemented with `canCreateTask()` and `canDeleteTask()` using `authStore.hasPermission('create_task')`
- Build passes cleanly
- No runtime issues identified

### Observations
- `canDeleteTask()` delegates to `canCreateTask()` — both share the same `create_task` permission string. This is intentional per requirements (create and delete use the same permission key).
- The `NgOnInit` lifecycle now calls `loadOptions()` before `load()`, fetching users and departments in parallel via `Promise.all`.
