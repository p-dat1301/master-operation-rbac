# Document Upload Failure Investigation

## TL;DR

> **Quick Summary**: Investigate why the Documents upload flow cannot complete by reproducing the failure end-to-end, capturing the exact browser/network/API evidence, and comparing the frontend request contract with the backend upload contract.
>
> **Deliverables**:
> - Reproduction notes with exact failure trigger and environment
> - Evidence bundle: browser network trace, API response body, and relevant server-side logs
> - Root-cause report with one clear failure statement backed by code references
> - Minimal contract mismatch matrix for frontend vs backend upload requirements
>
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Reproduce failure → capture request/response → verify frontend/backend contract mismatch → synthesize root cause

---

## Context

### Original Request
User asked to create a plan to check why the Documents feature cannot upload files.

### Interview Summary
**Key Discussions**:
- The issue is investigation/debugging only; no implementation yet.
- The upload flow is in `apps/admin/src/app/features/chat/agentic-documents-page.component.ts` and `apps/admin/src/app/services/agentic-api.service.ts`.
- Upload uses multipart `FormData` to `POST /api/v1/agentic/documents`.
- Frontend gating uses `authStore.hasPermission('manage_org')`.
- Frontend default `visibility_scope` is `public`.
- Backend route requires authenticated user and only allows admin/manager roles.
- Backend contract likely does not accept `public` and may expect a different enum value.
- Metis emphasized that the plan must start with reproducible evidence, not assumptions.

**Research Findings**:
- Frontend service constructs multipart upload payload with `file`, `classification`, `visibility_scope`, `allowed_roles`, and `department_id`.
- Backend route handles `POST /api/v1/agentic/documents` and enforces role-based permissions plus schema/parsing rules.
- Upload failure candidates include permission gate mismatch, multipart schema mismatch, visibility scope enum mismatch, parser limitations, and file content issues.

**Metis Review**:
**Identified Gaps** (addressed):
- Missing concrete failure reproduction and network trace capture.
- Open-ended scope between diagnosis and fixes.
- Ambiguous evidence strategy.
- Need to explicitly lock scope to investigation only.

---

## Work Objectives

### Core Objective
Identify the exact reason the Documents upload flow fails, using reproducible evidence and contract verification, without changing code.

### Concrete Deliverables
- A reproducible failure record with exact steps and environment
- Browser network capture of the failing upload request
- Backend/API response and log evidence for the failure
- A contract comparison between frontend upload payload and backend expectations
- A final root-cause summary naming the most likely break point(s)

### Definition of Done
- [ ] Failure reproduced at least once in a controlled environment
- [ ] Network trace or equivalent captured for `POST /api/v1/agentic/documents`
- [ ] Backend response body or server log shows the failure cause
- [ ] Frontend vs backend contract mismatch table completed
- [ ] Root cause stated in one sentence with evidence references

### Must Have
- Reproduce the failure before interpreting code
- Capture exact request payload and exact response/error
- Check both frontend permission gate and backend auth/validation path
- Compare `visibility_scope` values and multipart field names against backend schema
- Keep the work read-only: no implementation changes

### Must NOT Have (Guardrails)
- No code fixes in this plan
- No scope creep into unrelated chat UI work
- No broad refactor of auth or upload architecture
- No assumptions about root cause without evidence
- No expanding to all upload features outside Documents

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> This is an investigation plan, so verification means evidence capture and contract comparison, not unit test creation.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: None for this plan (diagnostic investigation only)
- **Framework**: none
- **Evidence-driven QA**: Reproduction steps, browser devtools network trace, API response capture, and backend log inspection

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright to open the admin app, reach the Documents page, attempt upload, and capture screenshots/network logs
- **API/Backend**: Use curl or direct request replay to hit `POST /api/v1/agentic/documents` and capture the JSON/error body
- **Logs**: Capture the relevant backend application logs around the failure timestamp

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent investigation tasks into parallel waves.
> Target: 3-5 tasks per wave. This is investigation work, so fewer tasks is acceptable when one step depends on prior evidence.

