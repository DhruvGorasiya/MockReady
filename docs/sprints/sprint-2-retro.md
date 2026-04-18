# Sprint 2 — Retrospective

**Sprint dates:** 2026-04-07 → 2026-04-21
**Retro date:** 2026-04-18

---

## What We Shipped

- Coach score override endpoint and UI (`/review` page)
- Full CI/CD pipeline: lint, typecheck, backend/frontend tests, security scan (npm audit + gitleaks), E2E Playwright tests, AI review, Vercel preview + production deploy
- 2 custom Claude Code skills: `review-endpoint` (v1→v2) and `create-pr`
- 2 hooks: PostToolUse (ruff lint on .py edit) + Stop (pytest gate)
- `.mcp.json` with Playwright MCP server
- `.claude/agents/security-reviewer.md` — OWASP Top 10 audit agent
- CLAUDE.md refactored with `@imports` into 6 modular docs files
- OWASP Top 10 documented in `docs/security.md`
- Parallel feature development via git worktrees (`feature/vercel-deployment` + `feature/sprint-docs`)

---

## What Went Well

- **CI/CD came together fast.** The GitHub Actions workflow was written and passing within a single session using Claude Code.
- **`security-reviewer` agent caught real issues.** Running the OWASP audit agent on the sessions route surfaced the missing role check on the coach override endpoint before it went to PR.
- **`create-pr` skill saved time on every PR.** The C.L.E.A.R. + AI disclosure template is now the default — no PR goes out without it.
- **Worktrees proved their value.** Working on `vercel.json` and sprint docs simultaneously in separate worktrees meant no context switching or branch juggling.
- **`@imports` in CLAUDE.md keeps context clean.** Each session now loads only the relevant docs rather than a 300-line monolith.

---

## What Didn't Go Well

- **Vercel deploy not yet live.** `vercel.json` is written but the Vercel project isn't linked to GitHub yet — secrets (`VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`) need to be added to GitHub. Carrying forward.
- **Feedback agent scores gap still open.** The `scores={}` / `reasoning={}` issue from Sprint 1 wasn't addressed this sprint — deprioritized in favour of CI/CD and rubric requirements.
- **No `GET /api/v1/auth/me` endpoint.** Frontend can't fetch current user profile; role-aware redirects are a partial workaround.

---

## Action Items (Post-Sprint / Hardening)

| Action | Owner | Priority |
|---|---|---|
| Link Vercel project to GitHub, add secrets | Dhruv | High |
| Fix feedback agent to pass evaluated scores | Dhruv | Medium |
| Add `GET /api/v1/auth/me` endpoint | Dhruv | Low |
| Write technical blog post | Dhruv | High (deliverable) |
| Record 5-10 min video demo | Dhruv | High (deliverable) |

---

## Team Health

- Solo sprint — velocity held steady
- Claude Code worktree + skills + agents workflow is now the default — no going back to manual PRs
