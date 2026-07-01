# Draft: Frontend Redesign

## Requirements (confirmed)
- User wants to "thực hiện lên plan thiết kế lại frontend".
- Current repo is an Angular 21 admin app with ng-zorro-antd, Tailwind v4, and a protected admin shell.
- A layout rebuild is possible and should focus on shell, sidebar, shared page styles, then representative screens.

## Technical Decisions
- Recommend a Linear-style dark admin shell as the base layout.
- Optionally borrow a light Voltagent-style AI/devtool accent.
- User selected the visual direction: Linear hybrid.
- Keep auth, permission guards, and routes intact unless information architecture changes.

## Research Findings
- Current UI has a clear shell: `admin-shell.component.ts`, `admin-shell-nav.component.ts`, shared styles in `admin-page-styles.ts`.
- The safest high-leverage files are the shell, nav, shared styles, and `styles.css`.
- `awesome-design-md` works best as a design constitution source, not a direct copy-paste layout.

## Open Questions
- Which visual direction do you want: closer to Linear, closer to Voltagent, or a custom hybrid?
- Do you want only a visual redesign, or also a navigation / information architecture reshuffle?
- Should we include a design doc only, or also a concrete implementation plan next?

## Scope Boundaries
- INCLUDE: layout, navigation, shell, shared component styling, dashboard baseline.
- EXCLUDE: auth logic, permission logic, backend APIs, unrelated feature rewrites.