```
Wave 1 (Reproduce and capture evidence):
├── Task 1: Reproduce the upload failure in the admin UI and capture network trace
├── Task 3: Verify the logged-in role/permission state used by the upload UI
└── Task 4: Record the exact file type and form values used during reproduction

Sequential Gate after Task 1:
└── 2. Capture backend/API response and server logs for the same failed request

Wave 2 (Contract comparison and root cause isolation):
├── Task 5: Compare frontend multipart payload against backend schema expectations
├── Task 6: Compare frontend permission gate against backend auth/role rules
├── Task 7: Check parser support and file-content constraints for the reproduced file type
└── Task 8: Synthesize one root-cause statement and evidence matrix

Wave FINAL (Cross-check):
├── F1. Evidence completeness audit
├── F2. Contract mismatch audit
├── F3. Reproduction consistency audit
└── F4. Root-cause confidence review
```

### Dependency Matrix

- **1, 3, 4**: Start immediately; all feed Wave 2
- **2**: Depends on 1
- **5**: Depends on 1 and 2
- **6**: Depends on 1 and 3
- **7**: Depends on 1 and 4
- **8**: Depends on 5-7
- **F1-F4**: Depends on 1-8

### Agent Dispatch Summary

- **1-4**: `unspecified-high` for evidence capture and targeted debugging
- **5-7**: `deep` or `unspecified-high` depending on contract complexity
- **8**: `deep` for synthesis
- **FINAL**: `oracle`, `unspecified-high`, `unspecified-high`, `deep`

---

## TODOs

> Implementation + Test = ONE Task. For this plan, each task is investigation + evidence capture in one unit.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE.**
> **FORMAT**: Task labels MUST use bare numbers: `1.`, `2.`, `3.` — NOT `T1.`, `Task 1.`, `Phase 1:`.
> Final Verification Wave labels MUST use `F1.`, `F2.`, etc.

