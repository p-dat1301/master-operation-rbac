# Agentic frontend/admin redesign notes

## 2026-06-22 - Agentic DTO coverage

- Mirrored backend `agentic_schema.py` DTOs in `apps/admin/src/app/models/agentic.models.ts` for conversation create/summary/response/list, message/list, chat request/response, document upload request/response, document summary/list.
- Removed redundant private agentic list/payload/request interfaces from `AgenticApiService` by importing the shared exported model contracts.
- Kept changes model/service-only; backend schemas, UI, and routing were not changed.

## 2026-06-22 - Admin shell nav grouping

- Reassigned admin shell navigation items into readable groups: Workspace, Agent/AI, Organization, Access Control, Operations, Security, and Advanced/Admin tools.
- Preserved direct routes and permission checks for `/config/menu-sync` and `/config/i18n-sync`; only their nav grouping changed so they remain behind `system.config.manage`.
- Left `AdminShellNavComponent.navSections` unchanged because it already groups by `ShellNavItem.group` and renders the new labels automatically.

## 2026-06-22 - Agentic documents page

- Implemented `/agentic/documents` as a standalone documents workspace with list, detail preview, and upload modal flows wired to `AgenticApiService.getDocuments()`, `getDocument(documentId)`, and `uploadDocument(file, policy)`.
- Added loading, empty, and error states for list/detail views and kept the upload action behind the existing `manage_org` permission check from `AuthStoreService`.
- Enforced client-side policy validation so role-scoped uploads require `allowed_roles` and department-scoped uploads require `department_id` before submit; upload payload continues to travel as `FormData` through the service.
- Reused shared admin surface/text tokens from `admin-page-styles.ts` for the page chrome and panels.

## 2026-06-22 - Breadcrumb hierarchy consistency

- Updated shell route breadcrumbs to mirror the grouped sidebar taxonomy so page titles and crumbs stay aligned with the new navigation structure.
- Kept route paths and permission keys intact; only display hierarchy changed for Admin, Workspace, Agent/AI, Organization, Access Control, Operations, Security, and Advanced/Admin tools.
- Verified collapsed sidebar still hides section labels via the existing template guard while retaining icon-only navigation.

## 2026-06-22 - Agentic conversation history UI

- Expanded `AgenticConversationsPageComponent` from a stub into an API-backed list/detail/message-history screen using existing `AgenticApiService.getConversations`, `getConversation`, and `getConversationMessages`.
- Added independent loading, empty, error, retry, and not-found states for list, detail, and persisted message history without changing routes, service methods, or model contracts.
- Styled the page with shared admin contrast tokens from `ADMIN_PAGE_COMMON_STYLES`; `apps/admin && npm run build` passes.

## 2026-06-22 - Conversation-aware chat rollout

- Upgraded `ChatWindowComponent` to keep quick chat as the default path while routing selected conversations through `chatInConversation(conversationId, message, topK)`.
- Added a conversation selector that loads from `getConversations()`, a backend-ranged `top_k` control capped client-side to 1–10, and explicit loading/error state for both conversation loading and message sending.
- Rendered assistant response metadata inline, including `status`, `conversation_id`, `thread_id`, `cited_chunk_ids`, `cited_document_ids`, and structured `citations` when present.
- Matched the new UI with shared admin contrast tokens and kept the existing `/chat` route and quick chat behavior intact.

## 2026-06-22 - Admin readability audit cleanup

- Replaced repeated hardcoded text/surface colors on users, roles, permissions, audit logs, tasks, leaves, notifications, and departments pages with shared `ADMIN_PAGE_COMMON_STYLES` tokens/classes where practical.
- Kept layout changes light and readability-driven only: tighter modal grouping, clearer detail toolbar spacing, and safer shared semantic color usage for table content and action controls.
- Confirmed system error pages (`forbidden`, `not-found`, `unauthorized`) remain low-risk route-only shells and did not need structural changes for contrast cleanup.

## 2026-06-22 - Agentic integration state polish

- Normalized agentic document list/detail/upload failures through `runAdminAsync()` so backend-down, forbidden, and validation failures render explicit inline state panels and toast messages instead of console-only errors.
- Added missing not-found/unavailable states for refreshed conversation and document selections so removed or inaccessible records no longer leave stale detail panes or infinite loading.
- Hardened chat send/conversation-loading failures with visible error panels, loading indicators, preserved failed input text for retry, and no unhandled promise path while keeping quick chat as the default.

