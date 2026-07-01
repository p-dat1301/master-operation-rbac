# Frontend Redesign Plan

## TL;DR
> **Quick Summary**: Rebuild the admin frontend around a Linear-style dark shell, keeping the Angular routes and auth flow intact. The work starts at the shell and shared styling layers, then proves the new system on the dashboard and one table-heavy page before expanding outward.
>
> **Deliverables**:
> - Updated admin shell and sidebar navigation
> - Shared page styling aligned to the new visual system
> - Refreshed dashboard baseline
> - One table-heavy screen updated to validate the pattern
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Shell + shared styles → dashboard baseline → table-heavy validation page

---

## Context

### Original Request
User wants a frontend redesign plan for the current Angular admin app. They selected a **Linear hybrid** direction: dark admin shell first, with a light Voltagent-style AI/devtool accent if it fits.

### Interview Summary
**Key Discussions**:
- The current app is an Angular 21 admin console with ng-zorro-antd and Tailwind v4.
- The layout rebuild should be centered on the admin shell, sidebar, and shared page styles.
- The safest, highest-leverage redesign path is to keep auth and routing intact while restyling the shell and representative pages.

**Research Findings**:
- The current UI already has a strong shell split: `admin-shell.component.ts`, `admin-shell-nav.component.ts`, and `admin-page-styles.ts` are the leverage points.
- The app is not a greenfield rewrite. It is a protected admin console with route guards and many table/form-heavy screens.
- `awesome-design-md` is best used as a visual constitution source, not as a direct layout copy.

### Metis Review
**Identified Gaps** (addressed):
- Potential scope creep from a shell redesign into auth or route logic: explicitly excluded.
- Possible ambiguity between pure visual refresh and navigation reshuffle: resolved to visual refresh first, with reshuffle deferred unless user asks.
- Need for a representative validation screen: added a table-heavy page after the dashboard.

---

## Work Objectives

### Core Objective
Redesign the admin frontend so it feels like a cohesive, modern Linear-style dark product while preserving the current Angular app structure and access control model.

### Concrete Deliverables
- A redesigned admin shell with updated layout, spacing, and visual hierarchy.
- A sidebar/nav refresh that matches the new shell.
- Shared page styles that make the redesign scale across screens.
- A dashboard refresh that becomes the visual baseline.
- One table-heavy feature page updated to prove the new system works outside the dashboard.

### Definition of Done
- [ ] `admin-shell.component.ts` renders the new shell successfully in local dev.
- [ ] `admin-shell-nav.component.ts` matches the new navigation look and grouping.
- [ ] `admin-page-styles.ts` supports the new card/table/form language.
- [ ] Dashboard reflects the new visual direction without breaking route guards.
- [ ] One table-heavy page matches the new design system and still functions.

### Must Have
- Keep auth flow, permission guards, and route definitions intact.
- Preserve admin app behavior while changing layout and styling.
- Make shell-level changes first so the new look propagates efficiently.

### Must NOT Have (Guardrails)
- No backend API changes.
- No auth or permission logic rewrites.
- No unrelated feature rewrites.
- No whole-app IA rewrite unless explicitly approved later.
- No generic “theme refresh” that stops at surface-level colors only.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring user confirmation are forbidden.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: Existing project test stack + Angular build/diagnostics checks
- **If Tests-after**: Implement layout/styling changes first, then verify with build, diagnostics, and targeted UI checks

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright or the repo’s browser QA path to verify shell, nav, and page states
- **Angular UI**: Run build/diagnostics and inspect rendered routes
- **Feature pages**: Validate both happy path and edge-state rendering

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - foundation + scaffolding):
├── Task 1: Shell layout refresh [quick]
├── Task 2: Sidebar/nav refresh [quick]
└── Task 3: Shared page style tokens [quick]

Wave 2 (After Wave 1 - core pages, MAX PARALLEL):
├── Task 4: Dashboard redesign [unspecified-high]
├── Task 5: Table-heavy page redesign [unspecified-high]
└── Task 6: Global theme polish [quick]

