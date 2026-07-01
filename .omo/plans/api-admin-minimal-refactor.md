# Minimal Refactor Plan: Move backend from `app/` to `apps/api/`

## TL;DR
> **Quick Summary**: Move the Python backend package from `app/` to `apps/api/`, migrate the Python namespace from `app.*` to `apps.api.*`, keep the internal backend architecture unchanged, and update the imports/config/runtime references required to keep the repo working.
>
> **Deliverables**:
> - Backend source relocated to `apps/api/`
> - All `app.*` references updated to the new package path where needed
> - Runtime/tooling paths updated so backend still boots, tests, and migrations still run
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Move package → update imports/config → verify backend startup/tests

---

## Context

### Original Request
User wants the repo cleaned up by changing the backend layout from `app/` + `apps/admin/` to `apps/api/` + `apps/admin/`, with minimal risk and minimal structural churn.

### Interview Summary
**Key Discussions**:
- `apps/admin/` stays as-is.
- This plan is the low-risk version, not a deep backend architecture refactor.
- Backend internals should stay intact: domain/application/infrastructure/presentation/di/agentic.

**Research Findings**:
- Repo root currently has `app/`, `apps/admin/`, `alembic/`, `alembic.ini`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `pytest.ini`, `requirements.txt`, `scripts/`, `tests/`.
- Backend already follows a layered structure inside `app/`, so the safest change is a package move, not a redesign.
- Metis flagged likely coupling points: runtime entrypoints, Docker/Compose, Alembic imports, tests, scripts, and any hidden `app/` references.

**Metis Review**
**Identified Gaps** (addressed):
- Hidden runtime/deploy references to `app.main:app`
- Alembic path/import coupling
- Potential `backend/` directory ambiguity in current tree
- Need to verify current tree before moving anything

---

## Work Objectives

### Core Objective
Move the backend source directory from `app/` to `apps/api/`, migrate backend imports from `app.*` to `apps.api.*`, and keep behavior and architecture the same. This is a relocation and namespace-update refactor, not a redesign.

### Concrete Deliverables
- `app/` moved to `apps/api/`
- Backend imports updated from `app.*` to `apps.api.*`
- Runtime config updated so backend still starts from the new location
- Test and migration commands updated if they depend on old paths

### Definition of Done
- [ ] `apps/api/` contains the backend package tree and `app/` is no longer the backend source root
- [ ] Backend startup command works from the new path and new namespace
- [ ] Test command passes after the move
- [ ] Alembic-related commands still resolve imports/paths
- [ ] No unexpected backend architecture changes beyond the path and namespace move

### Must Have
- Move backend source to `apps/api/`
- Migrate backend namespace from `app.*` to `apps.api.*`
- Keep `apps/admin/` untouched except for backend startup/runbook command references that must follow the new namespace
- Preserve current backend module boundaries and behavior
- Update only the references required to make the new path and namespace work

### Must NOT Have (Guardrails)
- Do not redesign backend architecture
- Do not rename backend classes, functions, or modules unless a namespace/path break forces it
- Do not preserve a mixed namespace where some active backend files use `app.*` and others use `apps.api.*`
- Do not move `alembic/` or `alembic.ini` unless a specific path break requires it
- Do not move `tests/`, `scripts/`, `requirements.txt`, or `pytest.ini` as part of this plan
- Do not mix in unrelated cleanup work or feature changes
- Do not refactor `main.py` composition logic beyond what is needed for the new location and namespace

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: pytest
- **If TDD**: Not applicable here; this is a relocation refactor, so verify after each batch of path changes.

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved under `.omo/evidence/`.

- **Backend/API**: use Bash commands such as `python`, `pytest`, `uvicorn`, `alembic`, `docker compose`, or project Make targets
- **Evidence**: terminal output captured to `.omo/evidence/task-{N}-...`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation + namespace decision + path move):
├── Task 1: Inventory all runtime/config/test consumers of `app.*` and `app.main:app`
├── Task 2: Verify current tree and move `app/` to `apps/api/`
└── Task 3: Add/confirm package markers so `apps/api` is importable as `apps.api`

Wave 2 (Namespace + runtime wiring):
├── Task 4: Rewrite Python imports from `app.*` to `apps.api.*`
├── Task 5: Update backend startup entrypoints and Make/Docker/Compose references
├── Task 6: Update Alembic, seed, scripts, and test path assumptions
└── Task 7: Search for leftover `app/` references and fix only the ones that should follow the namespace move

