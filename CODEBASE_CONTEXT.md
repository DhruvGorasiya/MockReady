# MockReady — Codebase Context

> **Purpose:** Drop this file into any new Claude session to immediately understand the full state of the codebase — architecture, what's built, what's tested, and how every piece connects.

---

## What MockReady Is

AI-powered technical interview prep platform. Candidates practice with an AI interviewer that:
1. Generates role-specific questions (behavioral / technical / system_design)
2. Scores answers across 5 dimensions (clarity, depth, structure, relevance, communication_quality) — each 1–10
3. Synthesizes behavioral, actionable feedback per dimension

Coaches can audit and override AI scores. Both AI and coach scores are stored permanently (immutable history). Coach score is authoritative when present.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 App Router, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI (Python 3.11+) |
| Database | Supabase (PostgreSQL) via SQLAlchemy async ORM |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) |
| Auth | Custom JWT (HS256, 24h expiry) — NOT Supabase Auth |
| Testing (BE) | pytest + pytest-asyncio |
| Testing (FE) | Jest + React Testing Library |
| Package mgmt | uv (Python), npm (Node) |

---

## Repository Layout

```
/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, router mounting
│   │   ├── core/
│   │   │   ├── config.py            # Settings from env vars
│   │   │   ├── db.py                # AsyncSession factory
│   │   │   └── security.py         # get_current_user dependency (JWT + dev bypass)
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── user.py              # User, UserRole (candidate/coach/admin)
│   │   │   ├── session.py           # Session, InterviewType, InterviewRole, SessionStatus
│   │   │   ├── question.py          # Question, SessionQuestion
│   │   │   ├── evaluation_score.py  # EvaluationScore, ScoredBy (ai/coach)
│   │   │   └── rubric.py            # RubricVersion (weights JSONB)
│   │   ├── schemas/
│   │   │   ├── auth.py              # RegisterRequest, LoginRequest, TokenResponse, UserResponse
│   │   │   ├── session.py           # All session schemas (see below)
│   │   │   └── coach.py             # CoachScoreRequest
│   │   ├── services/
│   │   │   ├── auth_service.py      # register_user, login_user
│   │   │   ├── session_service.py   # Session + answer logic (see below)
│   │   │   └── coach_service.py     # submit_coach_score, list_sessions_for_review
│   │   ├── agents/
│   │   │   ├── logging_utils.py     # log_agent_invocation() — structured JSON logging
│   │   │   ├── question_generation.py
│   │   │   ├── answer_evaluation.py
│   │   │   └── feedback_synthesis.py
│   │   ├── api/v1/
│   │   │   ├── health.py            # GET /health
│   │   │   ├── auth.py              # POST /auth/register, POST /auth/login
│   │   │   ├── sessions.py          # Session CRUD + answer submission
│   │   │   └── coach.py             # Coach score submission + review queue
│   │   └── tests/
│   │       ├── test_auth_router.py
│   │       ├── test_sessions_router.py
│   │       ├── test_session_service.py
│   │       ├── test_agent_logging.py
│   │       ├── test_agent_retry.py
│   │       ├── test_rubric_weights.py
│   │       ├── test_coach_service.py
│   │       └── test_coach_router.py
│   ├── alembic/                     # DB migrations
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout — wraps with AuthProvider
│   │   ├── page.tsx                 # Root redirect (→ /dashboard or /login)
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── (candidate)/
│   │   │   ├── layout.tsx           # Auth guard + nav bar + logout
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── sessions/new/page.tsx
│   │   │   ├── sessions/[id]/page.tsx
│   │   │   └── sessions/[id]/interview/page.tsx
│   │   └── (coach)/
│   │       ├── layout.tsx           # Auth guard + coach nav bar
│   │       ├── review/page.tsx      # Review queue
│   │       └── review/[sessionId]/page.tsx
│   ├── components/
│   │   ├── session/
│   │   │   ├── DashboardClient.tsx
│   │   │   ├── SessionSetupClient.tsx
│   │   │   ├── InterviewSessionClient.tsx
│   │   │   ├── SessionDetailClient.tsx
│   │   │   ├── SessionCard.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── DimensionBreakdown.tsx
│   │   │   └── EmptySessionState.tsx
│   │   └── coach/
│   │       └── CoachScoreForm.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── config.ts            # API_BASE (NEXT_PUBLIC_API_URL)
│   │   │   ├── client.ts            # apiFetch<T> + ApiError
│   │   │   ├── auth.ts              # login(), register()
│   │   │   ├── sessions.ts          # All session API calls
│   │   │   └── coach.ts             # getSessionsForReview(), submitCoachScore()
│   │   ├── auth/
│   │   │   └── AuthContext.tsx      # AuthProvider, useAuth()
│   │   └── types/
│   │       └── session.ts           # TypeScript mirrors of all Pydantic schemas
│   └── __tests__/
│       ├── auth/AuthContext.test.tsx
│       ├── app/dashboard.test.tsx
│       ├── app/sessionDetail.test.tsx
│       ├── app/login.test.tsx
│       ├── app/register.test.tsx
│       └── components/
│           ├── SessionCard.test.tsx
│           ├── TrendChart.test.tsx
│           ├── DimensionBreakdown.test.tsx
│           ├── EmptySessionState.test.tsx
│           └── coach/CoachScoreForm.test.tsx
├── docs/
│   ├── PRD.md                       # Full product requirements
│   └── auth_PRD.md                  # Auth implementation spec
├── tasks/
│   ├── todo.md                      # Original session dashboard task (completed)
│   ├── todo-session-flow.md         # Session flow task
│   └── todo-gap-fixes.md            # All 5 gap fixes (all completed)
└── CLAUDE.md                        # Project rules and conventions
```