Wave 3 (After Wave 2 - validation + cleanup):
├── Task 7: Cross-screen consistency pass [deep]
├── Task 8: Responsive behavior pass [unspecified-high]
└── Task 9: Final visual QA and build verification [unspecified-high]

Wave FINAL (After ALL tasks - 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Real manual QA [unspecified-high]
└── Task F4: Scope fidelity check [deep]
-> Present results -> Get explicit user okay
```

### Dependency Matrix
- **1-3**: foundation tasks, can start immediately in parallel
- **4-6**: depend on the shell/styling foundation from Wave 1
- **7-8**: depend on the core page work from Wave 2
- **9**: depends on 1-8 being complete

### Agent Dispatch Summary
- **1-3**: `quick`
- **4-6**: `unspecified-high`
- **7**: `deep`
- **8-9**: `unspecified-high`
- **F1**: `oracle`
- **F2-F3**: `unspecified-high`
- **F4**: `deep`

---

## TODOs

- [x] 1. `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`: Refresh the app shell frame to create the new layout language - expect a cleaner dark admin canvas

  **What to do**:
  - Update the shell spacing, header density, and content framing to fit a Linear-style admin layout.
  - Keep the router outlet and auth-protected structure unchanged.
  - Verify the shell still behaves responsively when collapsed.

  **Must NOT do**:
  - Do not change route guards or authentication wiring.
  - Do not restructure the application route tree.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Single shell component with a focused layout pass.
  - **Skills**: `[]`
    - No special skill needed beyond focused implementation.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4-9
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Primary layout entry point for the redesign.
  - `apps/admin/src/app/app.routes.ts` - Confirms the shell is route-wrapper infrastructure, not the place to change navigation logic.

  **Acceptance Criteria**:
  - [ ] Shell renders with updated spacing and visual hierarchy.
  - [ ] Router outlet still works inside the shell.
  - [ ] Collapse/expand behavior still functions.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Shell renders the new layout on authenticated routes
    Tool: Playwright
    Preconditions: App running locally, authenticated user session available
    Steps:
      1. Open the admin root route.
      2. Verify the shell header, sidebar, breadcrumb area, and content panel are visible.
      3. Assert the new shell spacing and framing are applied.
    Expected Result: The app shell matches the new layout without breaking route rendering.
    Failure Indicators: Missing sidebar, broken outlet, clipped content panel.
    Evidence: .omo/evidence/task-1-shell-render.png

  Scenario: Shell handles collapsed navigation state
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Collapse the sidebar using the shell toggle.
      2. Verify content width expands and header remains aligned.
      3. Navigate to another route and confirm shell persists.
    Expected Result: Collapse/expand behavior remains stable across navigation.
    Evidence: .omo/evidence/task-1-shell-collapse.png
  ```

  **Evidence to Capture**:
  - [ ] `task-1-shell-render.png`
  - [ ] `task-1-shell-collapse.png`

  **Commit**: YES | NO (groups with 2, 3)
  - Message: `feat(ui): refresh admin shell layout`
  - Files: `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`
  - Pre-commit: `build + targeted UI check`

- [x] 2. `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts`: Rework the sidebar navigation presentation - expect clearer sections and stronger active states

  **What to do**:
  - Rebuild nav grouping, active-state styling, and spacing to match the new shell.
  - Keep the existing route destinations and permissions intact.
  - Make the nav feel denser and more intentional without hiding key sections.

  **Must NOT do**:
  - Do not change permission checks or route targets.
  - Do not add new navigation sections unless already present in the app.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Focused sidebar presentation update.
  - **Skills**: `[]`
    - No special skill needed.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 4-9
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts` - Sidebar presentation and active state logic.
  - `apps/admin/src/app/app.routes.ts` - Existing route groups and permissions used by the nav.

  **Acceptance Criteria**:
  - [ ] Sidebar grouping matches the redesign language.
  - [ ] Active route state is visually obvious.
  - [ ] Navigation still points to the same routes.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Sidebar highlights the active route
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Open the dashboard route.
      2. Navigate to a second major route like users or audit logs.
      3. Verify the sidebar active state shifts correctly.
    Expected Result: The sidebar clearly marks the current page.
    Evidence: .omo/evidence/task-2-nav-active.png

  Scenario: Sidebar groups remain intact after redesign
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Expand the sidebar.
      2. Inspect the major section labels.
      3. Confirm the same route destinations still exist.
    Expected Result: Navigation structure remains intact and readable.
    Evidence: .omo/evidence/task-2-nav-groups.png
  ```

  **Evidence to Capture**:
  - [ ] `task-2-nav-active.png`
  - [ ] `task-2-nav-groups.png`

  **Commit**: YES | NO (groups with 1, 3)
  - Message: `feat(ui): refresh sidebar navigation`
  - Files: `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts`
  - Pre-commit: `build + targeted UI check`

- [x] 3. `apps/admin/src/app/shared/admin-page-styles.ts`: Replace shared page surfaces with the new visual language - expect reusable card, table, and form styling

  **What to do**:
  - Update shared card/table/form page primitives so the redesign scales.
  - Make the page surfaces feel consistent with the Linear hybrid direction.
  - Keep the styles reusable across dashboard and operational screens.

  **Must NOT do**:
  - Do not hardcode page-specific logic here.
  - Do not couple these tokens to only one screen.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Shared styling file with focused token updates.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Tasks 4-9
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared page primitives used across the admin app.
  - `apps/admin/src/styles.css` - Global theme layer that may need to align with these tokens.

  **Acceptance Criteria**:
  - [ ] Shared surfaces support the new dark admin language.
  - [ ] Cards/tables/forms look consistent across screens.
  - [ ] The file stays reusable and screen-agnostic.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Shared surfaces render consistently on dashboard and tables
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Open the dashboard page.
      2. Open a table-heavy page.
      3. Compare card borders, spacing, and table treatment.
    Expected Result: Shared surfaces appear consistent across different screens.
    Evidence: .omo/evidence/task-3-shared-surfaces.png

  Scenario: Shared styles do not collapse forms or empty states
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Navigate to a screen with forms or empty states.
      2. Verify spacing and surface hierarchy remain readable.
    Expected Result: Forms and empty states still look intentional.
    Evidence: .omo/evidence/task-3-forms-empty.png
  ```

  **Evidence to Capture**:
  - [ ] `task-3-shared-surfaces.png`
  - [ ] `task-3-forms-empty.png`

  **Commit**: YES | NO (groups with 1, 2)
  - Message: `feat(ui): update shared admin page styles`
  - Files: `apps/admin/src/app/shared/admin-page-styles.ts`
  - Pre-commit: `build + targeted UI check`

- [x] 4. `apps/admin/src/app/features/dashboard/dashboard-page.component.ts`: Redesign the dashboard as the visual baseline - expect the new shell language to show up first here

  **What to do**:
  - Restyle the dashboard to establish the new design vocabulary.
  - Prioritize hierarchy, spacing, and readable density.
  - Use the dashboard as the first proof that the new shell language works.

  **Must NOT do**:
  - Do not add new backend data dependencies.
  - Do not change dashboard routing or guard logic.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: This is a key representative screen with enough surface area to need careful design judgment.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6)
  - **Blocks**: Tasks 7-9
  - **Blocked By**: Tasks 1-3

  **References**:
  - `apps/admin/src/app/features/dashboard/dashboard-page.component.ts` - Main authenticated landing screen.
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared surface system to reuse here.

  **Acceptance Criteria**:
  - [ ] Dashboard reflects the new Linear hybrid direction.
  - [ ] Dashboard remains readable and dense without looking cramped.
  - [ ] No route or data regressions.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Dashboard renders the redesigned baseline cleanly
    Tool: Playwright
    Preconditions: App running locally, authenticated user session available
    Steps:
      1. Open the dashboard.
      2. Verify page hierarchy, cards, and whitespace are intentional.
      3. Capture a screenshot for visual comparison.
    Expected Result: The dashboard looks like the new design system baseline.
    Evidence: .omo/evidence/task-4-dashboard-baseline.png

  Scenario: Dashboard still loads with empty or slow data states
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Simulate or observe a loading state.
      2. Verify the page does not collapse or show broken layout.
    Expected Result: Loading/empty states remain structurally sound.
    Evidence: .omo/evidence/task-4-dashboard-loading.png
  ```

  **Evidence to Capture**:
  - [ ] `task-4-dashboard-baseline.png`
  - [ ] `task-4-dashboard-loading.png`

  **Commit**: YES | NO (groups with 5, 6)
  - Message: `feat(ui): redesign dashboard baseline`
  - Files: `apps/admin/src/app/features/dashboard/dashboard-page.component.ts`
  - Pre-commit: `build + targeted UI check`

- [x] 5. `apps/admin/src/app/features/users/users-page.component.ts` or another table-heavy screen: Apply the redesign to a data-dense page - expect proof the system works beyond the dashboard

  **What to do**:
  - Restyle one table-heavy operational screen so the redesign proves itself on real work content.
  - Keep the underlying behavior intact.
  - Reuse the shared page surfaces rather than special-casing the screen.

  **Must NOT do**:
  - Do not rewrite table logic or API calls.
  - Do not introduce one-off styling that cannot scale to other pages.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Table-heavy operational page needs careful density and readability choices.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 6)
  - **Blocks**: Tasks 7-9
  - **Blocked By**: Tasks 1-3

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts` - Representative data-dense page.
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared styling layer to use here.

  **Acceptance Criteria**:
  - [ ] Table-heavy page matches the new design language.
  - [ ] Density remains functional and readable.
  - [ ] Existing page behavior remains intact.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Table-heavy page renders with the new surface system
    Tool: Playwright
    Preconditions: App running locally, authenticated user session available
    Steps:
      1. Open the users page or chosen table-heavy page.
      2. Verify table header, rows, controls, and surface styling.
      3. Capture a screenshot for later comparison.
    Expected Result: The page clearly matches the new visual system.
    Evidence: .omo/evidence/task-5-table-page.png

  Scenario: Table interactions still work after restyling
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Sort or interact with one table control.
      2. Verify the control still responds correctly.
    Expected Result: Redesign does not break table interaction.
    Evidence: .omo/evidence/task-5-table-interaction.png
  ```

  **Evidence to Capture**:
  - [ ] `task-5-table-page.png`
  - [ ] `task-5-table-interaction.png`

  **Commit**: YES | NO (groups with 4, 6)
  - Message: `feat(ui): restyle data-dense admin page`
  - Files: `apps/admin/src/app/features/users/users-page.component.ts`
  - Pre-commit: `build + targeted UI check`

