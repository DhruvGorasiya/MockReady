# Project 3 Requirements Audit

Last updated: 2026-04-17

---

## Compliance Scorecard

| Requirement | Status | Notes |
|---|---|---|
| **CLAUDE.md with `@imports`** | Partial | Exists, comprehensive — but no `@imports` for modular organization |
| **Auto-memory system** | Yes ✓ | `.claude/MEMORY.md` index + 7 memory files created |
| **2+ Custom Skills** | Yes ✓ | `review-endpoint` (v1→v2) + `create-pr` (C.L.E.A.R. + AI disclosure) |
| **2+ Hooks (PreToolUse/PostToolUse + Stop)** | Yes ✓ | PostToolUse (ruff lint on .py edit) + Stop (pytest gate) |
| **1+ MCP Server with `.mcp.json`** | Yes ✓ | `.mcp.json` at repo root configures Playwright MCP server |
| **Custom Agents (`.claude/agents/`)** | Yes ✓ | `security-reviewer` agent — OWASP Top 10 audit, no code modification |
| **Worktree / Parallel Development** | No | Only `main` branch, no worktrees |
| **TDD (red-green-refactor)** | Yes ✓ | Strong — 18 test files, commits labeled red/green/refactor |
| **E2E Tests (Playwright)** | Yes ✓ | `playwright.config.ts` + 3 auth E2E tests passing locally and in CI |
| **70%+ Test Coverage** | Yes ✓ | Backend 70% enforced via pytest-cov; frontend 70% enforced via Jest threshold |
| **CI/CD (GitHub Actions, all 8 stages)** | Yes ✓ | Full pipeline: lint, typecheck, unit tests, security scan, gitleaks, E2E, AI review, Vercel deploy |
| **Security (4 of 8 gates)** | Yes ✓ | `npm audit --audit-level=critical` + Gitleaks secrets scan in CI |
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

- [x] **CI/CD Pipeline** — `.github/workflows/ci.yml` with lint, typecheck, tests, security scan, Vercel deploy
- [x] **2nd Custom Skill** — `create-pr` skill with C.L.E.A.R. + AI disclosure metadata
- [x] **2+ Hooks** — PostToolUse (ruff lint on .py edit) + Stop (pytest gate)
- [x] **`.mcp.json`** — Playwright MCP server config at repo root
- [ ] **Deployment** — `vercel.json` + deploy to Vercel for a public URL
- [x] **E2E Tests** — at least 1 Playwright test

### Medium Priority

- [x] **Claude Code Agents** — `security-reviewer` agent (OWASP Top 10 audit)
- [ ] **`CLAUDE.md` `@imports`** — split into modular files and use `@docs/conventions.md` etc.
- [ ] **OWASP Top 10** section added to `CLAUDE.md`
- [ ] **Security tooling** — gitleaks pre-commit config, `npm audit` in CI

### Documentation / Process

- [ ] Sprint 1 + Sprint 2 planning and retro docs
- [ ] Async standup logs (3+ per sprint per partner)
- [ ] GitHub Issue templates with acceptance criteria
- [ ] Technical blog post (Medium / dev.to)
- [ ] Video demonstration (5–10 min)
