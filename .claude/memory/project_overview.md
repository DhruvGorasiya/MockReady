---
name: Project Overview — MockReady
description: What MockReady is, the tech stack, and current implementation state
type: project
---

MockReady is an AI-powered technical interview prep platform built as a Northeastern University course project.

**Two user roles:** Candidate (practices interviews) and Coach (audits/overrides AI scores).

**Tech stack:**
- Frontend: Next.js 14 App Router, TypeScript, Tailwind CSS
- Backend: FastAPI (Python 3.11+), SQLAlchemy async ORM
- Database: Supabase (PostgreSQL) — uses Session Pooler URL (not direct connection)
- AI: Anthropic Claude API (`claude-sonnet-4-6`) via 3 agents
- Auth: Custom JWT (HS256, 24h) using `bcrypt` directly — passlib removed due to version incompatibility
- Testing: pytest + pytest-asyncio (backend), Jest + RTL (frontend)
- Package management: `uv` (Python), `npm` (Node)

**Current state (as of 2026-04-17):**
- Core features fully implemented: session creation with AI questions, answer evaluation, feedback synthesis, coach score override
- 76 backend tests passing, 51 frontend tests passing
- 7 pre-existing failing tests in `test_session_service.py` (stale `create_session` call signature — known, not regressions)
- App is running locally but NOT deployed yet

**Why:** Built for a course project grade. Also serves as a portfolio piece.
**How to apply:** Understand this is a solo/pair student project, not a startup. Scope suggestions to what's feasible before a deadline.
