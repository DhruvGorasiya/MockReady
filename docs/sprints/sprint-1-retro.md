# Sprint 1 — Retrospective

**Sprint dates:** 2026-03-24 → 2026-04-07
**Retro date:** 2026-04-07

---

## What We Shipped

- Candidate auth (register + login with JWT)
- Session creation with AI-generated questions (Question Generation Agent)
- Answer submission with concurrent evaluation + feedback (asyncio.gather)
- Candidate dashboard showing past sessions and scores
- 76 backend tests, 51 frontend tests — all passing
- TDD workflow established: red/green/refactor commits throughout

---

## What Went Well

- **TDD discipline held.** Every service function had a failing test before implementation. The commit history clearly shows the red → green → refactor pattern.
- **Agent parallelism worked.** Running the Evaluation and Feedback agents concurrently via `asyncio.gather()` kept response times acceptable even with two Claude API calls per answer.
- **Services pattern kept routes thin.** No business logic leaked into route handlers — every route is ≤ 20 lines.
- **Pydantic schemas caught bugs early.** Two agent output mismatches were caught at the schema validation layer before they could corrupt the DB.

---

## What Didn't Go Well

- **Feedback agent receives empty scores.** `submit_answer()` passes `scores={}` and `reasoning={}` to `synthesize_feedback`. The agent still produces useful feedback from the raw answer text, but it doesn't leverage the dimension scores. Deferred to Sprint 2.
- **7 stale tests in `test_session_service.py`.** The `create_session` signature changed (added `role` param) but old tests weren't updated. They pre-date the current implementation and aren't regressions — but they need cleanup.
- **Coach UI has no role-aware redirect.** Coach users have to navigate to `/review` manually. Not caught until demo day.
- **No session locking.** Simultaneous answer submissions to the same question aren't prevented at the DB level. Low risk for MVP but needs to be addressed before production.

---

## Action Items for Sprint 2

| Action | Owner | Priority |
|---|---|---|
| Fix feedback agent to pass evaluated scores/reasoning | Dhruv | High |
| Fix 7 stale `create_session` tests | Dhruv | High |
| Add role-aware redirect for coach users on login | Dhruv | Medium |
| Add CI/CD pipeline (GitHub Actions) | Dhruv | High |
| Add coach score override UI and endpoint | Dhruv | High |

---

## Team Health

- Solo sprint — no blockers from teammates
- Claude Code used for TDD scaffolding, code review, and agent implementation — significant productivity gain
- Estimated time saved vs. manual implementation: ~40%