- [ ] 1. Reproduce the upload failure in the admin UI and capture the browser network trace

  **What to do**:
  - Open the admin app and navigate to the Documents page.
  - Attempt the exact upload flow that currently fails.
  - Capture the failing `POST /api/v1/agentic/documents` request in browser devtools/network logs.
  - Record the chosen file name, file type, visibility scope, and any optional policy fields.

  **Must NOT do**:
  - Do not change the UI or any code.
  - Do not assume the error source before capturing the request/response.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Requires interactive debugging and evidence capture in the running app.
  - **Skills**: [`playwright`, `gitnexus-debugging`]
    - `playwright`: Needed to reproduce the UI flow and capture screenshots/network evidence.
    - `gitnexus-debugging`: Needed to trace the relevant upload flow symbols and verify no hidden code path is missed.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Not needed because no code changes are allowed.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3, 4)
  - **Blocks**: Tasks 5-8
  - **Blocked By**: None

  **References** (CRITICAL - Be Exhaustive):
  - `apps/admin/src/app/features/chat/agentic-documents-page.component.ts:297-325` - Exact submit flow and client-side validation to reproduce the same path.
  - `apps/admin/src/app/services/agentic-api.service.ts:56-60` - Multipart request construction used by the upload action.
  - `apps/admin/src/app/services/auth-store.service.ts` - Permission gate affecting whether upload is visible or allowed.
  - `apps/admin/src/app/shared/async-state.ts` - Error mapping path that may hide the real API response.

  **WHY Each Reference Matters**:
  - These files define the actual failure surface in the admin UI and show what should be observable in the browser trace.

  **Acceptance Criteria**:
  - [ ] A reproduction note exists with exact steps and environment.
  - [ ] A captured network trace for `POST /api/v1/agentic/documents` exists.
  - [ ] The captured trace includes request payload and response status/body.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Successful reproduction of failing upload path
    Tool: Playwright
    Preconditions: Admin app running, authenticated user on Documents page, known failing file ready.
    Steps:
      1. Open the Documents page and open the upload modal.
      2. Select file `policy.pdf` and submit using the same form values used by the user.
      3. Capture the network request `POST /api/v1/agentic/documents` and save it.
    Expected Result: Request is sent and the exact failure response is captured.
    Failure Indicators: No request is sent, or response details are missing.
    Evidence: .omo/evidence/task-1-upload-trace.har

  Scenario: Negative case - blocked before network request
    Tool: Playwright
    Preconditions: Upload modal open, no file selected or invalid form state.
    Steps:
      1. Leave the file input empty and click Upload.
      2. Observe whether the frontend blocks the request.
    Expected Result: Frontend shows validation and no network request is sent.
    Evidence: .omo/evidence/task-1-validation-blocked.png
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-1-upload-trace.har`
  - [ ] `.omo/evidence/task-1-validation-blocked.png`

  **Commit**: NO

- [ ] 2. Capture backend/API response and logs for the same failed upload request

  **What to do**:
  - Replay the same upload request against the backend.
  - Capture the JSON response body and HTTP status code.
  - Pull the relevant server logs around the failure timestamp.
  - Confirm whether the backend rejected the request at auth, schema, or parsing time.

  **Must NOT do**:
  - Do not alter backend code.
  - Do not infer the failure cause from the frontend alone.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Requires backend request replay and log inspection.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to map the backend upload route and inspect its failure path.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not necessary if replaying the same request directly with curl or HTTP client.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Task 1
  - **Blocks**: Tasks 5, 8
  - **Blocked By**: Task 1 for the exact request shape

  **References**:
  - `app/presentation/api/v1/agentic/router.py:229-328` - Backend upload route and its validation/parse path.
  - `tests/unit/test_agentic_api.py:100-121` - Existing expectations for success and 403 behavior.
  - `app/presentation/dependencies/auth_deps.py` - Authentication requirement for the route.

  **WHY Each Reference Matters**:
  - These references show where a backend rejection can occur and what success/error responses should look like.

  **Acceptance Criteria**:
  - [ ] HTTP status and response body captured for the failing request.
  - [ ] Relevant backend log lines collected.
  - [ ] Rejection stage classified as auth, schema, or parser/processing.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Replay failing upload request and capture backend response
    Tool: Bash (curl)
    Preconditions: Exact multipart payload from Task 1 available.
    Steps:
      1. Replay the request with the same file and fields.
      2. Save status code and response body.
      3. Collect backend logs for the same timestamp window.
    Expected Result: The backend’s exact rejection reason is captured.
    Failure Indicators: Status/body absent or logs unavailable.
    Evidence: .omo/evidence/task-2-backend-response.json

  Scenario: Negative case - unauthorized request
    Tool: Bash (curl)
    Preconditions: Valid endpoint, missing/invalid token.
    Steps:
      1. Submit the same multipart request without a valid Bearer token.
      2. Capture the response.
    Expected Result: 401/403 is returned and logged.
    Evidence: .omo/evidence/task-2-unauthorized-response.json
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-2-backend-response.json`
  - [ ] `.omo/evidence/task-2-backend-logs.txt`

  **Commit**: NO

