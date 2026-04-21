# MockReady

**AI-powered technical interview preparation platform.** Practice with an AI interviewer that generates role-specific questions, evaluates responses across five dimensions, and delivers actionable behavioral feedback. Coaches audit and override AI scores, building ground-truth data that powers a self-improving LLM-as-judge evaluation system.

> Course project — CS Graduate AI Engineering, Northeastern University
> Authors: Xuan Bai, Dhruv Gorasiya

---

## For Reviewers / TAs — Quick Demo Walkthrough

This project has **two user roles** (Candidate and Coach). You will need to create one of each to exercise the full flow. Everything below assumes the backend is on `http://localhost:8000` and the frontend on `http://localhost:3000`.

### 1. Create a Candidate account

1. Open **http://localhost:3000/register**
2. Enter any email + a password with at least 8 characters, one uppercase letter, and one digit (e.g. `Candidate1`)
3. Submit → you are auto-logged-in and land on **`/dashboard`** (the candidate dashboard)
4. Click **New Session**, pick an interview type (behavioral / technical / system design) and a role (SWE / PM / DS), and start
5. Answer each question → the session transitions to `completed` once all questions are answered

### 2. Create a Coach account (no SQL required)

> Coach registration is gated by a query parameter instead of a separate form — it keeps the UI simple while still letting reviewers create coach accounts without touching the database.

1. Open **http://localhost:3000/register?role=coach**
2. You should see a **purple "Registering as Coach" badge** next to the page heading — this confirms the role parameter was picked up
3. Fill in a different email and the same password rules as above
4. Submit → you are auto-logged-in and land on **`/review`** (the coach review queue — not the candidate dashboard)

If the purple badge is missing, the URL did not include `?role=coach` and the account will be created as a candidate. Double-check the URL before submitting.

Admin accounts are deliberately **not** creatable via the public register endpoint. `?role=admin` is silently treated as candidate.

### 3. Walk the coach flow

1. Log in as the coach you just created (or stay logged in)
2. Land on **`/review`** — the queue shows every candidate session whose status is `completed` (not yet `reviewed`)
3. Click into a session → you see the question, the candidate's answer, the AI scores across all five dimensions, and an override form pre-filled with the AI scores as a starting point
4. Adjust any dimension score, optionally add a **Justification** explaining the override, and click **Submit score**
5. Navigate between questions with **Previous / Next** — the form resets per question so nothing leaks between them
6. The first override flips the session's status from `completed` to `reviewed`, so it drops off the queue. The candidate can still view it from their dashboard — it just no longer needs review.

### 4. Things worth trying

- **Log out and back in** — coaches should always land on `/review`, candidates on `/dashboard`. The post-login redirect is driven by `GET /api/v1/auth/me`.
- **Stale token** — edit `mockready_access_token` in LocalStorage to a garbage value and refresh. The UI auto-logs-out instead of getting stuck (the `/auth/me` 401 clears the token).
- **Cross-role URL poking** — as a candidate, navigate to `/review`. The coach layout guard bounces you back to `/login` because the route is role-gated.

---

## What It Does

MockReady addresses a gap that existing tools like Leetcode, Pramp, and ChatGPT do not fill: **dimensional, behavioral feedback on explanation quality and communication**, not just correctness.

| Role | What They Do |
|---|---|
| **Candidate** | Selects a role and interview type, completes a timed session, receives per-dimension AI scores with behavioral feedback |
| **Coach** | Reviews AI-scored sessions, overrides scores with justification |
| **Admin** | (planned) Manages the question bank, configures scoring rubrics, monitors AI evaluation drift |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| Database | Supabase (PostgreSQL) via SQLAlchemy ORM |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) |
| Auth | JWT (HS256), verified against `SUPABASE_JWT_SECRET` |
| Testing | pytest + pytest-asyncio (backend), Jest + React Testing Library (frontend), Playwright (e2e) |
| Linting | Ruff (Python), ESLint + Prettier (TypeScript) |
| Package mgmt | uv (Python), npm (Node) |
| Deployment | Vercel (frontend) |

