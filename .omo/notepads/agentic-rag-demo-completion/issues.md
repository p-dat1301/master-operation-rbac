# Issues and Gotchas

## Problems Encountered

(Subagents will append issues here)

- 2026-06-22: Added admin agentic routes `/agentic/conversations` and `/agentic/documents` as lazy standalone shells under auth. `/chat` stayed unchanged. Nav now groups agentic entries under an `Agentic` section for future regrouping.
- 2026-06-22: Admin agentic API service now exposes detail reads for `/agentic/conversations/{id}` and `/agentic/documents/{id}`, and upload payloads forward optional classification / visibility / allowed_roles / department_id policy fields via multipart FormData.
- 2026-06-22: Moved agentic shared DTOs into `apps/admin/src/app/models/agentic.models.ts` so the service can consume exported interfaces instead of private duplicates.
