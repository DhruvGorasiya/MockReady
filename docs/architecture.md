# Architecture

## Project Overview

MockReady is a production-grade AI-powered technical interview preparation platform. Candidates practice with an AI interviewer that generates role-specific questions, evaluates responses across multiple dimensions, and delivers actionable feedback. Coaches audit and override AI scores, building ground-truth data that powers an LLM-as-judge evaluation system.

**Three parallel AI agents:**

1. Question Generation Agent — produces role/type-specific questions at session start
2. Answer Evaluation Agent — scores responses across 5 dimensions (1-10 each)
3. Feedback Synthesis Agent — generates behavioral, actionable feedback per dimension

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

## Open Questions (from PRD)

See PRD Section 15. Key unresolved items affecting implementation:

- Monolith vs. microservices decision (lean toward monolith for v1)
- Coach assignment mechanism (self-select for v1 as placeholder)
- Follow-up question generation: dynamic vs. templated
- Caching layer: Redis vs. in-memory

_Resolve these in sprint planning before building the affected modules._