- [x] 6. `apps/admin/src/styles.css`: Align global theme overrides with the new design language - expect ng-zorro to feel native to the redesign

  **What to do**:
  - Tune global dark theme overrides so ng-zorro components match the shell and shared surfaces.
  - Keep the changes broad enough to help modals, inputs, selects, and tables.
  - Avoid overfitting to one screen.

  **Must NOT do**:
  - Do not add ad hoc per-page hacks here.
  - Do not break existing dark mode or component defaults.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Global theme layer is a focused style polish task.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: Tasks 7-9
  - **Blocked By**: Tasks 1-3

  **References**:
  - `apps/admin/src/styles.css` - Global styling and ng-zorro overrides.
  - `apps/admin/src/app/shared/admin-page-styles.ts` - Shared surface styles that should stay in sync.

  **Acceptance Criteria**:
  - [ ] Global overrides match the redesigned shell.
  - [ ] Core ng-zorro elements feel visually consistent.
  - [ ] No regressions in component rendering.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Global theme makes modals, inputs, and selects feel consistent
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Open a page with inputs or a modal.
      2. Verify the component surfaces match the shell language.
      3. Capture a screenshot for review.
    Expected Result: Core ng-zorro components feel native to the redesign.
    Evidence: .omo/evidence/task-6-global-theme.png

  Scenario: Global overrides do not break component readability
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Inspect focus states and text contrast.
      2. Verify inputs and buttons remain legible.
    Expected Result: Theme changes improve polish without reducing usability.
    Evidence: .omo/evidence/task-6-contrast.png
  ```

  **Evidence to Capture**:
  - [ ] `task-6-global-theme.png`
  - [ ] `task-6-contrast.png`

  **Commit**: YES | NO (groups with 4, 5)
  - Message: `feat(ui): align global theme overrides`
  - Files: `apps/admin/src/styles.css`
  - Pre-commit: `build + targeted UI check`

- [x] 7. Cross-screen consistency pass: compare shell, dashboard, and data-heavy page together - expect one coherent visual system

  **What to do**:
  - Review the redesigned shell and the two representative pages together.
  - Fix spacing, hierarchy, or contrast mismatches that only show up across screens.
  - Make sure the app feels like one system, not three different ones.

  **Must NOT do**:
  - Do not introduce new page-specific exceptions.
  - Do not reopen unrelated feature areas.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `deep`
    - Reason: Cross-screen consistency requires system-level judgment.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 9)
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 1-6

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Shell baseline.
  - `apps/admin/src/app/features/dashboard/dashboard-page.component.ts` - Primary landing page.
  - `apps/admin/src/app/features/users/users-page.component.ts` - Data-dense validation page.

  **Acceptance Criteria**:
  - [ ] Shell and pages feel like the same design system.
  - [ ] Spacing and surface treatment are consistent.
  - [ ] No stray old-theme elements remain on the validated screens.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Compare redesign consistency across major screens
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Capture the shell.
      2. Capture the dashboard.
      3. Capture the data-heavy page and compare consistency.
    Expected Result: The screens look like one product family.
    Evidence: .omo/evidence/task-7-consistency-board.png

  Scenario: No lingering legacy layout artifacts remain on validated screens
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Inspect the selected screens.
      2. Confirm old spacing, color, or border conventions are not still prominent.
    Expected Result: The validated screens fully reflect the new design language.
    Evidence: .omo/evidence/task-7-legacy-check.png
  ```

  **Evidence to Capture**:
  - [ ] `task-7-consistency-board.png`
  - [ ] `task-7-legacy-check.png`

  **Commit**: YES | NO
  - Message: `refactor(ui): align frontend redesign across screens`
  - Files: `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`, `apps/admin/src/app/features/dashboard/dashboard-page.component.ts`, `apps/admin/src/app/features/users/users-page.component.ts`
  - Pre-commit: `visual QA + build`

