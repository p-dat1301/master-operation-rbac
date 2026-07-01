# Draft: frontend-backend-rbac-alignment

## Requirements (confirmed)
- User reports frontend permissions do not match backend RBAC completely.
- Example mismatch: manager cannot view department users and cannot create tasks.
- Goal: align frontend permissions/visibility/actions with backend API behavior.
- Backend is source of truth for authorization; frontend must mirror backend capabilities and scopes as UX, not replace backend enforcement.
- `UserRepository.list_by_department()` already exists; manager department user listing should use this capability through the use-case/API path rather than granting `manage_org`.

## Technical Decisions
- Start with read-only analysis of backend RBAC definitions, frontend guards/routes/UI checks, and relevant API contracts.
- Defer implementation until mismatch map is confirmed.
- Backend is the source of truth: frontend must mirror backend permission/API scope exactly; if backend permits manager actions, UI should expose them.

## Research Findings
- No SDD framework detected (`openspec/`, `.specify/`, `_bmad/` absent).

## Open Questions
- None blocking for plan generation.

## Product Decisions
- Manager Users behavior: manager can view users in their department subtree only; manager must not get broad `manage_org`; manager cannot create/edit/reset/deactivate users in Users page.
- Manager no-department behavior: self-only fallback.
- Employee Users behavior: employee can view self only.
- RBAC Roles/Permissions list mismatch: keep as-is/out of scope for this plan.
- Frontend mirrors backend capabilities/scopes as UX; backend remains security boundary.

## Test Strategy Decision
- **Infrastructure exists**: YES (pytest backend tests, Angular unit tests, Playwright e2e).
- **Automated tests**: YES (tests-after for targeted RBAC changes; add/adjust tests alongside implementation tasks).
- **Agent-Executed QA**: ALWAYS, using pytest, Angular unit tests, Playwright e2e, and curl/API checks where useful.

## Scope Boundaries
- INCLUDE: backend role/permission definitions, frontend route/action gating, mismatch analysis.
- EXCLUDE: unrelated visual/UI theme issues.

## New Request
- User now wants the repo layout to reflect `apps/api` as the backend and `apps/admin` as the frontend.
- This is a monorepo boundary/layout refactor request, not just RBAC alignment.
- The existing RBAC alignment draft is likely not the same work item, so it should not be conflated with the layout refactor plan.