## 2026-06-22 - Advanced/Admin sync tool placement refinement

- Verified `AdminShellComponent.allNavItems` still places `Menu sync` and `i18n sync` in `group: 'Advanced/Admin tools'` as the final sidebar entries, keeping them visually secondary but discoverable for admins with `system.config.manage`.
- Confirmed direct routes remain intact: `app.routes.ts` still resolves `/config/menu-sync` and `/config/i18n-sync` to their standalone sync page components with the existing `permissionGuard('system.config.manage')`.
- Kept breadcrumb/title consistency by preserving `Admin > Advanced/Admin tools > Menu sync` and `Admin > Advanced/Admin tools > i18n sync`; reordered the shell route metadata list so the advanced tools also stay last in display metadata.
- Verified with `cd apps/admin && npm run build`.

## 2026-06-22 - Cross-page contrast regression cleanup

- Finished the remaining Task 9 follow-up on users, roles, permissions, departments, attendance, notifications, audit logs, tasks, and leaves by pulling repeated page-root/header/filter/table typography back onto `ADMIN_PAGE_COMMON_STYLES` where those pages still carried one-off text and surface declarations.
- Standardized dark table/header/modal copy to `--admin-text-primary|strong|secondary|muted`, aligned unread/action emphasis to shared admin action tokens, and swapped page-local card/field backgrounds back to the shared surface tokens rather than light-mode hex values.
- Left semantic status-tinted chips in place where they communicate state, but removed avoidable duplicate header/card scaffolding and preserved page structure/functionality unchanged.

## 2026-06-22 - Task 14 route regression sweep

- `apps/admin && npm run build` passes, backend was already listening on `127.0.0.1:8010`, and frontend dev server was already listening on `127.0.0.1:4200`.
- Browser regression logged in with `admin@company.vn / Admin@123` and direct-loaded `/chat`, `/agentic/conversations`, `/agentic/documents`, `/users`, `/rbac/roles`, `/audit-logs`, `/config/menu-sync`, and `/config/i18n-sync` without 404, forbidden, or unauthorized redirects.
- Evidence and screenshots were saved at `.omo/evidence/task-14-route-regression.md` and `.omo/evidence/task-14-screenshots/`; readable dark/admin text and direct Advanced/Admin tool access were verified.

## 2026-06-22 - Final verification wave F2 findings

- `apps/admin && npm run build` passes.
- `apps/admin && npm run test:unit` passes after using the correct script; `npm run test:unit -- --runInBand` failed because Angular CLI does not accept `--runInBand`.
- `apps/admin` has no `lint` script, so lint verification is currently unavailable from package scripts.
- Quality issue found: `apps/admin/src/app/features/chat/agentic-documents-page.component.ts` still hardcodes `#fecaca` in `.error-state`, which bypasses the shared admin contrast token plan.
- No `as any`, `@ts-ignore`, empty catches, or console logs were found in the changed frontend files reviewed.
- LSP diagnostics were clean for the changed TypeScript files reviewed.

## 2026-06-22 - F4 scope fidelity issues

- Final commit `74797ef` is not scope-faithful to the plan: the diff includes broad backend/platform work (`app/agentic/**`, migrations, tests, docker/env/config changes, scripts) even though Task 14 commit strategy said the commit should contain admin frontend files from Waves 1-3.
- Unaccounted frontend expansion also exists beyond the explicitly required agentic/nav/contrast scope, including CRUD/features for users, tasks, attendance, departments, and supporting APIs/specs that were not deliverables in Tasks 1-14.
- No accidental removal of `/config/menu-sync` or `/config/i18n-sync` was found; both remain routed and grouped under `Advanced/Admin tools`, and no forbidden route rename was detected in the inspected admin shell routes.
- Verdict basis: reject for contamination/unaccounted changes, not for missing menu/i18n availability.

## 2026-06-22 - Sidebar grouped-nav visibility bug

- Reproduced the browser symptom before the fix: the live sidebar accessibility tree exposed only the `Workspace` section even though `AdminShellComponent.navItems` still included permission-free `Agent/AI` entries.
- Root cause was layout/rendering in `AdminShellNavComponent`, not route filtering: separate grouped menus were not housed in a dedicated full-height scroll container, so later sections were effectively lost in the visible sider.
- Wrapped the grouped nav sections in a flex column with a scrollable middle region so all eligible groups render in order, with `Workspace` first, `Agent/AI` immediately after it for any authenticated user, and `Advanced/Admin tools` still gated by `system.config.manage`.