- [x] 8. Responsive behavior pass: verify the redesigned shell on smaller widths - expect the admin layout to hold together when compressed

  **What to do**:
  - Check collapse behavior, content wrapping, and nav accessibility at smaller sizes.
  - Make sure the design still works when the sidebar is narrower or hidden.
  - Fix any layout breakage surfaced by mobile-ish or laptop-width testing.

  **Must NOT do**:
  - Do not create a separate mobile app layout.
  - Do not change the route structure to solve responsiveness.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Responsive shell behavior needs careful interactive testing.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 7, 9)
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 1-6

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Responsive shell behavior.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts` - Sidebar collapse behavior.

  **Acceptance Criteria**:
  - [ ] Layout remains usable at smaller widths.
  - [ ] Sidebar collapse still works.
  - [ ] Content does not overflow or clip badly.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Shell remains usable at reduced width
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Resize viewport to a narrower desktop width.
      2. Verify the shell and sidebar still render correctly.
      3. Confirm content remains readable.
    Expected Result: The layout degrades gracefully instead of breaking.
    Evidence: .omo/evidence/task-8-responsive-shell.png

  Scenario: Sidebar collapse behaves on smaller screens
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Collapse the sidebar at smaller width.
      2. Navigate to another route.
      3. Verify the shell remains stable.
    Expected Result: Responsive behavior stays functional.
    Evidence: .omo/evidence/task-8-responsive-collapse.png
  ```

  **Evidence to Capture**:
  - [ ] `task-8-responsive-shell.png`
  - [ ] `task-8-responsive-collapse.png`

  **Commit**: YES | NO
  - Message: `fix(ui): harden responsive shell behavior`
  - Files: `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`, `apps/admin/src/app/layouts/admin-shell/admin-shell-nav.component.ts`
  - Pre-commit: `responsive QA + build`

