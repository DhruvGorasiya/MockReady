---
name: Project 3 Rubric Gaps
description: What's missing for the p3.md grade requirements and what still needs to be built
type: project
---

Audited 2026-04-17. Full details in `docs/p3-audit.md`.

## Already Done
- TDD with red/green/refactor commits ✓
- CLAUDE.md with architecture, conventions, do's/don'ts ✓
- 1 skill (`review-endpoint`) with v1→v2 iteration ✓
- 76 backend + 51 frontend tests ✓
- Dual roles (candidate + coach) ✓

## Still Needed

### Must Build (blocking grade)
- [x] CI/CD — `.github/workflows/ci.yml` (lint, typecheck, tests, security scan, Vercel deploy) ✓ DONE
- [ ] Deployment — `vercel.json` + live Vercel URL
- [x] 2nd Custom Skill — `create-pr` with C.L.E.A.R. + AI disclosure ✓ DONE
- [x] 2+ Hooks in `.claude/settings.json` (PostToolUse: ruff lint on .py edit; Stop: pytest gate) ✓ DONE
- [x] `.mcp.json` at repo root documenting Playwright MCP ✓ DONE
- [ ] E2E test (at least 1 Playwright test)

### Should Build
- [x] `.claude/agents/` — `security-reviewer` agent (OWASP Top 10) ✓ DONE
- [ ] `CLAUDE.md` refactored to use `@imports` for modular organization
- [ ] OWASP Top 10 section added to `CLAUDE.md`
- [ ] Gitleaks pre-commit config + `npm audit` in CI

### Documentation
- [ ] Sprint 1 + Sprint 2 planning and retro docs
- [ ] Async standup logs
- [ ] Technical blog post
- [ ] 5–10 min video demo

**Why:** These are graded requirements for the Northeastern course project (19% of final grade).
**How to apply:** Prioritize CI/CD and deployment first — they unlock the most points and are prerequisites for other deliverables.