---

## API Routes

### Auth (`/api/v1/auth`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | None | Register new user. Returns `UserResponse`. |
| POST | `/auth/login` | None | Login. Returns `TokenResponse` with `access_token`. |

### Sessions (`/api/v1/sessions`) — all require Bearer token
| Method | Path | Description |
|--------|------|-------------|
| POST | `/sessions` | Create bare session (no AI). |
| POST | `/sessions` (via frontend) | `create_session_with_questions` — calls question generation AI. |
| POST | `/sessions/{id}/questions/{qid}/answer` | Submit answer → runs eval + feedback agents in parallel → returns `AnswerFeedbackResponse`. |
| GET | `/sessions/history` | Candidate's completed/reviewed sessions. |
| GET | `/sessions/trends` | Last 10 sessions, ascending, for trend chart. |
| GET | `/sessions/{id}` | Full session detail with per-question scores. |

### Coach (`/api/v1/coach`) — requires `coach` or `admin` role (→ 403 otherwise)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/coach/sessions` | Sessions in `completed` status needing review. |
| POST | `/coach/sessions/{id}/questions/{qid}/score` | Submit coach score override. Returns updated `QuestionResult`. 409 if already scored. |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | No auth. Returns `{"status": "ok"}`. |

---

## Key Data Models

### Session lifecycle
`created` → `in_progress` → `completed` → `reviewed`

### EvaluationScore
- Both `ai` and `coach` scores stored as separate rows — **never deleted or overwritten**
- `scored_by`: enum `ai` | `coach`
- Fields: `clarity`, `depth`, `structure`, `relevance`, `communication_quality` (int 1–10), `composite_score` (Decimal 4,1)
- `reasoning` (JSONB): per-dimension reasoning from AI
- `justification` (text): coach's written override rationale

### SessionQuestion
- Snapshots `question_text` at creation — never re-fetched
- `candidate_answer` set once at `submit_answer()`

### RubricVersion
- `weights` (JSONB): `{"clarity": 0.2, "depth": 0.2, ...}` summing to 1.0
- Linked to `Session.rubric_version_id` (nullable)

---

## Core Service Logic

### `session_service.py`

**`_compute_weighted_composite(dims, weights)`** — pure helper
- If `weights` is None → equal weights (0.2 each)
- Returns `round(sum(w_i * score_i), 1)`