Wave FINAL (Verification):
├── Task F1: Run backend startup verification
├── Task F2: Run pytest verification
├── Task F3: Run Alembic/DB path verification
└── Task F4: Run repo-wide reference sweep for old `app/` backend path
```

Critical Path: Task 1 → Task 2 → Task 4 → Task 5 → F1/F2/F3 → final sweep
Parallel Speedup: moderate, because import/runtime fixes can run alongside tree relocation once the namespace decision is locked
Max Concurrent: 4

### Dependency Matrix (abbreviated)
- **1**: none
- **2**: 1
- **3**: 1
- **4**: 1, 2
- **5**: 1, 2
- **6**: 1, 4
- **7**: 1, 4, 5, 6
- **F1-F4**: all prior tasks complete

### Agent Dispatch Summary
- **1**: `quick`
- **2**: `quick`
- **3**: `quick`
- **4**: `unspecified-high`
- **5**: `unspecified-high`
- **6**: `unspecified-high`
- **7**: `unspecified-high`
- **FINAL**: `unspecified-high` / `oracle`

---

## TODOs

- [ ] 1. Inventory every executable consumer of `app.*` and `app.main:app` before moving the backend

  **What to do**:
  - Read the current runtime and test consumers that hardcode `app.*` or `app.main:app`.
  - Capture the exact files that must be updated for the namespace migration: Dockerfile, docker-compose.yml, Makefile, alembic/env.py, tests, scripts, docs, and admin runbooks that start the backend.
  - Produce a concrete list of all current executable consumers before the move so the implementation step has no hidden surprises.

  **Must NOT do**:
  - Do not alter module contents during the inventory.
  - Do not move files yet.
  - Do not mix in cleanup or redesign work.

  **Recommended Agent Profile**:
  > Select an exploration-oriented agent because this task creates the migration checklist.
  - **Category**: `unspecified-high`
    - Reason: This is a repo-wide inventory of executable consumers and hardcoded import/runtime paths.
  - **Skills**: [`gitnexus-exploring`, `gitnexus-refactoring`]
    - `gitnexus-exploring`: Finds current runtime/test/script consumers accurately.
    - `gitnexus-refactoring`: Keeps findings tied to the namespace migration.
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because missing one consumer can break runtime after the migration.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Tasks 2-7
  - **Blocked By**: None

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References**:
  - `app/` backend tree - Source of truth for the current backend layout that will move and change namespace.
  - `Dockerfile` - Likely contains backend startup or copy-path assumptions.
  - `docker-compose.yml` - Likely contains backend service mount/startup assumptions.
  - `Makefile` - Likely contains backend run/test/seed commands using `app.*`.
  - `alembic/env.py` - Common place for direct backend imports.
  - `apps/admin/playwright.config.ts` - May start the backend with `uvicorn app.main:app` during E2E.
  - `apps/admin/README.md` - May document active backend startup commands used by developers.

  **API/Type References**:
  - `apps/admin/` - Existing frontend app that must stay in place but may need backend startup command updates.

  **Test References**:
  - `tests/` - Existing test tree that may import `app.*` directly.
  - `scripts/` - Common place for seed/demo/reset commands that may import backend modules.

  **External References**:
  - N/A

  **WHY Each Reference Matters**:
  - `app/` shows the current backend structure that must be preserved while relocating.
  - Docker, Compose, Make, Alembic, admin Playwright, and scripts are the hidden consumers most likely to break the migration.
  - `tests/` is the canary for import/path breakage after the move.

  **Acceptance Criteria**:
  - [ ] The inventory lists every executable consumer of `app.*` and `app.main:app` that the move must update
  - [ ] The resulting checklist names the exact files and commands that will break if left stale
  - [ ] The task identifies admin Playwright, Make, Docker, Compose, Alembic, scripts, tests, and docs consumers where they exist

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Runtime consumer inventory is complete
    Tool: Bash
    Preconditions: Repo is still before the move.
    Steps:
      1. Search active repo files for `app.main:app`, `app.*`, and `app/` backend path references.
      2. Record matches from Dockerfile, docker-compose.yml, Makefile, alembic/env.py, tests, scripts, apps/admin, and docs/runbooks where present.
      3. Classify each match as runtime-critical, test-critical, doc/runbook-critical, or intentionally unrelated.
    Expected Result: A concrete migration checklist exists before any file move.
    Failure Indicators: Known consumers like Docker, Make, Alembic, admin Playwright, tests, or scripts are not checked.
    Evidence: .omo/evidence/task-1-consumer-inventory.txt

  Scenario: No conflicting backend source root is missed
    Tool: Bash
    Preconditions: Inventory completed.
    Steps:
      1. Inspect root-level source directories for `app/`, `apps/`, and any existing `backend/` tree.
      2. Confirm which directory is the canonical backend source before moving.
    Expected Result: The plan executor knows exactly which backend tree to move.
    Failure Indicators: A competing backend tree exists but is not classified.
    Evidence: .omo/evidence/task-1-backend-root-inventory.txt
  ```

  **Evidence to Capture**:
  - [ ] Consumer inventory output
  - [ ] Classification of any existing `backend/` directory or competing backend tree

  **Commit**: NO
  - Message: N/A, inventory only
  - Files: none
  - Pre-commit: N/A

