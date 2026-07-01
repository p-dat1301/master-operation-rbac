# Task 7 targeted permission mismatch findings

Date: 2026-06-11

## Scope
- Fixed only the targeted audit permission mismatch and `complete_task` permission-source mismatch.
- Did not perform broad permission taxonomy cleanup.

## Impact analysis
- `ListAuditLogsUseCase` upstream impact: LOW. Direct dependent: `app/di/audit_logs.py`; indirect API route import in `app/presentation/api/v1/audit_logs.py`; no indexed affected processes reported.
- `complete_task` API function upstream impact: LOW. No upstream dependents reported; active process is `Complete_task → From_entity` from GitNexus context.
- `_seed_permissions` upstream impact: LOW. Direct caller: `seed_all`; module impacted: Database.

## Decisions
- Audit logs now use `audit:view` as the canonical permission string in backend check, matching seed data and admin frontend route/nav gating.
- `complete_task` remains canonical in backend logic/tests. The seed permission source now includes a `complete_task` permission entry so active backend checks have a seeded/documented source.

## Verification notes
- Targeted searches should show no active Python `view_audit_logs` checks and should show `audit:view` in backend seed/use case plus frontend route/nav.
- Targeted searches should show `complete_task` in task completion logic/tests and the seed permission list.