- [ ] 3. Verify the logged-in user role and permission state used by the upload UI

  **What to do**:
  - Inspect the current admin session state and the permission gate used by Documents upload.
  - Confirm whether the user is blocked by `manage_org` permission or by backend role expectations.
  - Record the exact role/permission combination for the failing user.

  **Must NOT do**:
  - Do not change the permission logic.
  - Do not widen scope to unrelated auth features.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Requires auth-state inspection and code-path validation.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to trace permission checks and auth state in the codebase.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Only needed if reproducing the UI session state visually is required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 4)
  - **Blocks**: Tasks 6 and 8
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/features/chat/agentic-documents-page.component.ts:211,297-300` - Frontend permission gate and submit guard.
  - `apps/admin/src/app/services/auth-store.service.ts` - Source of truth for `hasPermission('manage_org')`.
  - `app/presentation/api/v1/agentic/router.py:229-236` - Backend role/auth requirement.

  **WHY Each Reference Matters**:
  - Upload can fail before reaching the backend if the permission gate rejects the user, so the plan must capture the actual auth state.

  **Acceptance Criteria**:
  - [ ] Exact current role/permission state recorded.
  - [ ] Permission gate result documented.
  - [ ] Mismatch between frontend gate and backend role rule noted if present.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Confirm upload gate state for current user
    Tool: Browser devtools or Playwright
    Preconditions: Authenticated admin session on Documents page.
    Steps:
      1. Inspect the rendered upload controls and permission-dependent UI.
      2. Verify whether upload is visible/enabled.
    Expected Result: The current permission gate state is documented.
    Evidence: .omo/evidence/task-3-permission-state.png

  Scenario: Negative case - permission denied user
    Tool: Playwright
    Preconditions: Use a user known not to have `manage_org`.
    Steps:
      1. Open Documents page.
      2. Attempt to open/submit upload.
    Expected Result: Upload is blocked by the frontend gate.
    Evidence: .omo/evidence/task-3-permission-denied.png
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-3-permission-state.png`
  - [ ] `.omo/evidence/task-3-permission-denied.png`

  **Commit**: NO

- [ ] 4. Record the exact file type and form values used during reproduction

  **What to do**:
  - Note the file name, extension, MIME type, size, and any policy fields used in the failing attempt.
  - Verify whether the failing case uses the frontend default `visibility_scope` or a custom one.
  - Identify whether the issue depends on file type or content.

  **Must NOT do**:
  - Do not test unrelated file upload areas.
  - Do not switch to fixing the file parser.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Needs careful reproduction metadata capture.
  - **Skills**: [`playwright`]
    - `playwright`: Needed to exercise the upload form with concrete file inputs and record the chosen values.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-debugging`: Optional, but not required for pure metadata capture.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 7 and 8
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/features/chat/agentic-documents-page.component.ts:213,332-351` - Policy fields and client-side validation rules.
  - `apps/admin/src/app/services/agentic-api.service.ts:56-95` - Payload construction and field naming.
  - `app/presentation/api/v1/agentic/router.py:229-260` - Backend form expectations and parsing path.

  **WHY Each Reference Matters**:
  - File metadata and form values are essential for determining whether the failure is tied to content, MIME type, or policy fields.

  **Acceptance Criteria**:
  - [ ] File metadata recorded.
  - [ ] Policy values recorded.
  - [ ] Any file-type-specific behavior noted.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Capture known failing file metadata
    Tool: Playwright
    Preconditions: Failing file available.
    Steps:
      1. Select the failing file in the upload modal.
      2. Record file name, size, and MIME type.
      3. Submit and log the form values.
    Expected Result: Exact reproduction metadata is recorded.
    Evidence: .omo/evidence/task-4-file-metadata.txt

  Scenario: Negative case - different file type
    Tool: Playwright
    Preconditions: Alternate supported file available.
    Steps:
      1. Repeat upload with a different supported file type.
      2. Compare result to failing file.
    Expected Result: Any file-type-specific failure pattern becomes visible.
    Evidence: .omo/evidence/task-4-file-type-compare.txt
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-4-file-metadata.txt`
  - [ ] `.omo/evidence/task-4-file-type-compare.txt`

  **Commit**: NO

- [ ] 5. Compare frontend multipart payload against backend schema expectations

  **What to do**:
  - Compare the actual request fields captured in Wave 1 against backend request parsing/schema.
  - Check `visibility_scope`, `allowed_roles`, `department_id`, and `file` naming and typing.
  - Identify the first field mismatch that would reject the upload.

  **Must NOT do**:
  - Do not change schema values.
  - Do not infer success from matching names alone; verify enum/value semantics.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: Requires contract comparison and precise reasoning over request schemas.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to inspect backend route, schema, and related failure paths.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed for contract comparison once the trace is captured.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 1 and 2

  **References**:
  - `apps/admin/src/app/services/agentic-api.service.ts:56-95` - Actual multipart payload construction.
  - `app/presentation/api/v1/agentic/router.py:229-260` - Backend upload function and policy handling.
  - `app/presentation/schemas/agentic_schema.py` - Backend request schema definitions.

  **WHY Each Reference Matters**:
  - This is the most likely root-cause area if the frontend sends a value or field shape the backend rejects.

  **Acceptance Criteria**:
  - [ ] Frontend payload fields listed.
  - [ ] Backend-expected fields listed.
  - [ ] Every mismatch categorized as harmless or blocking.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Match request payload to backend contract
    Tool: Bash
    Preconditions: Wave 1 request capture available.
    Steps:
      1. Compare request field names and values to backend schema.
      2. Identify mismatches in enum/value semantics.
    Expected Result: A clear mismatch table is produced.
    Evidence: .omo/evidence/task-5-payload-contract.md

  Scenario: Negative case - invalid visibility scope value
    Tool: Bash
    Preconditions: Known backend enum values available.
    Steps:
      1. Replay the request with the frontend default value.
      2. Observe backend validation result.
    Expected Result: The invalid value is rejected or confirmed as accepted.
    Evidence: .omo/evidence/task-5-visibility-scope-check.json
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-5-payload-contract.md`
  - [ ] `.omo/evidence/task-5-visibility-scope-check.json`

  **Commit**: NO

