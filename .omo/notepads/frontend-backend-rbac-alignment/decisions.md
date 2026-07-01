## Task 11 - frontend task affordance alignment (2026-06-11)
- `/tasks` route/nav should not require `create_task`; backend list/detail scope is role/relation-based, so auth-only shell route now lets backend decide visible rows.
- Create affordance remains permission-based: only `create_task` users see/open/submit the minimal existing create modal. Manager with seeded `create_task` can use it.
- Row actions mirror backend rules as frontend affordances: assign requires `assign_task`; start requires `manage_org`/admin-bod or assignee relation; complete requires admin/bod, `complete_task`, or assigner relation; cancel requires `manage_org`/admin-bod or assigner relation.
- 403 and validation failures are surfaced through `describeTaskError`; failed row mutations refresh from backend after showing the error so stale optimistic state is not kept.
- Task 12 should add/keep focused route/nav tests proving `/tasks` is visible to authenticated employee/manager/admin while create button remains hidden without `create_task`.

