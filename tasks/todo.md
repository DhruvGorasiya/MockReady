# Task: Session History Dashboard (US-C04)

**PRD Reference:** US-C04 — View Session History Dashboard
**Branch:** `feature/session-history-dashboard`
**Status:** Phase 1 Complete — awaiting Phase 2 approval

---

## Acceptance Criteria (from PRD)

- [ ] Dashboard shows all past sessions with date, interview type, role, and composite score
- [ ] Per-session view shows dimension-level scores for each question
- [ ] Trend chart shows composite score over time (minimum last 10 sessions)
- [ ] Dimension-level trend visible per dimension (e.g., "Clarity over last 10 sessions")
- [ ] Dashboard loads within 2 seconds
- [ ] Empty state handled gracefully with a prompt to start a first session

---

## Implementation Plan

### Phase 1 — Backend Foundation (Data Models)

> These are the minimum models needed to serve the history endpoint. Full data-entry flows (session creation, answer submission) are out of scope for this task — we only need the read path.

- [x] **1.1** Bootstrap backend package: create `backend/pyproject.toml` with deps (`fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`, `pydantic-settings`, `psycopg2-binary`, `python-jose`, `pytest`, `pytest-asyncio`, `httpx`, `ruff`)
- [x] **1.2** Create `backend/app/__init__.py` and `backend/app/main.py` (FastAPI app bootstrap, router mounting, CORS)
- [x] **1.3** Create `backend/app/core/config.py` — pydantic-settings `Settings` class reading from env vars (`DATABASE_URL`, `SUPABASE_JWT_SECRET`, `ANTHROPIC_API_KEY`)
- [x] **1.4** Create `backend/app/core/db.py` — SQLAlchemy async engine + `AsyncSession` dependency
- [x] **1.5** Create `backend/app/core/security.py` — `get_current_user` FastAPI dependency (validates Supabase JWT)
- [x] **1.6** Create `backend/app/models/base.py` — declarative base
- [x] **1.7** Create `backend/app/models/user.py` — `User` ORM model (id, email, role, created_at)
- [x] **1.8** Create `backend/app/models/session.py` — `Session` ORM model (id, candidate_id, interview_type, role, status, rubric_version_id, started_at, completed_at, created_at)
- [x] **1.9** Create `backend/app/models/question.py` — `Question` and `SessionQuestion` ORM models
- [x] **1.10** Create `backend/app/models/evaluation_score.py` — `EvaluationScore` ORM model (ai_score + coach_score both stored; never deleted)
- [x] **1.11** Create `backend/app/models/rubric.py` — `RubricVersion` ORM model
- [x] **1.12** Create `backend/alembic/` setup (`alembic init`, configure `env.py` to use `DATABASE_URL` from env, point `target_metadata` at all ORM models)
- [x] **1.13** Migration file written manually (`64620107b2d5_initial_schema.py`); apply with `alembic upgrade head` once DB is available

---

### Phase 2 — Backend: Schemas

- [ ] **2.1** Create `backend/app/schemas/session.py`:
  - `SessionSummary` — id, interview_type, role, status, composite_score (float | None), created_at
  - `DimensionScores` — clarity, depth, structure, relevance, communication_quality (all int 1-10)
  - `QuestionResult` — question_text, candidate_answer, ai_scores: DimensionScores, coach_scores: DimensionScores | None, feedback: dict | None
  - `SessionDetail` — all SessionSummary fields + questions: list[QuestionResult]
  - `SessionHistoryResponse` — sessions: list[SessionSummary], total: int
  - `TrendPoint` — session_id, created_at, composite_score, dimension_scores: DimensionScores
  - `TrendResponse` — points: list[TrendPoint]

---

### Phase 3 — Backend: Service (TDD — write tests first)

- [ ] **3.1** Write failing tests in `backend/app/tests/test_session_service.py`:
  - `test_list_sessions_returns_empty_for_new_user`
  - `test_list_sessions_returns_sessions_for_candidate`
  - `test_list_sessions_only_returns_own_sessions`
  - `test_get_session_detail_returns_questions_and_scores`
  - `test_get_session_detail_raises_404_for_wrong_user`
  - `test_get_score_trends_returns_sorted_asc_by_date`
  - `test_get_score_trends_caps_at_last_10_sessions`
  - `test_composite_score_uses_coach_score_when_present`
- [ ] **3.2** Implement `backend/app/services/session_service.py`:
  - `async def list_sessions(db, candidate_id) -> list[SessionSummary]`
    - Query `Session` + join `EvaluationScore` to compute composite per session
    - Coach score is authoritative when present; fall back to ai_score
    - Return only `completed` and `reviewed` sessions (not in-progress/abandoned)
  - `async def get_session_detail(db, session_id, candidate_id) -> SessionDetail`
    - Raise `HTTPException(404)` if session not found or does not belong to candidate
    - Join `SessionQuestion` → `EvaluationScore` (both ai and coach rows)
  - `async def get_score_trends(db, candidate_id, limit=10) -> TrendResponse`
    - Return last `limit` completed sessions sorted ascending by `created_at`
    - Include both composite and per-dimension scores for trend chart rendering
- [ ] **3.3** Run tests — all should pass (`pytest backend/app/tests/test_session_service.py -v`)

---

### Phase 4 — Backend: Route Handler

- [ ] **4.1** Write failing tests in `backend/app/tests/test_sessions_router.py`:
  - `test_get_history_requires_auth` — expect 401 with no token
  - `test_get_history_returns_200_for_valid_candidate`
  - `test_get_history_empty_state_returns_empty_list`
  - `test_get_session_detail_404_for_other_candidate`
  - `test_get_trends_returns_trend_points`