- [ ] 2. Move backend source from `app/` to `apps/api/` and verify the tree is what we expect

  **What to do**:
  - Move the backend package directory into `apps/api/` while preserving the existing internal module structure.
  - Confirm `apps/api/` now contains the backend code and `app/` is no longer the backend source root.
  - Validate the tree after the move so the import rewrite has a stable target.

  **Must NOT do**:
  - Do not change business modules.
  - Do not introduce a new packaging system or dependency manager.

  **Recommended Agent Profile**:
  > Select a small implementation agent that can perform the move without editing internals.
  - **Category**: `quick`
    - Reason: This is a filesystem relocation once the inventory has identified the canonical backend root.
  - **Skills**: [`gitnexus-refactoring`]
    - `gitnexus-refactoring`: Keeps the move scoped and avoids unrelated code changes.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-exploring`: Omitted because Task 1 already completed the exploration inventory.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1 and 3 once Task 1 has finished moving the tree)
  - **Blocks**: Tasks 4-7
  - **Blocked By**: Task 1

  **References**:
  - `app/` - Current backend root to relocate.
  - `apps/api/` - Destination backend root.
  - Task 1 inventory output - Source of truth for known consumers before the move.

  **WHY Each Reference Matters**:
  - The move must preserve backend internals while changing only location.
  - The inventory prevents moving the wrong tree or forgetting a coupled source root.

  **Acceptance Criteria**:
  - [ ] Backend source files now live under `apps/api/`
  - [ ] `app/` is no longer the backend source root
  - [ ] The resulting directory tree matches the intended monorepo layout

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Backend tree is relocated cleanly
    Tool: Bash
    Preconditions: Task 1 completed.
    Steps:
      1. Run a directory listing for the repo root.
      2. Confirm `apps/api/` exists and contains the backend package tree.
      3. Confirm `app/` is no longer present as the backend source root.
    Expected Result: The filesystem reflects the new monorepo layout with backend under `apps/api/`.
    Failure Indicators: `app/` still exists as the active backend source root or `apps/api/` is missing backend files.
    Evidence: .omo/evidence/task-2-backend-tree-relocated.txt

  Scenario: No conflicting backend tree remains
    Tool: Bash
    Preconditions: Relocation completed.
    Steps:
      1. Inspect root-level source directories.
      2. Verify there is no competing active backend tree masquerading as the source of truth.
    Expected Result: Only `apps/api/` is the backend source root.
    Failure Indicators: Two backend roots remain or the wrong tree still owns imports.
    Evidence: .omo/evidence/task-2-no-conflicting-backend-tree.txt
  ```

  **Evidence to Capture**:
  - [ ] Directory listing showing the new tree
  - [ ] Any output proving the old backend root is gone

  **Commit**: YES | NO (groups with 4)
  - Message: `refactor(api): move backend into apps/api`
  - Files: `app/`, `apps/api/`
  - Pre-commit: `git status --short`

