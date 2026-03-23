# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Product requirements: `MockReady_PRD.md` (root). Task tracking: `tasks/todo.md`. Lessons: `tasks/lessons.md`.

---

## Development Commands

### Backend (from repo root)

```bash
# Install deps
cd backend && uv sync

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run all tests
pytest backend/app/tests/ -v --cov=app

# Run a single test file
pytest backend/app/tests/test_session_service.py -v

# Lint
ruff check backend/

# Apply DB migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "describe change"
```

### Frontend (from `frontend/`)

```bash
npm install
npm run dev        # dev server on :3000
npm test           # Jest + RTL
npm run lint       # ESLint + Prettier check
npm run build      # production build
```

---

## Project Overview

MockReady is a production-grade AI-powered technical interview preparation platform. Candidates practice with an AI interviewer that generates role-specific questions, evaluates responses across multiple dimensions, and delivers actionable feedback. Coaches audit and override AI scores, building ground-truth data that powers an LLM-as-judge evaluation system.

**Three parallel AI agents:**

1. Question Generation Agent — produces role/type-specific questions at session start
2. Answer Evaluation Agent — scores responses across 5 dimensions (1-10 each)
3. Feedback Synthesis Agent — generates behavioral, actionable feedback per dimension

---

## Tech Stack

| Layer        | Technology                                        |
| ------------ | ------------------------------------------------- |
| Frontend     | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend      | FastAPI (Python 3.11+)                            |
| Database     | Supabase (PostgreSQL) via SQLAlchemy ORM          |
| AI           | Anthropic Claude API (claude-sonnet-4-20250514)   |
| Auth         | Supabase Auth (JWT)                               |
| Testing (BE) | pytest + pytest-asyncio                           |
| Testing (FE) | Jest + React Testing Library                      |
| Linting      | Ruff (Python), ESLint + Prettier (TypeScript)     |
| Package mgmt | uv (Python), npm (Node)                           |

---

## Repository Structure

```
/                              # repo root
├── frontend/                  # Next.js app
│   ├── app/                   # App Router pages and layouts
│   ├── components/            # Reusable UI components
│   ├── lib/                   # API client, utilities, types
│   └── __tests__/             # Jest tests (mirror src structure)
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI route handlers (v1/)
│   │   ├── agents/            # AI agent modules
│   │   │   ├── question_generation.py
│   │   │   ├── answer_evaluation.py
│   │   │   └── feedback_synthesis.py
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer
│   │   ├── core/              # Config, db session, security
│   │   └── tests/             # pytest tests (mirror app structure)
│   ├── alembic/               # Database migrations
│   └── pyproject.toml
├── docs/                      # Additional docs
├── tasks/                     # todo.md, lessons.md
├── MockReady_PRD.md           # Source of truth for all feature requirements
└── CLAUDE.md
```

---

## Architecture Decisions

### Frontend/Backend Separation

Fully separated. Frontend communicates with backend exclusively via REST API. No server actions that bypass the API layer. This keeps the backend independently testable and deployable.

### Backend Structure: Services Pattern

Route handlers are thin. All business logic lives in `services/`. Agents are a separate layer called by services, never directly by route handlers.

```
Route Handler → Service → Agent (if AI needed) → DB
```

### Agent Parallelism

Answer Evaluation and Feedback Synthesis agents run concurrently using `asyncio.gather()` after answer submission. Question Generation runs once at session start, independently.

### Database: SQLAlchemy over raw Supabase client

Use SQLAlchemy ORM for all database operations in the backend. Never write raw SQL strings in application code. Supabase is the hosting layer; SQLAlchemy is the interface. Migrations via Alembic.

### Authentication

Supabase Auth issues JWTs. FastAPI validates JWTs on every protected endpoint using a dependency injector (`get_current_user`). Never roll custom auth logic.

### Scoring Schema

- Dimension scores: integers 1-10
- Composite: weighted average per active RubricVersion for the session's role
- Both `ai_score` and `coach_score` are stored. Coach score is authoritative when present. Neither is deleted or overwritten — both persist.

---

## Coding Conventions

### Python (Backend)

- **Naming:** `snake_case` for everything. Files, functions, variables, DB columns.
- **Schemas:** Every API endpoint has a dedicated Pydantic request schema and response schema in `schemas/`. Never return ORM objects directly from routes.
- **Services:** One file per domain (`session_service.py`, `scoring_service.py`). Functions are async by default.
- **Agents:** Each agent is a single async function with typed inputs and typed outputs. No side effects inside agent functions — the calling service handles DB writes.
- **Error handling:** Use FastAPI `HTTPException` with specific status codes. Never return 200 with an error payload.
- **Environment:** All secrets via environment variables. Never hardcode API keys, DB URLs, or credentials anywhere.
- **Imports:** Absolute imports only. No relative imports outside of `__init__.py`.

### TypeScript (Frontend)

- **Naming:** `camelCase` for variables/functions, `PascalCase` for components and types.
- **Components:** One component per file. Filename matches component name.
- **API calls:** All fetch logic lives in `lib/api/`. Components never call `fetch` directly.
- **Types:** Define types in `lib/types/`. No `any`. No implicit `any`.
- **State:** Prefer React state and context. No global state library unless justified.

### Git

