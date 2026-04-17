# Project 3 Requirements Audit

Last updated: 2026-04-17

---

## Compliance Scorecard

| Requirement | Status | Notes |
|---|---|---|
| **CLAUDE.md with `@imports`** | Partial | Exists, comprehensive — but no `@imports` for modular organization |
| **Auto-memory system** | Yes ✓ | `.claude/MEMORY.md` index + 7 memory files created |
| **2+ Custom Skills** | Partial | Only 1 skill (`review-endpoint`); v1→v2 iteration exists ✓ |
| **2+ Hooks (PreToolUse/PostToolUse + Stop)** | No | `.claude/settings.json` only has permissions, no hooks |
| **1+ MCP Server with `.mcp.json`** | Partial | Playwright traces exist but no `.mcp.json` config file |
| **Custom Agents (`.claude/agents/`)** | No | App has AI agents (backend), but no Claude Code agents |
| **Worktree / Parallel Development** | No | Only `main` branch, no worktrees |
| **TDD (red-green-refactor)** | Yes ✓ | Strong — 18 test files, commits labeled red/green/refactor |
| **E2E Tests (Playwright)** | No | No `playwright.config.ts`, no e2e tests |
| **70%+ Test Coverage** | Partial | Good unit tests, but no coverage report generated |
| **CI/CD (GitHub Actions, all 8 stages)** | No | No `.github/workflows/` at all |
| **Security (4 of 8 gates)** | No | No gitleaks, no SAST, no formal tooling |
| **Deployed on Vercel** | No | No `vercel.json`, no public URL |
| **2 Sprints with planning + retros** | No | Tasks tracked but no sprint structure |
| **GitHub Issues + standups** | No | No issue templates, no standup logs |
| **Technical blog post** | No | Not found |
| **Video demo** | No | Not found |

---

## What's Done Well

- Strong **TDD** with red/green/refactor git commits
- Solid **CLAUDE.md** with architecture, conventions, do's/don'ts
- **1 skill** (`review-endpoint`) with v1→v2 iteration documented
- 76 backend + 51 frontend tests passing
- Coach + candidate dual roles fully implemented

---

## What Needs to Be Built

### High Priority (most points at risk)

- [ ] **CI/CD Pipeline** — `.github/workflows/ci.yml` with lint, typecheck, tests, security scan, Vercel deploy
- [ ] **2nd Custom Skill** — add one more in `.claude/skills/` (e.g., `/add-feature`, `/create-pr`)
- [ ] **2+ Hooks** — add in `.claude/settings.json` (e.g., auto-lint on edit, block pushes to main, run tests on stop)
- [ ] **`.mcp.json`** — document the Playwright MCP server config at repo root
- [ ] **Deployment** — `vercel.json` + deploy to Vercel for a public URL
- [ ] **E2E Tests** — at least 1 Playwright test

### Medium Priority

- [ ] **Claude Code Agents** — create `.claude/agents/` with a sub-agent (e.g., `test-writer`, `security-reviewer`)
- [ ] **`CLAUDE.md` `@imports`** — split into modular files and use `@docs/conventions.md` etc.
- [ ] **OWASP Top 10** section added to `CLAUDE.md`
- [ ] **Security tooling** — gitleaks pre-commit config, `npm audit` in CI

### Documentation / Process

- [ ] Sprint 1 + Sprint 2 planning and retro docs
- [ ] Async standup logs (3+ per sprint per partner)
- [ ] GitHub Issue templates with acceptance criteria
- [ ] Technical blog post (Medium / dev.to)
- [ ] Video demonstration (5–10 min)
