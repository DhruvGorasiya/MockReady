# Sprint 2 — Async Standup Logs

**Sprint dates:** 2026-04-07 → 2026-04-21

---

## Standup 1 — 2026-04-07

**Done:**
- Sprint 2 planning doc written (US-5 through US-8)
- Coach role: `PATCH /api/v1/sessions/{id}/scores/{score_id}` endpoint (TDD — red phase tests written first)

**Doing:**
- Implementing coach score override service + route
- Role-based access control check (`user.role == "coach"`)

**Blockers:**
- None

---

## Standup 2 — 2026-04-10

**Done:**
- Coach score override complete — `coach_score` stored alongside `ai_score`, neither overwritten
- Coach review UI at `/review` — lists sessions pending review
- `POST /sessions` bug fixed: was calling `create_session` (bare) instead of `create_session_with_questions` — now calls correct function
- 7 stale `test_create_session_*` tests identified (stale signature, not regressions) — documented in known_bugs.md

**Doing:**
- CI/CD pipeline — `.github/workflows/ci.yml`
- Writing `review-endpoint` skill (v1) for Claude Code

**Blockers:**
- None

---

## Standup 3 — 2026-04-14

**Done:**
- CI/CD pipeline live: lint (ruff + ESLint + Prettier), typecheck, backend tests, frontend tests, security scan (npm audit + gitleaks), E2E (Playwright), AI review, Vercel preview + prod deploy
- `review-endpoint` skill v1 written; iterated to v2 after first real use (added input validation findings section)
- `create-pr` skill written with C.L.E.A.R. + AI disclosure metadata
- PostToolUse hook (ruff lint on .py edit) + Stop hook (pytest gate) configured in `.claude/settings.json`

**Doing:**
- `.mcp.json` Playwright MCP configuration
- `security-reviewer` agent (OWASP Top 10)

**Blockers:**
- None

---

## Standup 4 — 2026-04-17

**Done:**
- `.mcp.json` added at repo root — Playwright MCP server configured
- `security-reviewer` agent complete — audits new routes for OWASP Top 10
- 3 E2E Playwright tests passing (auth flow: register, login, logout)
- p3-audit.md updated: CI/CD, skills, hooks, MCP, agents all checked off

**Doing:**
- CLAUDE.md `@imports` refactor
- OWASP Top 10 section in `docs/security.md`

**Blockers:**
- None

---

## Standup 5 — 2026-04-18

**Done:**
- CLAUDE.md refactored into 6 modular docs files with `@imports`
- OWASP A01–A10 documented with MockReady-specific guidance in `docs/security.md`
- Git worktrees created: `feature/vercel-deployment` + `feature/sprint-docs` for parallel development
- `vercel.json` written for frontend deployment
- Sprint docs (planning + retro for both sprints) + standup logs written

**Doing:**
- Linking Vercel project to GitHub repo and adding secrets
- Merging both feature branches

**Blockers:**
- Need to create Vercel project and obtain `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` to complete deployment