- [ ] 3. Confirm `apps/api/` is importable as the backend package and add package markers only if needed

  **What to do**:
  - Check whether Python package markers are needed for `apps/` and `apps/api/` in the current project setup.
  - Add only the minimal markers/config needed so `apps.api.*` imports resolve cleanly from the new path.
  - Keep the package semantics aligned with the existing backend code.

  **Must NOT do**:
  - Do not change business modules.
  - Do not introduce a new packaging system or dependency manager.

  **Recommended Agent Profile**:
  > This is a path-update task, so keep it mechanical and low-risk.
  - **Category**: `quick`
    - Reason: This is mostly string/path adjustment in a few files.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: Helps ensure the touched files are the right path-sensitive ones.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-refactoring`: Omitted because the task is about config strings, not code structure.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (after Task 1 confirms the move)
  - **Blocks**: Tasks 4-7
  - **Blocked By**: Tasks 1 and 2 where import semantics are relevant

  **References**:
  - `Dockerfile` - likely has backend entrypoint or copy path references.
  - `docker-compose.yml` - likely has backend service paths or mount references.
  - `Makefile` - likely has backend startup/test commands.
  - `pytest.ini` - may hold path or import config.
  - `alembic.ini` - may reference the backend package path.

  **WHY Each Reference Matters**:
  - These files are the most likely to break when the package moves.
  - Path-sensitive strings here must be updated for the new layout to work.

  **Acceptance Criteria**:
  - [ ] Obvious `app/` path references in runtime/config files are updated
  - [ ] No accidental behavior changes beyond the new path

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Path-sensitive config no longer points at old backend root
    Tool: Bash
    Preconditions: Task 1 completed.
    Steps:
      1. Inspect the key config/runtime files.
      2. Verify backend references point to `apps/api/` or the new import path.
    Expected Result: No obvious runtime config still assumes the old `app/` root.
    Failure Indicators: `app.main` or `COPY app` style references remain where they should not.
    Evidence: .omo/evidence/task-3-config-paths-updated.txt

  Scenario: Build/start commands still refer to backend in a valid way
    Tool: Bash
    Preconditions: Config changes applied.
    Steps:
      1. Read the Make/Docker/Compose entrypoints.
      2. Confirm they align with the relocated backend.
    Expected Result: Entry commands use the new path or remain compatible with the new layout.
    Failure Indicators: Stale backend path in startup commands.
    Evidence: .omo/evidence/task-3-entrypoints-valid.txt
  ```

  **Evidence to Capture**:
  - [ ] Snippets from updated config files
  - [ ] Command output or file excerpts showing old paths removed

  **Commit**: YES | NO (groups with 4)
  - Message: `refactor(api): update backend path references`
  - Files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `pytest.ini`, `alembic.ini`
  - Pre-commit: `git diff --stat`

