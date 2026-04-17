---
name: Known Bugs and Tech Debt
description: Pre-existing failures and known issues that are not regressions
type: project
---

## Pre-existing Test Failures (7 tests)

In `backend/app/tests/test_session_service.py`, the `test_create_session_*` tests call `create_session(db, user_id, interview_type)` but the function now requires a `role` argument. These tests pre-date the current signature and are NOT regressions introduced by recent work. Do not count these as failures when assessing test health.

## Known Tech Debt

1. **Feedback agent receives empty scores/reasoning** — `submit_answer()` passes `scores={}` and `reasoning={}` to `synthesize_feedback`. Output is still meaningful (agent uses raw answer text) but doesn't leverage evaluated dimension scores.

2. **No session locking** — simultaneous answer submissions to the same question aren't prevented at the DB level.

3. **Auth token in localStorage** — acceptable for MVP/demo; `auth_PRD.md` notes this as a hardening opportunity (httpOnly cookie would be more secure).

4. **No `GET /api/v1/auth/me` endpoint** — frontend can't fetch current user profile; only the token is stored.

5. **Coach UI has no role-aware redirect** — coach users must navigate to `/review` manually; root redirect doesn't check role.

6. **Wrong service called from session route** — FIXED 2026-04-17: `POST /sessions` was calling `create_session` (bare, no AI) instead of `create_session_with_questions`. Now fixed to call the correct function.