**`_agent_call_with_retry(fn, *args, **kwargs)`**
- Calls `fn` once. On failure: logs WARNING, retries once.
- Second failure: logs ERROR, raises `HTTP 502`.

**`create_session_with_questions(db, candidate_id, request)`**
- Calls `question_generation` agent (with retry)
- Pre-assigns UUIDs to session, Question, SessionQuestion before commit
- Returns `SessionCreatedResponse` with question list

**`submit_answer(db, session_id, question_id, candidate_id, answer)`**
- Eager-loads session + questions + rubric_version in one query
- Runs `answer_evaluation` + `feedback_synthesis` in parallel via `asyncio.gather()` (each with retry)
- Computes weighted composite using `rubric_version.weights` if present
- Persists `EvaluationScore(scored_by=ai)`
- Auto-completes session when all questions answered
- Returns `AnswerFeedbackResponse`

**`_authoritative_score(scores)`** — coach score if exists, else AI score

**`_composite_for_session(session)`** — averages per-question `composite_score` (which already embeds rubric weights)

### `coach_service.py`

**`submit_coach_score(db, session_id, question_id, coach_id, scores, justification)`**
- Loads `SessionQuestion` with `evaluation_scores` + `session.rubric_version`
- Raises 404 if not found, 409 if coach score already exists
- Computes weighted composite using session's rubric
- Creates `EvaluationScore(scored_by=coach)`
- Sets `session.status = reviewed`
- Returns updated `QuestionResult`

**`list_sessions_for_review(db)`**
- All sessions with `status=completed`, newest first
- Returns `SessionHistoryResponse`

---

## Agent System

All three agents follow the same pattern:
1. Build a structured prompt
2. Call Claude API (async)
3. Strip markdown code fences from response
4. Parse JSON
5. Emit a structured log record via `log_agent_invocation()` (success or error)
6. On exception: log and re-raise (service layer handles retry)

### Structured log fields (JSON, one record per invocation)
```json
{
  "agent_id": "uuid",
  "agent_name": "answer_evaluation | feedback_synthesis | question_generation",
  "model": "claude-sonnet-4-6",
  "timestamp": "ISO datetime",
  "latency_ms": 234.5,
  "status": "success | error",
  "input_payload": { "interview_type": "...", "role": "...", ... },
  "output_payload": { ... },   // success only
  "error": "..."               // error only
}
```

### Agent outputs
- **question_generation**: `[{"text": "..."}]`
- **answer_evaluation**: `{clarity, depth, structure, relevance, communication_quality (1–10), reasoning: {dim: "sentence..."}}`
- **feedback_synthesis**: `{feedback_summary, dimension_feedback: {dim: "..."}, improvement_suggestion}`

---

## Frontend Auth Flow

**Storage:** `localStorage` key `mockready_access_token`

**`AuthContext`** (wraps entire app via `app/layout.tsx`):
- `useAuth()` → `{ token, isAuthenticated, isLoading, login, register, logout }`
- `login(email, password)` → calls `/auth/login` → stores token
- `register(email, password)` → calls `/auth/register` → auto-login
- `logout()` → clears localStorage + token state

**Route protection:**
- `(candidate)/layout.tsx` — redirects to `/login` if not authenticated
- `(coach)/layout.tsx` — same guard + coach badge in nav

**Token usage:** All 4 session components use `useAuth().token`. `NEXT_PUBLIC_API_TOKEN` env var is **deprecated** (legacy only).

---

## Test Coverage Summary

### Backend (76 passing, 7 pre-existing failures*)
| File | Tests | What's covered |
|------|-------|---------------|
| `test_auth_router.py` | ~8 | Register, login, 401 flows |
| `test_sessions_router.py` | ~10 | Session CRUD routes, auth guards |
| `test_session_service.py` | ~19 | list_sessions, get_session_detail, get_score_trends, create_session |
| `test_agent_logging.py` | 6 | Structured log on success + failure for all 3 agents |
| `test_agent_retry.py` | 6 | Retry-once success; double-failure → 502 for all 3 agent call sites |
| `test_rubric_weights.py` | 5 | `_compute_weighted_composite` unit tests + weighted/equal paths in `submit_answer` |
| `test_coach_service.py` | 6 | submit_coach_score (happy, 404, 409), list_sessions_for_review |
| `test_coach_router.py` | 5 | 200/403/401 for both coach routes |