- [x] 9. Final visual QA and build verification: run the redesign through diagnostics and evidence capture - expect a shippable frontend redesign plan

  **What to do**:
  - Run the app build and diagnostics.
  - Capture final screenshots for the shell and the representative pages.
  - Verify the redesign is stable enough to hand off.

  **Must NOT do**:
  - Do not leave the app in a partially themed state.
  - Do not ignore build or diagnostics failures.

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-high`
    - Reason: Final verification requires cross-cutting validation.
  - **Skills**: `[]`
    - No extra skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 7, 8)
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 1-8

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - Final shell target.
  - `apps/admin/src/app/features/dashboard/dashboard-page.component.ts` - Final dashboard check.
  - `apps/admin/src/app/features/users/users-page.component.ts` - Final data-page check.

  **Acceptance Criteria**:
  - [ ] Build passes.
  - [ ] Diagnostics are clean or only have understood, non-blocking issues.
  - [ ] Final screenshots are captured for review.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Final build and diagnostics pass
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Run the project build.
      2. Run diagnostics if available.
      3. Confirm there are no blocking errors.
    Expected Result: Build and diagnostics support shipping the redesign.
    Evidence: .omo/evidence/task-9-build-check.txt

  Scenario: Final screenshot set captures the redesigned frontend
    Tool: Playwright
    Preconditions: App running locally
    Steps:
      1. Capture the shell.
      2. Capture the dashboard.
      3. Capture the table-heavy page.
    Expected Result: Final evidence exists for the handoff.
    Evidence: .omo/evidence/task-9-final-shots.png
  ```

  **Evidence to Capture**:
  - [ ] `task-9-build-check.txt`
  - [ ] `task-9-final-shots.png`

  **Commit**: YES | NO
  - Message: `chore(ui): finalize frontend redesign verification`
  - Files: `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts`, `apps/admin/src/app/features/dashboard/dashboard-page.component.ts`, `apps/admin/src/app/features/users/users-page.component.ts`, `apps/admin/src/styles.css`
  - Pre-commit: `full build + screenshot sweep`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .omo/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run diagnostics + build. Review all changed files for regressions, over-complicated styling, and accidental scope creep.
  Output: `Build [PASS/FAIL] | Diagnostics [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute the QA scenarios from every task and capture evidence in `.omo/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: verify 1:1 that only the stated pages/files changed. Flag any contamination or unrelated rewrites.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `feat(ui): refresh admin shell layout` - `admin-shell.component.ts`, `build + targeted UI check`