- Branch naming: `feature/`, `fix/`, `chore/` prefixes.
- Commit messages: imperative mood, specific. "Add session state machine" not "stuff".
- Every feature branch merges via PR, not direct push to main.

---

## Testing Strategy

### Philosophy: TDD for all core logic

Write failing tests first. Implement minimum code to pass. Refactor. This is not optional for services and agents — it is the required workflow.

### Backend (pytest)

- **Unit tests:** Every service function has a unit test. Mock all external dependencies (DB, Anthropic API, Supabase).
- **Integration tests:** Test the full route → service → DB path using a test database. Use Supabase local or a dedicated test schema.
- **Agent tests:** Mock the Anthropic API response. Test that the agent correctly parses structured outputs and handles malformed responses.
- **Coverage target:** >80% on all `services/` and `agents/` modules.
- **Run:** `pytest backend/app/tests/ -v --cov=app`

### Frontend (Jest + RTL)

- **Unit tests:** All utility functions in `lib/`.
- **Component tests:** All components that contain logic (forms, dashboards, session screen). Use RTL — test behavior, not implementation.
- **API mocks:** Use `jest.mock` for all `lib/api/` calls in component tests.
- **Run:** `npm test` from `frontend/`

### Commit pattern for TDD

```
test: add failing tests for session creation service    ← RED
feat: implement session creation to pass tests          ← GREEN
refactor: extract session state validation to helper    ← REFACTOR
```

---

## Workflow Orchestration

### 1. Plan Node Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — do not keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy

- Use subagents liberally to keep the main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop

- After ANY correction, update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for any relevant project

### 4. Verification Before Done

- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — do not over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Do not ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

---

## Task Management

1. **Plan First:** Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan:** Check in before starting implementation
3. **Track Progress:** Mark items complete as you go
4. **Explain Changes:** High-level summary at each step
5. **Document Results:** Add review section to `tasks/todo.md`
6. **Capture Lessons:** Update `tasks/lessons.md` after corrections

---

## Do's and Don'ts

### Do

- **Do** log every agent invocation: agentId, input payload, output payload, latency (ms), model version, timestamp. This is non-negotiable for the LLM-as-judge pipeline.
- **Do** store both `ai_score` and `coach_score` in `EvaluationScore`. Never overwrite either.
- **Do** run Evaluation and Feedback agents with `asyncio.gather()` — never sequentially.
- **Do** snapshot `questionText` into `SessionQuestion` at session creation. Never re-fetch the question text after the session starts.
- **Do** validate all rubric weight configs sum to 100% before persisting.
- **Do** use `get_current_user` dependency on every protected route.
- **Do** handle agent failures gracefully: retry once, then surface a user-facing error and log the failure event.
- **Do** use Alembic for every schema change. Never mutate tables manually in Supabase.
- **Do** write Pydantic schemas for every request and response. No ORM objects leave the service layer.
- **Do** write tests before implementation for all service and agent code.

### Don't

- **Don't** pass raw user input directly to LLM prompts. Always sanitize and structure input before passing to any agent.
- **Don't** write raw SQL strings. Use SQLAlchemy ORM exclusively.
- **Don't** hardcode API keys, secrets, or database URLs anywhere in the codebase.
- **Don't** call agents directly from route handlers. Route → Service → Agent is the only valid path.
- **Don't** delete score records. Scores are immutable history. Supersede, never delete.
- **Don't** return ORM model objects from API routes. Always serialize to Pydantic response schemas first.
- **Don't** make agent calls synchronous. All agent calls are async.
- **Don't** add features outside the PRD scope without flagging it. Scope creep will break the timeline.
- **Don't** use `any` in TypeScript. Ever.
- **Don't** write a test after the implementation. Red-green-refactor is the order.
- **Don't** use generic feedback strings in agent prompts (e.g., "good job", "needs improvement"). All feedback must reference the candidate's actual answer.
- **Don't** apply rubric weight changes retroactively. New weights apply to new sessions only.

---

## Core Principles

- **Simplicity First:** Make every change as simple as possible. Minimal impact on surrounding code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact:** Changes should only touch what is necessary. Avoid introducing bugs in unrelated areas.

---

## Permissions Configuration

### Allowed Tools

- Bash (scoped to project directory)
- Read/write files within `mockready/`
- Run `pytest` and `npm test`
- Run `alembic upgrade head`
- Run `uvicorn` and `npm run dev` for local servers

### Denied

- No direct Supabase dashboard mutations during development
- No pushing to `main` directly
- No installing packages without updating `pyproject.toml` or `package.json`

---

## Context Management Strategy

- Run `/compact` after completing each discrete feature to keep context focused
- Run `/clear` when switching between frontend and backend work to avoid cross-context bleed
- Use `--continue` to resume interrupted sessions without losing progress
- Keep `tasks/todo.md` updated so session state can be reconstructed after a `/clear`

---

## Open Questions (from PRD)

See PRD Section 15. Key unresolved items affecting implementation:

- Monolith vs. microservices decision (lean toward monolith for v1)
- Coach assignment mechanism (self-select for v1 as placeholder)
- Follow-up question generation: dynamic vs. templated
- Caching layer: Redis vs. in-memory

_Resolve these in sprint planning before building the affected modules._