*7 pre-existing failures: `test_create_session_*` tests call `create_session()` without the required `role` argument — pre-date the current signature, not introduced by recent work.

### Frontend (51 passing, 10 suites)
| File | Tests |
|------|-------|
| `AuthContext.test.tsx` | 5 |
| `login.test.tsx` | 5 |
| `register.test.tsx` | 6 |
| `dashboard.test.tsx` | 5 |
| `sessionDetail.test.tsx` | 6 |
| `SessionCard.test.tsx` | ~6 |
| `TrendChart.test.tsx` | ~3 |
| `DimensionBreakdown.test.tsx` | ~5 |
| `EmptySessionState.test.tsx` | ~3 |
| `CoachScoreForm.test.tsx` | 6 |

---

## Environment Variables

### Backend (`.env` in `backend/`)
```
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_JWT_SECRET=<secret>          # Used to sign/verify JWTs
ANTHROPIC_API_KEY=<key>
DEV_BYPASS_AUTH=true                  # Skips JWT validation in dev
DEV_BYPASS_USER_ID=<uuid>             # Fixed user ID when bypass active
CLAUDE_MODEL=claude-sonnet-4-6        # Configurable model
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`.env.local` in `frontend/`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_API_TOKEN is deprecated — no longer needed for normal use
```

---

## Dev Commands

```bash
# Backend
cd backend && uv sync
uvicorn app.main:app --reload --port 8000
pytest backend/app/tests/ -v --cov=app
ruff check backend/
alembic upgrade head

# Frontend
cd frontend && npm install
npm run dev        # :3000
npm test
npm run lint
npm run build
```

---

## Key Conventions

### Python
- `snake_case` everywhere
- No raw SQL — SQLAlchemy ORM only
- No ORM objects returned from routes — always Pydantic schemas
- All agent calls are async; all service functions are async
- `get_current_user` on every protected route
- `HTTPException` with specific status codes — never `200` with error payload

### TypeScript
- `camelCase` variables/functions, `PascalCase` components/types
- No `any`. Ever.
- All fetch logic in `lib/api/` — components never call `fetch` directly
- All auth token access via `useAuth()` — never `process.env.NEXT_PUBLIC_API_TOKEN`

### Architecture rules
- Route → Service → Agent → DB (agents never called directly from routes)
- Evaluation + Feedback agents run in `asyncio.gather()` (parallel, never sequential)
- Question text snapshotted at session creation — never re-fetched
- `EvaluationScore` rows are immutable — never delete, never overwrite
- Composite score uses `RubricVersion.weights` when set; falls back to equal weights (0.2)

---

## Known Issues / Pre-existing Tech Debt

1. **7 failing tests** in `test_session_service.py` — `test_create_session_*` tests call `create_session(db, user_id, interview_type)` but the function now requires a `role` argument. Tests need updating.
2. **Feedback agent receives empty scores/reasoning** — `submit_answer()` passes `scores={}` and `reasoning={}` to `synthesize_feedback`. The agent re-generates feedback from the raw answer text, so output is still meaningful, but it doesn't use the evaluated dimension scores.
3. **No session locking** — simultaneous answer submissions to the same question aren't prevented at the DB level.
4. **Auth token is localStorage (not httpOnly cookie)** — acceptable for MVP/demo; noted in `auth_PRD.md` as hardening opportunity.
5. **No `GET /api/v1/auth/me` endpoint** — frontend can't fetch the current user's profile; only the token is stored.
6. **Coach UI has no role-switching** — the app doesn't redirect coach users to `/review`; they must navigate manually. A role-aware root redirect is the fix.