- [ ] **4.2** Create `backend/app/api/v1/sessions.py` — thin route handlers only; all logic delegated to `session_service`:
  - `GET /api/v1/sessions/history` → `session_service.list_sessions`
  - `GET /api/v1/sessions/{session_id}` → `session_service.get_session_detail`
  - `GET /api/v1/sessions/trends` → `session_service.get_score_trends`
  - All routes use `get_current_user` dependency; candidate role required
- [ ] **4.3** Create `backend/app/api/v1/__init__.py` and `backend/app/api/__init__.py`; mount router in `main.py`
- [ ] **4.4** Create `backend/app/api/v1/health.py` — `GET /health` (no auth; liveness probe)
- [ ] **4.5** Run router tests — all should pass

---

### Phase 5 — Frontend Foundation

- [ ] **5.1** Bootstrap frontend: create `frontend/package.json` with Next.js 14, TypeScript, Tailwind CSS, Jest, RTL
- [ ] **5.2** Create `frontend/tsconfig.json`, `frontend/tailwind.config.ts`, `frontend/next.config.ts`, `frontend/jest.config.ts`
- [ ] **5.3** Create `frontend/app/layout.tsx` — root layout with Tailwind base styles
- [ ] **5.4** Create `frontend/lib/types/session.ts` — TypeScript types mirroring backend Pydantic schemas:
  - `DimensionScores`, `QuestionResult`, `SessionSummary`, `SessionDetail`, `TrendPoint`, `TrendResponse`
- [ ] **5.5** Create `frontend/lib/api/client.ts` — base fetch wrapper with auth header injection and error handling
- [ ] **5.6** Create `frontend/lib/api/sessions.ts` — typed API functions:
  - `getSessionHistory(): Promise<SessionHistoryResponse>`
  - `getSessionDetail(id: string): Promise<SessionDetail>`
  - `getScoreTrends(): Promise<TrendResponse>`

---

### Phase 6 — Frontend: Components (TDD)

- [ ] **6.1** Write failing tests in `frontend/__tests__/components/SessionCard.test.tsx`:
  - Renders session date, interview type, role, composite score
  - Shows "Pending" when composite score is null
- [ ] **6.2** Create `frontend/components/session/SessionCard.tsx` — single session row card
- [ ] **6.3** Write failing tests in `frontend/__tests__/components/TrendChart.test.tsx`:
  - Renders without crashing with 0 data points (empty state)
  - Renders with 10 data points
- [ ] **6.4** Create `frontend/components/session/TrendChart.tsx` — composite score over time line chart (use `recharts`)
- [ ] **6.5** Write failing tests in `frontend/__tests__/components/DimensionBreakdown.test.tsx`:
  - Renders all 5 dimension scores
  - Highlights coach score as authoritative when both ai and coach present
- [ ] **6.6** Create `frontend/components/session/DimensionBreakdown.tsx` — dimension score bar display
- [ ] **6.7** Write failing tests in `frontend/__tests__/components/EmptySessionState.test.tsx`:
  - Renders call-to-action to start first session
- [ ] **6.8** Create `frontend/components/session/EmptySessionState.tsx`

---

### Phase 7 — Frontend: Dashboard Page

- [ ] **7.1** Write failing tests in `frontend/__tests__/app/dashboard.test.tsx`:
  - Shows empty state when API returns 0 sessions
  - Renders session list when sessions exist
  - Renders trend chart with correct data
  - Shows loading state while fetching
  - Shows error state on API failure
- [ ] **7.2** Create `frontend/app/(candidate)/dashboard/page.tsx`:
  - Server component fetches session history and trend data
  - Passes data to `SessionCard` list and `TrendChart`
  - Handles empty state, loading state, error state
  - Per-PRD: must load within 2 seconds (verified via lighthouse or manual check)
- [ ] **7.3** Create `frontend/app/(candidate)/sessions/[id]/page.tsx`:
  - Fetches `SessionDetail` by id
  - Renders `DimensionBreakdown` per question
  - Shows coach score as authoritative (with label) when present
  - Navigation between questions

---

### Phase 8 — Verification

- [ ] **8.1** Run full backend test suite: `pytest backend/app/tests/ -v --cov=app` — target >80% on `services/` and `api/`
- [ ] **8.2** Run frontend tests: `npm test` from `frontend/` — all tests pass
- [ ] **8.3** Run linters: `ruff check backend/` and `npm run lint` from `frontend/` — zero errors
- [ ] **8.4** Manual smoke test: spin up backend + frontend, verify dashboard loads, empty state renders, and session drill-through works
- [ ] **8.5** Confirm all US-C04 acceptance criteria are met

---

## Architecture Notes

```
GET /api/v1/sessions/history
  └── sessions router (api/v1/sessions.py)
        └── session_service.list_sessions()
              └── SQLAlchemy query: Session JOIN SessionQuestion JOIN EvaluationScore
                    └── Returns SessionHistoryResponse (Pydantic)

GET /api/v1/sessions/trends
  └── sessions router
        └── session_service.get_score_trends()
              └── Last 10 completed sessions, sorted asc

Frontend dashboard page
  └── getSessionHistory() → SessionCard list
  └── getScoreTrends()    → TrendChart
  └── Empty state if sessions.length === 0
```

**Key constraints from CLAUDE.md:**
- Coach score is authoritative over AI score; both are stored and never deleted
- Route handlers are thin — zero business logic; all in service layer
- No ORM objects returned from routes — always Pydantic response schemas
- `get_current_user` on every protected route
- Tests written before implementation (TDD: red → green → refactor)

---

## Review

_To be filled in after implementation._