- **2**: `feat(ui): refresh sidebar navigation` - `admin-shell-nav.component.ts`, `build + targeted UI check`
- **3**: `feat(ui): update shared admin page styles` - `admin-page-styles.ts`, `build + targeted UI check`
- **4**: `feat(ui): redesign dashboard baseline` - `dashboard-page.component.ts`, `build + targeted UI check`
- **5**: `feat(ui): restyle data-dense admin page` - `users-page.component.ts`, `build + targeted UI check`
- **6**: `feat(ui): align global theme overrides` - `styles.css`, `build + targeted UI check`
- **7**: `refactor(ui): align frontend redesign across screens` - shell + validated pages, `visual QA + build`
- **8**: `fix(ui): harden responsive shell behavior` - shell + nav, `responsive QA + build`
- **9**: `chore(ui): finalize frontend redesign verification` - shell + representative pages, `full build + screenshot sweep`

---

## Success Criteria

### Verification Commands
```bash
# Example commands the executor should run
build command  # Expected: passes
playwright or browser QA  # Expected: renders new shell and representative pages correctly
diagnostics command  # Expected: no blocking errors
```

### Final Checklist
- [ ] Shell and nav reflect the Linear hybrid direction
- [ ] Shared styles support the new visual system
- [ ] Dashboard and at least one table-heavy page prove the system works
- [ ] Responsive behavior is acceptable
- [ ] Build and visual QA pass