- [ ] 6. Compare frontend permission gate against backend auth/role rules

  **What to do**:
  - Compare `manage_org` permission gate with backend `admin/manager` role requirement.
  - Determine whether the upload is blocked on the client or rejected by the server for the affected user.
  - Document whether the observed failure is a UI gate issue, a role mismatch, or both.

  **Must NOT do**:
  - Do not redesign auth.
  - Do not broaden scope to all admin permissions.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: Requires reasoning about auth rules across frontend and backend.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to trace the gate in both the frontend and backend code.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Optional because auth state was captured in Wave 1.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 1 and 3

  **References**:
  - `apps/admin/src/app/features/chat/agentic-documents-page.component.ts:211,297-300` - Frontend permission gate.
  - `apps/admin/src/app/services/auth-store.service.ts` - Permission mapping logic.
  - `app/presentation/api/v1/agentic/router.py:229-236` - Backend auth/role enforcement.
  - `tests/unit/test_agentic_api.py:100-121` - Existing role-based behavior expectations.

  **WHY Each Reference Matters**:
  - This comparison determines whether the user is blocked before request submission or rejected afterward.

  **Acceptance Criteria**:
  - [ ] Frontend gate rule documented.
  - [ ] Backend role rule documented.
  - [ ] Any mismatch clearly labeled as cause or non-cause.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Compare permission gate and backend role rule
    Tool: Bash
    Preconditions: Current auth state known.
    Steps:
      1. Inspect frontend permission check and backend role requirement.
      2. Compare against current user role.
    Expected Result: The blocking layer is identified.
    Evidence: .omo/evidence/task-6-auth-compare.md

  Scenario: Negative case - role mismatch
    Tool: Bash
    Preconditions: Test user without manager/admin role.
    Steps:
      1. Attempt upload.
      2. Capture whether the client or server blocks first.
    Expected Result: Role mismatch failure is reproduced and classified.
    Evidence: .omo/evidence/task-6-role-mismatch.json
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-6-auth-compare.md`
  - [ ] `.omo/evidence/task-6-role-mismatch.json`

  **Commit**: NO

- [ ] 7. Check parser support and file-content constraints for the reproduced file type

  **What to do**:
  - Verify whether the uploaded file type is supported by the backend parser registry.
  - Check whether file content triggers parser/normalization failure rather than upload/authorization failure.
  - Distinguish unsupported MIME type from a valid MIME type with empty/no-extractable content.

  **Must NOT do**:
  - Do not change parser code.
  - Do not expand to unrelated ingestion pipelines.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: Requires backend parsing path analysis and failure mode comparison.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to trace parser registry and parse/normalize failures.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not required once the file type has been identified.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6)
  - **Blocks**: Task 8
  - **Blocked By**: Task 4

  **References**:
  - `app/agentic/pipeline/parsing/parser_registry.py` - Supported MIME types and parser routing.
  - `app/agentic/adapters/parsers/pdf_parser.py` - PDF parser failure behavior.
  - `app/agentic/adapters/parsers/docx_parser.py` - DOCX parser behavior and unsupported legacy `.doc` path.
  - `app/agentic/pipeline/parsing/core.py` - Parse/normalize failure handling.

  **WHY Each Reference Matters**:
  - A file-type/content issue can look identical to an auth or contract issue unless parser constraints are checked.

  **Acceptance Criteria**:
  - [ ] Supported vs unsupported file type confirmed.
  - [ ] File-content failure mode documented if applicable.
  - [ ] Parser-related failure ruled in or out.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Check parser support for failing file type
    Tool: Bash
    Preconditions: Reproduced file type known.
    Steps:
      1. Inspect parser registry support for the MIME type.
      2. Compare to the failing upload’s MIME type.
    Expected Result: Support mismatch or compatibility is documented.
    Evidence: .omo/evidence/task-7-parser-support.md

  Scenario: Negative case - empty or textless supported file
    Tool: Bash
    Preconditions: Supported file type available.
    Steps:
      1. Upload a supported file with no extractable text.
      2. Capture parser failure behavior.
    Expected Result: Parser/content failure is distinguished from contract failure.
    Evidence: .omo/evidence/task-7-parser-failure.json
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-7-parser-support.md`
  - [ ] `.omo/evidence/task-7-parser-failure.json`

  **Commit**: NO

