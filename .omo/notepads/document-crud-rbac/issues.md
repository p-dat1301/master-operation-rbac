- F1 compliance gap: `.omo/plans/document-crud-rbac.md` requires delete to ignore only missing MinIO objects but raise a defined exception for real storage failures; current `app/application/use_cases/document/delete_document.py` swallows every `Exception` and `tests/unit/application/test_delete_document_use_case.py` locks in that broader tolerance.
- F2 code-quality note: `app/application/use_cases/document/delete_document.py:43-46` still catches `Exception` around storage cleanup and converts every failure into a warning. That keeps delete moving, but it also hides real storage bugs and violates the plan's narrow ignore-only-missing-object rule.
# F3 Document CRUD RBAC API QA Issues

## 2026-06-30
- Live API QA blocker: running server at `http://localhost:8000` responds `200` for `/api/v1/auth/login` but `404 {"detail":"Not Found"}` for `/api/v1/documents/` and `/api/v1/documents/99999`.
- Because the document CRUD routes are not mounted on the active server, real employee/manager/admin list/detail/search/update/delete HTTP verification could not execute end-to-end against the live app.
- Partial executable fallback completed instead:
  - `pytest tests/integration/test_document_crud.py -vv -rs` -> `3 passed, 17 skipped`
  - Skips are explicit route-unavailable guards in `tests/integration/test_document_crud.py`.
  - `pytest` unit/RBAC coverage for document CRUD policy/use cases -> `91 passed`.
- Fresh evidence saved under `.omo/evidence/final-qa/document-crud-rbac/` and summarized in `.omo/evidence/f3-document-crud-rbac-api-qa.md`.
- F3 gate verdict for current environment: `REJECT` until a server exposing `/api/v1/documents/*` is available and the skipped integration matrix can run live.