- [ ] 4. Rewrite Python imports from `app.*` to `apps.api.*` where the relocation requires it

  **What to do**:
  - Update absolute imports throughout the backend and tests to use the new package path.
  - Keep the import changes mechanical and limited to the move.
  - Preserve module behavior and names.

  **Must NOT do**:
  - Do not rename application modules.
  - Do not refactor logic while touching imports.

  **Recommended Agent Profile**:
  > This is the main code-edit task, so use a higher-effort agent and keep the change set coherent.
  - **Category**: `unspecified-high`
    - Reason: This is the widest search-and-rewrite step and may touch many files.
  - **Skills**: [`gitnexus-refactoring`]
    - `gitnexus-refactoring`: Best fit for a broad package path move with many references.
  - **Skills Evaluated but Omitted**:
    - `gitnexus-exploring`: Omitted because the import surface was already mapped earlier.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 5-7
  - **Blocked By**: Tasks 1-3

  **References**:
  - `app/` / `apps/api/` backend tree - source and destination paths for the import rewrite.
  - `tests/` - likely contains backend imports that need the new path.
  - `scripts/` - may reference backend modules directly.

  **WHY Each Reference Matters**:
  - The move will fail unless every `app.*` import that still matters is updated.
  - Tests and scripts often expose the hidden import surface.

  **Acceptance Criteria**:
  - [ ] All required `app.*` backend imports are updated to `apps.api.*`
  - [ ] The codebase still imports cleanly after the move
  - [ ] No accidental logic changes were introduced

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Backend imports resolve under new package path
    Tool: Bash
    Preconditions: Tasks 1-3 completed.
    Steps:
      1. Run a Python import sweep or targeted import check against the backend package.
      2. Confirm the relocated package imports successfully.
    Expected Result: Imports succeed with the new `apps.api` path.
    Failure Indicators: Module import errors or broken absolute paths.
    Evidence: .omo/evidence/task-4-imports-resolve.txt

  Scenario: No accidental code rewrite beyond imports
    Tool: Bash
    Preconditions: Import rewrite applied.
    Steps:
      1. Inspect diff for import-only changes in the touched backend files.
      2. Confirm there are no unrelated logic edits mixed into the import rewrite.
    Expected Result: The diff stays focused on import path changes.
    Failure Indicators: Business logic or unrelated cleanup changed in the same patch.
    Evidence: .omo/evidence/task-4-import-only-diff.txt
  ```

  **Evidence to Capture**:
  - [ ] Import check output
  - [ ] Diff excerpt showing import-only edits

  **Commit**: YES | NO (groups with 5)
  - Message: `refactor(api): rewrite backend imports`
  - Files: backend Python source and tests touched by the import rename
  - Pre-commit: `python -m compileall apps/api` or project equivalent

- [ ] 5. Update backend startup, Make, Docker, and Compose wiring to the new package location

  **What to do**:
  - Update runtime commands so the backend boots from `apps/api/`.
  - Adjust `uvicorn` or module entrypoints if they still point at `app.main`.
  - Keep the operational flow the same; only the path changes.

  **Must NOT do**:
  - Do not redesign the boot process.
  - Do not add a new service architecture.

  **Recommended Agent Profile**:
  > This task is path-sensitive and touches runtime behavior, so it needs careful verification.
  - **Category**: `unspecified-high`
    - Reason: Runtime config changes can silently break the app if a path is missed.
  - **Skills**: [`gitnexus-exploring`, `gitnexus-refactoring`]
    - `gitnexus-exploring`: Useful for tracing entrypoint flow.
    - `gitnexus-refactoring`: Keeps the command updates aligned with the move.
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because the runtime surface is bigger than a trivial one-file edit.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 1-4

  **References**:
  - `Dockerfile` - backend image/start command wiring.
  - `docker-compose.yml` - service startup and mount wiring.
  - `Makefile` - local dev and test shortcuts.
  - `alembic.ini` - if the entrypoint references backend module paths.

  **WHY Each Reference Matters**:
  - This is where `app.main:app` or `COPY app` style assumptions usually live.
  - Missing one path here can make the whole refactor look done but fail at runtime.

  **Acceptance Criteria**:
  - [ ] Backend runtime commands target the new package path
  - [ ] Docker/Compose flows still start the backend successfully
  - [ ] Make targets still work or are updated to equivalent commands

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Backend starts from new package path
    Tool: Bash
    Preconditions: Tasks 1-4 completed.
    Steps:
      1. Run the project’s documented backend start command.
      2. Observe successful startup from the relocated module path.
    Expected Result: Backend boots cleanly using `apps/api`.
    Failure Indicators: `ModuleNotFoundError`, `app.main` reference errors, or failed startup.
    Evidence: .omo/evidence/task-5-backend-starts.txt

  Scenario: Container/dev wiring still matches the move
    Tool: Bash
    Preconditions: Runtime config updated.
    Steps:
      1. Inspect Docker/Compose/Make references or run the lightweight validation command.
      2. Confirm they no longer assume `app/` as the backend root.
    Expected Result: Runtime wiring is aligned with the new layout.
    Failure Indicators: Startup command still points at the old root.
    Evidence: .omo/evidence/task-5-runtime-wiring.txt
  ```

  **Evidence to Capture**:
  - [ ] Backend startup command output
  - [ ] Docker/Compose/Make validation output

  **Commit**: YES | NO (groups with 4)
  - Message: `refactor(api): update runtime wiring`
  - Files: `Dockerfile`, `docker-compose.yml`, `Makefile`
  - Pre-commit: backend startup smoke command

