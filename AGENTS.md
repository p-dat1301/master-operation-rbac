<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **master-operation-rbac** (6396 symbols, 12543 relationships, 159 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/master-operation-rbac/context` | Codebase overview, check index freshness |
| `gitnexus://repo/master-operation-rbac/clusters` | All functional areas |
| `gitnexus://repo/master-operation-rbac/processes` | All execution flows |
| `gitnexus://repo/master-operation-rbac/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

<!-- gstack:start -->
## gstack

gstack skills are installed. Use these slash commands for AI-assisted development.

### Quick start flow
| When | Short alias | Full command |
|------|-------------|--------------|
| Product diagnostic / office hours | `/oh` | `/gstack-office-hours` |
| Architecture / eng review plan | `/eng-review` | `/gstack-plan-eng-review` |
| Code review before shipping | `/review` | `/gstack-review` |
| Browser QA (local app at :3000) | `/qa-local` | `/gstack-qa http://localhost:3000` |
| Release and PR workflow | `/ship` | `/gstack-ship` |
| Security audit (auth/payment/admin) | `/cso` | `/gstack-cso` |
| Open gstack browser | `/browse` | `/gstack-open-gstack-browser` |

### Browser
Use `/gstack-browse` or `/gstack-open-gstack-browser` for browser automation.
Never use unrelated MCP browser tools.

### Note
gstack skills are namespaced with `gstack-` prefix (e.g. `/gstack-office-hours`).
<!-- gstack:end -->
