# Draft: Backend Remaining API Timezone Standardization

## Requirements (confirmed)
- User wants a detailed work plan to standardize time handling on the remaining backend APIs.
- Already completed and verified API groups: attendance, tasks, notifications, audit logs, leaves, leave-balances.
- Remaining target API/model areas: users, roles, permissions, departments, menu sync, i18n sync.
- Goal: unify backend timestamp behavior around UTC-aware datetimes while preserving date-only business fields as `date`.
- User wants detail sufficient for phased execution.

## Technical Decisions
- Timestamp policy: instant timestamps should be UTC-aware.
- Date-only fields must remain `date` and must not be converted into datetime fields.
- Implementation should proceed in small API groups with testing after each group.
- Impact analysis is mandatory before editing each symbol/model per repository rules.

## Research Findings
- Already standardized in previous work: attendance model/repository use `DateTime(timezone=True)` and UTC normalization.
- Remaining non-explicit timezone timestamp models found in:
  - `app/infrastructure/database/models/role_model.py`
  - `app/infrastructure/database/models/menu_model.py`
  - `app/infrastructure/database/models/user_model.py`
  - `app/infrastructure/database/models/translation_model.py`
  - `app/infrastructure/database/models/department_model.py`
  - `app/infrastructure/database/models/permission_model.py`
- Client-visible APIs already tested successfully after previous phases:
  - `/api/v1/attendance/checkin`
  - `/api/v1/attendance/heatmap`
  - `/api/v1/tasks/`
  - `/api/v1/notifications/`
  - `/api/v1/audit_logs/`
  - `/api/v1/leaves/`
  - `/api/v1/leave-balances/me`
- Final grep after prior fixes still showed old timestamp definitions in the six models above.

## Open Questions
- None blocking for plan generation.

## Scope Boundaries
- INCLUDE: remaining backend API/model timezone standardization for users, roles, permissions, departments, menu sync, i18n sync, and shared metadata timestamp persistence behind those APIs.
- EXCLUDE: frontend formatting changes, already-completed API groups unless regression verification is required, unrelated RBAC/business logic refactors.

## Test Strategy Decision
- Infrastructure exists: YES
- Automated tests: tests-after (plus diagnostics/compile and live API smoke tests per phase)
- Agent-Executed QA: ALWAYS