- [ ] 6. Update Alembic and test assumptions that still point at the old backend path

  **What to do**:
  - Verify Alembic imports and path assumptions still work after the move.
  - Update test configs or fixtures only where they hardcode the old backend root.
  - Keep changes narrow and mechanically tied to the rename.

  **Must NOT do**:
  - Do not move Alembic out of place in this plan.
  - Do not rework the test suite structure.

  **Recommended Agent Profile**:
  > This is a medium-risk config task because it often breaks silently.
  - **Category**: `unspecified-high`
    - Reason: Alembic and tests are both sensitive to package-path changes.
  - **Skills**: [`gitnexus-refactoring`]
    - `gitnexus-refactoring`: Best fit for adjusting path assumptions without changing structure.
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because this may require multiple config touch points.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 1, 4, 5

  **References**:
  - `alembic/env.py` - likely imports backend models and metadata.
  - `pytest.ini` - may include import path or test discovery assumptions.
  - `tests/` - backend tests may still import `app.*`.

  **WHY Each Reference Matters**:
  - Alembic is the most common hidden break after a backend move.
  - Tests will catch import-path assumptions early.

  **Acceptance Criteria**:
  - [ ] Alembic commands still resolve backend models/imports
  - [ ] Test config or fixtures no longer assume the old path where necessary
  - [ ] Backend-related tests still run under the new package layout

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Alembic import/path check passes
    Tool: Bash
    Preconditions: Tasks 1, 4, and 5 completed.
    Steps:
      1. Run a non-destructive Alembic validation command.
      2. Confirm imports and config resolve under the relocated backend path.
    Expected Result: Alembic resolves without old-path errors.
    Failure Indicators: Module import failures, metadata not found, or stale path errors.
    Evidence: .omo/evidence/task-6-alembic-validates.txt

  Scenario: Test discovery still sees backend tests
    Tool: Bash
    Preconditions: Import/config updates applied.
    Steps:
      1. Run the project’s targeted backend test command.
      2. Confirm tests are discovered and run under the new layout.
    Expected Result: Backend tests still execute successfully.
    Failure Indicators: Discovery breaks or imports fail because of the path move.
    Evidence: .omo/evidence/task-6-tests-discover.txt
  ```

  **Evidence to Capture**:
  - [ ] Alembic validation output
  - [ ] Test discovery / test run output

  **Commit**: YES | NO (groups with 4)
  - Message: `refactor(api): repair alembic and test paths`
  - Files: `alembic/env.py`, `pytest.ini`, backend test files if needed
  - Pre-commit: `alembic current` or equivalent non-destructive check

- [ ] 7. Sweep the repo for leftover backend `app/` references and fix only the ones still relevant

  **What to do**:
  - Search for remaining `app.*`, `app/`, and `app.main` references that are still relevant after the move.
  - Fix only the references that should now point to `apps/api/`.
  - Leave intentional mentions alone if they are historical, explanatory, or unrelated.

  **Must NOT do**:
  - Do not rewrite the repo for style.
  - Do not touch unrelated docs or historical notes unless they break the move.

  **Recommended Agent Profile**:
  > This task is for cleanup of leftover references, not for new architecture.
  - **Category**: `unspecified-high`
    - Reason: It may touch many files, but the work is still mechanical.
  - **Skills**: [`gitnexus-exploring`, `gitnexus-refactoring`]
    - `gitnexus-exploring`: Helps find the remaining references accurately.
    - `gitnexus-refactoring`: Keeps the cleanup tied to the move rather than broad edits.
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because leftover references may be spread across multiple files.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification wave
  - **Blocked By**: Tasks 1-6

  **References**:
  - `README.md` - may still be empty, but should not be expanded unless needed for the move.
  - `scripts/` - possible hidden path references.
  - `tests/` - possible stale import references.
  - `Dockerfile`, `docker-compose.yml`, `Makefile`, `alembic.env.py`, `pytest.ini` - the most likely places for leftovers.

  **WHY Each Reference Matters**:
  - A move only counts if the old path stops leaking through operationally.
  - Sweeping leftovers catches what the first pass misses.

  **Acceptance Criteria**:
  - [ ] Relevant repo references to the old backend path are removed or updated
  - [ ] Any remaining `app` mentions are intentional and non-breaking
  - [ ] The move is not hiding stale path dependencies

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  ```
  Scenario: Repo-wide stale path sweep is clean
    Tool: Bash
    Preconditions: Tasks 1-6 completed.
    Steps:
      1. Run a repo-wide search for old backend path references.
      2. Inspect matches and ensure only intentional ones remain.
    Expected Result: No breaking stale `app/` backend references remain.
    Failure Indicators: `app.main`, `COPY app`, or similar stale references remain in active paths.
    Evidence: .omo/evidence/task-7-stale-reference-sweep.txt

  Scenario: Intentional historical mentions are not over-edited
    Tool: Bash
    Preconditions: Search completed.
    Steps:
      1. Check any surviving matches.
      2. Confirm they are historical or intentionally unrelated.
    Expected Result: Only non-breaking references remain.
    Failure Indicators: The sweep rewrote files that should have stayed untouched.
    Evidence: .omo/evidence/task-7-intentional-mentions.txt
  ```

  **Evidence to Capture**:
  - [ ] Search output for leftover references
  - [ ] Short note on any intentionally preserved mentions

  **Commit**: YES | NO (groups with 5)
  - Message: `refactor(api): sweep stale backend references`
  - Files: any remaining path-sensitive files
  - Pre-commit: `grep`/search command showing only intentional leftovers

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

- [ ] F1. **Backend startup smoke test** — `oracle`
  Read the new layout and validate the documented backend startup command against the relocated package path. Confirm the service starts without old-path failures.

  **Recommended Agent Profile**:
  - **Category**: `oracle`
    - Reason: This is a read-only verification of runtime behavior with a single correctness gate.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `unspecified-high`: Omitted because the startup check is a targeted verification, not broad exploration.

  **Acceptance Criteria**:
  - [ ] Backend startup command succeeds from the relocated package path
  - [ ] No `ModuleNotFoundError` or stale `app.main` path failure appears
  - [ ] The service reaches its normal ready state

  Output: `Startup [PASS/FAIL] | Path [PASS/FAIL] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Test suite verification** — `unspecified-high`
  Run the main backend test command and confirm test discovery/imports work from `apps/api/`.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: This verification can touch more than one test surface and needs broader execution.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because this is a repo-wide validation, not a trivial check.

  **Acceptance Criteria**:
  - [ ] Backend tests are discovered under the relocated layout
  - [ ] Test command completes successfully
  - [ ] No import errors stem from the new package path

  Output: `Tests [PASS/FAIL] | Discovery [PASS/FAIL] | VERDICT`