---

## Architecture Diagram

![Architecture](docs/architecture.png)

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [`uv`](https://github.com/astral-sh/uv) for Python package management
- A Supabase project (for the Postgres DB)
- An Anthropic API key

### Environment variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_JWT_SECRET=<jwt-secret-from-supabase-settings>
ANTHROPIC_API_KEY=<your-key>

# Optional: set to true to skip JWT validation in local dev.
# Keep false when testing the auth flow.
DEV_BYPASS_AUTH=false
```

The frontend defaults to `http://localhost:8000` for the backend. To point at a different host, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-host
```

### Backend

```bash
cd backend
uv sync --extra dev          # installs runtime + test deps
alembic upgrade head         # applies schema migrations
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev                  # dev server on :3000
```

Open `http://localhost:3000`.

---

## AI Agent Architecture

Three agents run during a session. Each agent invocation is logged (agent id, input, output, latency, model version, timestamp) for the LLM-as-judge pipeline.

### Question Generation Agent
- **Trigger:** Session start
- **Inputs:** interview type, role, difficulty, question count, previously seen question ids
- **Output:** Array of question objects with text, type, role, difficulty, and tags

### Answer Evaluation Agent
- **Trigger:** Candidate submits an answer
- **Inputs:** question text, candidate answer, interview type, role, active rubric
- **Output:** Integer scores (1–10) across 5 dimensions + one-sentence reasoning per dimension
- **Dimensions:** Clarity, Depth, Structure, Relevance, Communication Quality

### Feedback Synthesis Agent
- **Trigger:** Runs in parallel with the Evaluation Agent via `asyncio.gather()`
- **Inputs:** question, answer, evaluation scores, reasoning
- **Output:** 2–3 sentence summary, 1–3 sentence behavioral feedback per dimension, one concrete improvement suggestion

```
Route Handler → Service → asyncio.gather(
    answer_evaluation_agent(...),
    feedback_synthesis_agent(...),
)
```

---

## Scoring System

- **Dimension scores:** integers 1–10
- **Composite score:** weighted average using the active `RubricVersion` for the session's role; falls back to equal 0.2 weights when none is configured
- **Dual scores:** both `ai_score` and `coach_score` are stored. Coach score is authoritative when present. Neither is ever overwritten or deleted — overrides supersede, they do not replace.
- **Rubric weight changes** apply to new sessions only, never retroactively.

---

## API Overview

All endpoints are under `/api/v1`. Every route except `/health`, `/auth/register`, and `/auth/login` requires `Authorization: Bearer <token>`.

| Group | Route | Notes |
|---|---|---|
| Health | `GET /health` | Liveness probe |
| Auth | `POST /auth/register` | Accepts optional `role: "candidate" \| "coach"` (default candidate). `admin` is rejected with 422. |
| Auth | `POST /auth/login` | Returns a JWT |
| Auth | `GET /auth/me` | Returns the authenticated user's id, email, role, created_at |
| Sessions (candidate) | `POST /sessions` | Creates a session + generates questions |
| Sessions (candidate) | `GET /sessions/history` | Candidate's completed/reviewed sessions |
| Sessions (candidate) | `GET /sessions/trends` | Composite + per-dimension trend over the last 10 sessions |
| Sessions (candidate) | `GET /sessions/{id}` | Scoped to the authenticated candidate |
| Sessions (candidate) | `POST /sessions/{id}/questions/{qid}/answer` | Submit answer; runs eval + feedback agents in parallel |
| Coach | `GET /coach/sessions` | Queue of completed sessions awaiting review |
| Coach | `GET /coach/sessions/{id}` | Full session detail; not scoped by candidate_id |
| Coach | `POST /coach/sessions/{id}/questions/{qid}/score` | Submit override scores + justification; flips session to `reviewed` |

Coach routes return `403 Forbidden` for users whose role is not `coach` or `admin`.

---

## Session State Machine

```
CREATED → IN_PROGRESS → COMPLETED → REVIEWED
                                ↘ ABANDONED (auto, after 48h idle)
```

- `CREATED` — session record exists, no answers yet
- `IN_PROGRESS` — at least one answer submitted
- `COMPLETED` — all questions answered, appears on the coach queue
- `REVIEWED` — a coach has submitted at least one override; drops off the queue

---

## Testing

### Backend

```bash
cd backend

# Full suite with coverage
uv run pytest app/tests/ -v --cov=app

# Single file
uv run pytest app/tests/test_session_service.py -v

# Lint
uv run ruff check .
```

Coverage target: >80% on all `services/` and `agents/` modules.
Discipline: **Red → Green → Refactor** — failing tests are committed before the implementation that makes them pass. This is visible in the git history (`test:` commits precede their matching `feat:` commits).

### Frontend

```bash
cd frontend
npm test                     # Jest + React Testing Library
npm run lint                 # ESLint + Prettier
npx tsc --noEmit             # type check
npm run build                # production build
```

### End-to-end

```bash
cd frontend
npx playwright test          # requires the backend + frontend dev servers running
```

---

## Repository Structure

```
/
├── frontend/                  # Next.js app
│   ├── app/
│   │   ├── (candidate)/       # Candidate-facing routes (dashboard, new session, interview, detail)
│   │   ├── (coach)/           # Coach-facing routes (review queue, session review)
│   │   ├── login/
│   │   └── register/          # Accepts ?role=coach
│   ├── components/
│   │   ├── session/           # Candidate session UI (cards, charts, detail, setup, live interview)
│   │   └── coach/             # CoachScoreForm
│   ├── lib/
│   │   ├── api/               # Typed REST clients (auth, sessions, coach)
│   │   ├── auth/              # AuthContext — stores token + user, /auth/me hydration, auto-logout on 401
│   │   └── types/
│   └── __tests__/             # Jest + RTL
├── backend/
│   ├── app/
│   │   ├── api/v1/            # auth.py, sessions.py, coach.py, health.py
│   │   ├── agents/            # question_generation, answer_evaluation, feedback_synthesis, logging_utils
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic (session, coach, auth)
│   │   ├── core/              # config, db, security (JWT)
│   │   └── tests/             # pytest
│   ├── alembic/               # Database migrations
│   └── pyproject.toml
├── docs/                      # PRD, architecture, security, testing, commands, sprints
├── tasks/                     # todo.md, lessons.md
└── CLAUDE.md                  # Instructions for AI-assisted development
```

---

## Security

- All secrets are read from environment variables. No credentials in source.
- JWT validation on every protected route via the `get_current_user` FastAPI dependency.
- Role-based access: `/api/v1/coach/*` requires `role` ∈ {`coach`, `admin`}. Candidates receive `403`.
- Candidates can only read sessions they own — `get_session_detail` scopes by `candidate_id`.
- All database access goes through SQLAlchemy ORM. Raw SQL is never constructed from user input.
- User input is sanitized before being passed to any LLM prompt.
- CORS origins are explicitly allowlisted.
- CI gates: [Gitleaks](https://github.com/gitleaks/gitleaks) secrets scan, `npm audit --audit-level=critical`, and a dedicated security reviewer agent on new routes.
- Full OWASP Top 10 coverage documented in [`docs/security.md`](docs/security.md).

---

## Documentation

| File | Contents |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Full product requirements, user stories, acceptance criteria |
| [`docs/architecture.md`](docs/architecture.md) | Architecture decisions and patterns |
| [`docs/security.md`](docs/security.md) | OWASP coverage, CI security gates |
| [`docs/testing.md`](docs/testing.md) | Testing strategy and TDD conventions |
| [`docs/conventions.md`](docs/conventions.md) | Code style and naming conventions |
| [`docs/commands.md`](docs/commands.md) | All dev commands in one place |
| [`docs/demo_script.md`](docs/demo_script.md) | Walkthrough script for the demo video |
| [`CLAUDE.md`](CLAUDE.md) | Instructions for AI-assisted development |
| [`tasks/todo.md`](tasks/todo.md) | Current sprint task tracking |
