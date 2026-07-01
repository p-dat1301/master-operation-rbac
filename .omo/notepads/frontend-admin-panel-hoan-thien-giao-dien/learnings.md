# learnings.md

## 2026-06-22 — Tasks page: assignee/department dropdowns + permission gating

### Context
Task requested replacing raw `<input nz-input type="number">` for `assignee_id` and `department_id` with `<nz-select>` dropdowns populated from API, and hiding create/delete actions behind permission checks using `authStore.hasPermission('create_task')`.

### What was done
The changes were already applied in the working tree (unstaged). Specifically:

1. **Assignee + Department dropdowns** — The create/edit form and assign modal all use `<nz-select>` with:
   - `assigneeOptions` signal (loaded via `UserApiService.listUsers({ is_active: true })`)
   - `departmentOptions` signal (loaded via `RbacApiService.listDepartments()`)
   - `nzShowSearch` for filtering, `nzAllowClear` for clearing
   - `nzLoading` with `usersLoading`/`departmentsLoading` signals
   - `nzNotFoundContent` for empty/loading states
   - Label format for users: `"${user.full_name} · ${user.employee_code}"`, for departments: `department.name`

2. **Permission gating**:
   - `canCreateTask()` → `authStore.hasPermission('create_task')` — guards the create button (`*ngIf`)
   - `canDeleteTask()` → delegates to `canCreateTask()` — guards the delete button (`*ngIf`)
   - Both `openCreateTask()` and `confirmDeleteTask()` also have guard checks at method entry

3. **Assign modal** — Replaced raw number input for `assignAssigneeId` with the same `nz-select` user dropdown used in the main form.

### Patterns used
- Matching existing `nz-select` usage from the priority field
- `runAdminAsync` wrapper with `pending`, `fallbackMessage`, `onSuccess`, `onError` (existing project pattern)
- Signal-based loading states and option arrays
- Vietnamese labels for all UI text

### Risk assessment
- **Impact**: LOW (only `app.routes.ts` imports TasksPageComponent)
- Build passes cleanly with zero errors/warnings

### Verification
- `npm run build` in `apps/admin/` succeeds
- All existing CRUD methods (start, complete, cancel, edit, assign, delete, create) intact
- No backend changes, no new routes, no unrelated refactoring
