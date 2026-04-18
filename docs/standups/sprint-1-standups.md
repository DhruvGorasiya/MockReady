# Sprint 1 — Async Standup Logs

**Sprint dates:** 2026-03-24 → 2026-04-07

---

## Standup 1 — 2026-03-24

**Done:**
- Project scaffolding: Next.js 14 App Router + FastAPI boilerplate
- Supabase project created, Session Pooler connection string configured
- SQLAlchemy async engine setup with `asyncpg`
- Initial Alembic migration: `users` table

**Doing:**
- Auth endpoints: `POST /api/v1/auth/register` and `POST /api/v1/auth/login`
- Writing failing tests for auth service first (TDD — red phase)

**Blockers:**
- None

---

## Standup 2 — 2026-03-27

**Done:**
- Auth service tests written (red) and implementation passing (green)
- JWT signing with HS256, bcrypt password hashing (passlib removed — version incompatibility with Python 3.13, using bcrypt directly)
- `get_current_user` FastAPI dependency injector complete
- Frontend login/register pages with form validation

**Doing:**
- Session creation endpoint + Question Generation Agent
- Alembic migration for `sessions` and `session_questions` tables
- Writing agent tests with mocked Anthropic API responses

**Blockers:**
- None

---

## Standup 3 — 2026-03-31

**Done:**
- Question Generation Agent complete — generates 5 role/type-specific questions via Claude API
- `POST /api/v1/sessions` creates session + snapshots questions into DB
- Agent logging: agentId, input, output, latency, model version, timestamp
- 18 backend tests passing (auth + session creation)

**Doing:**
- Answer submission endpoint
- Answer Evaluation Agent (5-dimension scoring)
- Feedback Synthesis Agent
- Running Evaluation + Feedback concurrently with `asyncio.gather()`

**Blockers:**
- None

---

## Standup 4 — 2026-04-03

**Done:**
- Answer Evaluation Agent complete — returns scores 1-10 per dimension
- Feedback Synthesis Agent complete — generates behavioral feedback per dimension
- Both agents run concurrently via `asyncio.gather()` in `submit_answer()`
- `EvaluationScore` model stores both `ai_score` and `coach_score`
- 40 backend tests passing

**Doing:**
- Candidate dashboard frontend (session list + per-session score view)
- `GET /api/v1/sessions` and `GET /api/v1/sessions/{id}` endpoints

**Blockers:**
- Feedback agent receives empty `scores={}` and `reasoning={}` — deferred, agent still produces useful output from raw answer text

---

## Standup 5 — 2026-04-07

**Done:**
- Candidate dashboard complete — lists past sessions with composite scores
- Session detail view with per-question breakdown
- 76 backend tests, 51 frontend tests — all passing
- Sprint 1 retrospective written

**Doing:**
- Sprint 2 planning
- Coach role implementation

**Blockers:**
- None
