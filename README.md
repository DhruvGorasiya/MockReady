# MockReady

**AI-powered technical interview preparation platform.** Practice with an AI interviewer that generates role-specific questions, evaluates responses across five dimensions, and delivers actionable behavioral feedback. Coaches audit and override AI scores, building ground-truth data that powers a self-improving LLM-as-judge evaluation system.

> Course project — CS Graduate AI Engineering, Northeastern University  
> Authors: Xuan Bai, Dhruv Gorasiya

---

## What It Does

MockReady addresses a gap that existing tools like Leetcode, Pramp, and ChatGPT do not fill: **dimensional, behavioral feedback on explanation quality and communication**, not just correctness.

| Role | What They Do |
|---|---|
| **Candidate** | Selects a role and interview type, completes a timed session, receives per-dimension AI scores with behavioral feedback |
| **Coach** | Reviews AI-scored sessions, overrides scores with justification, adds written commentary |
| **Admin** | Manages the question bank, configures scoring rubrics, monitors AI evaluation accuracy |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| Database | Supabase (PostgreSQL) via SQLAlchemy ORM |
| AI | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| Auth | Supabase Auth (JWT) |
| Testing (BE) | pytest + pytest-asyncio |
| Testing (FE) | Jest + React Testing Library |
| Linting | Ruff (Python), ESLint + Prettier (TypeScript) |
| Package mgmt | uv (Python), npm (Node) |
| Deployment | Vercel (frontend) |

---

## Repository Structure

```
/
├── frontend/                  # Next.js app
│   ├── app/                   # App Router pages and layouts
│   │   ├── (candidate)/       # Candidate-facing routes
│   │   ├── (coach)/           # Coach-facing routes
│   │   ├── login/
│   │   └── register/
│   ├── components/            # Reusable UI components
│   ├── lib/                   # API client, utilities, types
│   └── __tests__/             # Jest tests
├── backend/
│   ├── app/
│   │   ├── api/v1/            # Route handlers (auth, sessions, coach, health)
│   │   ├── agents/            # AI agent modules
│   │   │   ├── question_generation.py
│   │   │   ├── answer_evaluation.py
│   │   │   ├── feedback_synthesis.py
│   │   │   └── logging_utils.py
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic (session, coach, auth)
│   │   ├── core/              # Config, DB session, security
│   │   └── tests/             # pytest tests
│   ├── alembic/               # Database migrations
│   └── pyproject.toml
├── docs/                      # Architecture, PRD, sprint notes, security
├── tasks/                     # todo.md, lessons.md
├── vercel.json
└── CLAUDE.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [`uv`](https://github.com/astral-sh/uv) for Python package management
- A Supabase project (for DB and auth)
- An Anthropic API key

### Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<db>
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
JWT_SECRET=<your-secret>
ANTHROPIC_API_KEY=<your-key>
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend

```bash
cd backend
uv sync
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # dev server on :3000
```

---

## AI Agent Architecture

Three agents run during a session. Each agent invocation is fully logged (agentId, input, output, latency, model version, timestamp) for the LLM-as-judge pipeline.

### Question Generation Agent
- **Trigger:** Session start
- **Inputs:** interview type, role, difficulty, question count, previously seen question IDs
- **Output:** Array of question objects with text, type, role, difficulty, and tags
- **Behavior:** Generates role-specific questions via Claude. Does not repeat questions seen in the last 5 sessions.

### Answer Evaluation Agent
- **Trigger:** Candidate submits an answer
- **Inputs:** question text, candidate answer, interview type, role, active rubric
- **Output:** Integer scores (1–10) across 5 dimensions + one-sentence reasoning per dimension
- **Dimensions:** Clarity, Depth, Structure, Relevance, Communication Quality

### Feedback Synthesis Agent
- **Trigger:** Runs in parallel with the Evaluation Agent via `asyncio.gather()`
- **Inputs:** question, answer, evaluation scores, reasoning
- **Output:** 2-3 sentence summary, 1-3 sentence behavioral feedback per dimension, one concrete improvement suggestion

```
Route Handler → Service → asyncio.gather(
    answer_evaluation_agent(...),
    feedback_synthesis_agent(...),
)
```

---

## Scoring System

- **Dimension scores:** integers 1–10
- **Composite score:** weighted average using the active `RubricVersion` for the session's role
- **Dual scores:** both `ai_score` and `coach_score` are stored. Coach score is authoritative when present. Neither is ever overwritten or deleted.
- **Rubric changes** apply to new sessions only — never retroactively.

---

## Coach Override & LLM-as-Judge

When a Coach overrides AI scores, the override (with justification) becomes a labeled ground-truth record. After review completion, an async LLM-as-judge job runs:

1. Inputs original question, candidate answer, AI scores + reasoning, Coach scores + justification to Claude
2. Claude outputs: `agreement` (bool per dimension), `confidence` (0.0–1.0), `reasoning` (string)
3. Results feed the Admin Evaluation Dashboard (agreement rate, score drift, override rate)

---

## API Overview

All endpoints are prefixed `/api/v1` and require `Authorization: Bearer <token>` except `/health` and `/auth/*`.

| Group | Routes |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Sessions | `POST /sessions`, `GET /sessions/:id`, `POST /sessions/:id/questions/:qid/answer`, `GET /sessions/:id/feedback`, `GET /sessions/history` |
| Coach | `GET /coach/queue`, `POST /coach/sessions/:id/overrides`, `POST /coach/sessions/:id/comment`, `PATCH /coach/sessions/:id/complete` |
| Admin | `GET/POST /admin/questions`, `GET/POST /admin/rubrics`, `GET /admin/evals/dashboard` |
| Health | `GET /health` |

---

## Testing

### Backend

```bash
# All tests with coverage
pytest backend/app/tests/ -v --cov=app

# Single file
pytest backend/app/tests/test_session_service.py -v

# Lint
ruff check backend/
```

Coverage target: >80% on all `services/` and `agents/` modules.  
Pattern: **Red → Green → Refactor** — tests are written before implementation.

### Frontend

```bash
cd frontend
npm test          # Jest + RTL
npm run lint      # ESLint + Prettier check
npm run build     # production build check
```

---

## Security

- All secrets via environment variables. No credentials in the codebase.
- JWT validation on every protected endpoint via `get_current_user` dependency.
- Role-based access: Candidates, Coaches, and Admins see only their authorized views.
- All DB access through SQLAlchemy ORM — no raw SQL strings.
- User input is sanitized before passing to any LLM prompt.
- CORS origins are explicitly allowlisted.
- CI gates: [Gitleaks](https://github.com/gitleaks/gitleaks) secrets scan, `npm audit --audit-level=critical`, and a security reviewer agent on new routes.
- Security policy addresses OWASP Top 10 — see [`docs/security.md`](docs/security.md).

---

## Session State Machine

```
CREATED → IN_PROGRESS → COMPLETED → REVIEWED
                                ↘ ABANDONED (auto, after 48h idle)
```

---

## Documentation

| File | Contents |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Full product requirements, user stories, acceptance criteria |
| [`docs/architecture.md`](docs/architecture.md) | Architecture decisions and patterns |
| [`docs/security.md`](docs/security.md) | OWASP coverage, CI security gates |
| [`docs/testing.md`](docs/testing.md) | Testing strategy and patterns |
| [`CLAUDE.md`](CLAUDE.md) | AI agent development instructions |
| [`tasks/todo.md`](tasks/todo.md) | Current sprint task tracking |
