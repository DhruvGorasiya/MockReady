# Sprint 2 — Planning

**Sprint dates:** 2026-04-07 → 2026-04-21
**Goal:** Ship the coach role, CI/CD pipeline, deployment, and all Claude Code mastery requirements (skills, hooks, MCP, agents, worktrees).

---

## Team

| Name | Role |
|---|---|
| Dhruv Gorasiya | Full-stack developer |

---

## Sprint Goal

A coach can log in, view candidate sessions, and override AI scores. The CI/CD pipeline runs on every PR with lint, tests, security scan, and Vercel preview deploy. All p3 rubric requirements (skills, hooks, MCP, agents, worktrees) are implemented and evidenced.

---

## User Stories

### US-5: Coach Score Override
**As a** coach
**I want to** review a candidate's answer and override the AI score
**So that** human judgement can correct AI errors and build ground-truth data

**Acceptance criteria:**
- [ ] `PATCH /api/v1/sessions/{id}/scores/{score_id}` accepts `coach_score` (1-10)
- [ ] Both `ai_score` and `coach_score` are stored — neither is overwritten
- [ ] Coach score is authoritative in composite calculation when present
- [ ] Only users with `role == "coach"` can call this endpoint (403 otherwise)
- [ ] Coach review UI at `/review` lists sessions pending review

---

### US-6: CI/CD Pipeline
**As a** developer
**I want** every PR to run automated checks
**So that** broken code never reaches `main`

**Acceptance criteria:**
- [ ] `.github/workflows/ci.yml` runs on every PR and push to `main`
- [ ] Stages: lint (ruff + ESLint), typecheck, backend tests, frontend tests, security scan (npm audit + gitleaks), E2E (Playwright), AI review, Vercel preview deploy
- [ ] All stages must pass before merge
- [ ] Coverage thresholds enforced (70% backend, 70% frontend)

---

### US-7: Claude Code Mastery — Skills, Hooks, MCP, Agents
**As a** developer
**I want** Claude Code configured with skills, hooks, MCP servers, and custom agents
**So that** the development workflow is automated and auditable

**Acceptance criteria:**
- [ ] 2+ skills in `.claude/skills/` with evidence of v1→v2 iteration
- [ ] 2+ hooks in `.claude/settings.json` (PostToolUse: ruff lint; Stop: pytest gate)
- [ ] `.mcp.json` configures Playwright MCP at repo root
- [ ] `.claude/agents/security-reviewer.md` performs OWASP Top 10 audit
- [ ] CLAUDE.md uses `@imports` for modular organization

---

### US-8: Vercel Deployment
**As a** user
**I want** MockReady accessible via a public URL
**So that** I can use it from any device

**Acceptance criteria:**
- [ ] `vercel.json` at repo root configures frontend deployment
- [ ] Vercel project linked to GitHub repo
- [ ] Preview deploys on every PR
- [ ] Production deploy on merge to `main`
- [ ] `NEXT_PUBLIC_API_URL` environment variable points to backend

---

## Definition of Done

- Code merged to `main` via PR (no direct pushes)
- All acceptance criteria checked off
- TDD workflow maintained for all new service/agent code
- CI pipeline passes end-to-end
- Public Vercel URL accessible

---

## Velocity / Estimates

| Story | Points |
|---|---|
| US-5: Coach score override | 8 |
| US-6: CI/CD pipeline | 5 |
| US-7: Claude Code mastery | 8 |
| US-8: Vercel deployment | 3 |
| **Total** | **24** |
