# Draft: Document Upload Investigation

## Requirements (confirmed)
- User wants a **plan** to investigate why the Documents feature cannot upload files.
- Scope is investigation/debugging, not implementation.
- Focus on the document upload flow in the admin app and its backend contract.

## Known Findings
- Frontend upload call uses `FormData` and posts to `POST /api/v1/agentic/documents`.
- Frontend upload UI is gated by `authStore.hasPermission('manage_org')`.
- Frontend default policy uses `visibility_scope: 'public'`.
- Backend route requires authenticated user and only allows admin/manager roles.
- Backend schema/contract appears to use different `visibility_scope` values than the frontend default.

## Hypotheses
- Permission gate mismatch: frontend permission check may hide/block upload for valid users.
- Contract mismatch: frontend sends `visibility_scope=public` but backend expects a different enum value.
- Multipart field mismatch: backend may expect a different field name or type.
- Parser/format issue: uploaded file type or file content may be rejected.

## Open Questions
- Which users are affected: admin, manager, or all users?
- What exact error is shown in browser network/console or API response?
- Is the failure at UI validation time, request time, or backend processing time?
- Should the plan include only diagnosis or also a minimal fix verification wave?

## Scope Boundaries
- INCLUDE: frontend service, permission gate, backend route, backend schema, and file parsing/validation path.
- INCLUDE: reproducing the failure and comparing request/response contract.
- EXCLUDE: unrelated chat UI redesign work.
- EXCLUDE: changing business logic until root cause is verified.
