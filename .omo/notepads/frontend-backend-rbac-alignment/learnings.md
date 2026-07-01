## Task 11 learnings (2026-06-11)
- The task page already had minimal create/assign dialogs; no new flow was needed, only route/nav exposure and stronger action gating.
- Backend task mutation rules are mixed permission + relation, so status-only UI affordances were insufficient.
- The tasks page now treats backend authorization errors as first-class UX and reloads after failed row actions to prevent stale action state.
- Task 12 locked frontend-only RBAC via specs: users route guard blocks employees and requires auth before role checks, admin shell nav shows Users for admin/manager but not employee, and tasks page keeps create hidden without `create_task` while exposing row affordances only through backend-shaped permission/relation rules.
- Tasks page spec cleanup: the verified spec-only fix was to satisfy the ng-zorro modal test double with an `afterClose.asObservable()` shape, await the mock confirm `nzOnOk`, and explicitly destroy created fixtures after each spec while preserving every RBAC assertion.
- Verified task-page command exits 0 from `apps/admin`: `CI=true npm test -- --watch=false --include=src/app/features/tasks/tasks-page.component.spec.ts`.


## Task 13 learnings (2026-06-12)
- Added a single Playwright e2e spec block in `apps/admin/e2e/admin.spec.ts` to keep the RBAC coverage close to the existing admin-spec style instead of spreading helpers into new files.
- Seeded test-only RBAC data now uses two departments so manager subtree behavior is provable in-browser: admin sees both departments, manager sees only the scoped department subset, employee remains restricted.
- The manager task-create flow is covered end-to-end by opening the existing create dialog, filling required fields, and asserting the success toast after a mocked backend create response.
- Employee restriction is proven by asserting `/users` redirects to forbidden and `/tasks` hides the create affordance; no production code changes were needed.

## Task 15 learnings (2026-06-12)
- Root cause of the `npm run test:unit` regression was missing NG Zorro icon registration in `apps/admin/src/app/layouts/admin-shell/admin-shell.component.spec.ts`; the standalone shell component renders `dashboard`, `bell`, `team`, `safety-certificate`, `key`, `check-square`, `menu-fold`, and `menu-unfold`, and the test bed was importing the component without supplying those icons.
- The fix stayed test-only and repo-consistent by adding `provideNzIcons([...])` with the exact icons the shell uses, matching the pattern already used in `users-page.component.spec.ts` and `tasks-page.component.spec.ts`.
- Verification passed: `CI=true npm test -- --watch=false --include=src/app/layouts/admin-shell/admin-shell.component.spec.ts` and `npm run test:unit` both exit cleanly with no unhandled icon-registration exceptions.
- No production nav logic changed; existing RBAC/nav assertions remain intact.
