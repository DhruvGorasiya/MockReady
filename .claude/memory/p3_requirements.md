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
- [ ] CI/CD — `.github/workflows/ci.yml` (lint, typecheck, tests, security scan, Vercel deploy)
- [ ] Deployment — `vercel.json` + live Vercel URL
- [ ] 2nd Custom Skill in `.claude/skills/`
- [ ] 2+ Hooks in `.claude/settings.json` (PreToolUse/PostToolUse + Stop hook)
- [ ] `.mcp.json` at repo root documenting Playwright MCP
- [ ] E2E test (at least 1 Playwright test)

### Should Build
- [ ] `.claude/agents/` with at least 1 sub-agent (e.g., `test-writer`, `security-reviewer`)
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