- [ ] 8. Synthesize the root cause and evidence matrix for the upload failure

  **What to do**:
  - Combine reproduction evidence, backend response, auth comparison, payload contract, and parser checks.
  - Write one root-cause statement with supporting evidence and confidence level.
  - Identify which mismatch is primary and which are secondary/noise.

  **Must NOT do**:
  - Do not suggest code changes as part of this plan.
  - Do not hide uncertainty; if evidence is partial, state it clearly.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Requires structured synthesis across multiple evidence sources.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to tie the traced code paths to the observed failure.
  - **Skills Evaluated but Omitted**:
    - `playwright`: Evidence should already exist from Wave 1.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 5, 6, 7

  **References**:
  - All evidence files from Tasks 1-7.
  - `apps/admin/src/app/features/chat/agentic-documents-page.component.ts`
  - `apps/admin/src/app/services/agentic-api.service.ts`
  - `app/presentation/api/v1/agentic/router.py`
  - `tests/unit/test_agentic_api.py`

  **WHY Each Reference Matters**:
  - This task turns raw evidence into a single actionable diagnosis.

  **Acceptance Criteria**:
  - [ ] One-sentence root cause written.
  - [ ] Evidence matrix included.
  - [ ] Confidence level stated.

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Synthesize evidence into a root-cause statement
    Tool: Bash
    Preconditions: Tasks 1-7 evidence available.
    Steps:
      1. Review all evidence artifacts.
      2. Produce a root-cause summary with citations.
    Expected Result: Clear diagnosis with confidence level.
    Evidence: .omo/evidence/task-8-root-cause.md

  Scenario: Negative case - conflicting evidence
    Tool: Bash
    Preconditions: At least two potential causes still plausible.
    Steps:
      1. Compare conflicting evidence.
      2. Note what additional proof would be needed.
    Expected Result: Uncertainty is explicitly documented.
    Evidence: .omo/evidence/task-8-uncertainty.md
  ```

  **Evidence to Capture**:
  - [ ] `.omo/evidence/task-8-root-cause.md`
  - [ ] `.omo/evidence/task-8-uncertainty.md`

  **Commit**: NO

---

## Final Verification Wave (MANDATORY — after ALL investigation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Evidence Completeness Audit** — `oracle`
  Confirm every required evidence artifact exists and matches the reproduction steps. Reject if the plan forgot network logs, response bodies, or logs.
  Output: `Evidence [N/N] | Repro [PASS/FAIL] | VERDICT: APPROVE/REJECT`

  **Recommended Agent Profile**:
  - **Category**: `oracle`
    - Reason: Requires independent evidence-quality judgment.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to verify evidence maps to the traced upload path.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F2, F3, F4)
  - **Blocks**: Final user handoff
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - [ ] All evidence artifacts from Tasks 1-8 are present.
  - [ ] Network trace, backend response, and logs are all accounted for.
  - [ ] No missing reproduction evidence remains.

- [ ] F2. **Contract Mismatch Audit** — `unspecified-high`
  Verify the documented frontend payload and backend schema comparison is complete. Check for missing enum/value mismatches, auth mismatches, and multipart field mismatches.
  Output: `Payload [PASS/FAIL] | Auth [PASS/FAIL] | Parser [PASS/FAIL] | VERDICT`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful cross-file contract review.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to validate frontend/backend upload flow references.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F3, F4)
  - **Blocks**: Final user handoff
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - [ ] Frontend multipart fields are fully listed.
  - [ ] Backend schema/enum expectations are fully listed.
  - [ ] Every mismatch is classified as blocking or non-blocking.

- [ ] F3. **Reproduction Consistency Audit** — `unspecified-high`
  Re-run the reproduction steps from a clean state and confirm the failure is deterministic or clearly conditional. Note any environment-sensitive behavior.
  Output: `Deterministic [YES/NO] | Environment [stable/variable] | VERDICT`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires re-running and validating the investigation path from a clean state.
  - **Skills**: [`playwright`, `gitnexus-debugging`]
    - `playwright`: Needed to reproduce the UI flow again.
    - `gitnexus-debugging`: Needed to keep the reproduction tied to the traced code path.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F4)
  - **Blocks**: Final user handoff
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - [ ] The failure is re-run from a clean state.
  - [ ] Determinism or environment sensitivity is explicitly recorded.
  - [ ] Reproduction steps remain valid for another operator.

- [ ] F4. **Root-Cause Confidence Review** — `deep`
  Read the final synthesis and judge whether the root cause is supported strongly enough to proceed to a fix plan later. Flag any remaining ambiguity.
  Output: `Confidence [HIGH/MED/LOW] | Gaps [list] | VERDICT`

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires synthesis of all evidence into a confidence-ranked diagnosis.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: Needed to tie the evidence back to the upload flow and root cause.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F3)
  - **Blocks**: Final user handoff
  - **Blocked By**: Tasks 1-8

  **Acceptance Criteria**:
  - [ ] One root-cause statement is supported by evidence.
  - [ ] Any remaining ambiguity is explicitly listed.
  - [ ] The result is suitable to hand off to a future fix plan.

---

## Commit Strategy

- **1-8**: `no` - investigation only, no code changes
- **F1-F4**: `no` - final review only

---

## Success Criteria

### Verification Commands
```bash
# Reproduce upload failure and capture network trace
# Expected: evidence artifact created and failure captured

# Replay request against backend
# Expected: exact response body and status captured

# Compare frontend and backend contracts
# Expected: mismatch table completed with root cause evidence
```

### Final Checklist
- [ ] Failure reproduced
- [ ] Request/response captured
- [ ] Frontend/backend contract compared
- [ ] Parser/file-type constraints checked
- [ ] Root cause synthesized