- [ ] F3. **Alembic / migration verification** — `unspecified-high`
  Run a non-destructive Alembic command to confirm model imports and config still resolve after the move.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Migration validation often reveals import or metadata breakage that needs careful inspection.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because Alembic validation can require multiple checks if imports drift.

  **Acceptance Criteria**:
  - [ ] Alembic resolves the backend models/metadata after the move
  - [ ] The non-destructive command exits cleanly
  - [ ] No stale path errors remain in migration wiring

  Output: `Alembic [PASS/FAIL] | Imports [PASS/FAIL] | VERDICT`

- [ ] F4. **Stale reference audit** — `deep`
  Search the repo for old backend path references and verify any survivors are intentional, not broken. Check for accidental leftovers in Docker, Compose, Make, tests, scripts, and docs.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: This is the broadest final audit and needs a thorough repo sweep.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `quick`: Omitted because stale-reference hunting is wider than a small fix.

  **Acceptance Criteria**:
  - [ ] No breaking backend references to the old `app/` root remain
  - [ ] Any remaining matches are intentional and non-breaking
  - [ ] Docker, Compose, Make, tests, scripts, and docs are free of stale backend paths

  Output: `Stale refs [CLEAN/ISSUES] | Intentional [YES/NO] | VERDICT`

---

## Commit Strategy

- **1**: `refactor(api): move backend into apps/api` - relocation only
- **2**: `refactor(api): update backend path references` - config/runtime strings
- **3**: `refactor(api): rewrite backend imports` - Python imports and tests
- **4**: `refactor(api): update runtime wiring` - Docker/Compose/Make
- **5**: `refactor(api): repair alembic and test paths` - migration and test config
- **6**: `refactor(api): sweep stale backend references` - leftovers only

---

## Success Criteria

### Verification Commands
```bash
# Backend startup command used by the repo
command  # Expected: starts cleanly from apps/api

# Test command
pytest  # Expected: backend tests pass

# Migration validation
alembic current  # Expected: resolves without path/import errors
```

### Final Checklist
- [ ] Backend lives under `apps/api/`
- [ ] `apps/admin/` unchanged
- [ ] Runtime and tool configs point to the new backend path
- [ ] Tests pass
- [ ] Alembic still works
- [ ] No stale breaking `app/` backend references remain
