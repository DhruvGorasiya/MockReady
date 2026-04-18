# Coding Conventions

## Python (Backend)

- **Naming:** `snake_case` for everything. Files, functions, variables, DB columns.
- **Schemas:** Every API endpoint has a dedicated Pydantic request schema and response schema in `schemas/`. Never return ORM objects directly from routes.
- **Services:** One file per domain (`session_service.py`, `scoring_service.py`). Functions are async by default.
- **Agents:** Each agent is a single async function with typed inputs and typed outputs. No side effects inside agent functions — the calling service handles DB writes.
- **Error handling:** Use FastAPI `HTTPException` with specific status codes. Never return 200 with an error payload.
- **Environment:** All secrets via environment variables. Never hardcode API keys, DB URLs, or credentials anywhere.
- **Imports:** Absolute imports only. No relative imports outside of `__init__.py`.

## TypeScript (Frontend)

- **Naming:** `camelCase` for variables/functions, `PascalCase` for components and types.
- **Components:** One component per file. Filename matches component name.
- **API calls:** All fetch logic lives in `lib/api/`. Components never call `fetch` directly.
- **Types:** Define types in `lib/types/`. No `any`. No implicit `any`.
- **State:** Prefer React state and context. No global state library unless justified.

## Git

- Branch naming: `feature/`, `fix/`, `chore/` prefixes.
- Commit messages: imperative mood, specific. "Add session state machine" not "stuff".
- Every feature branch merges via PR, not direct push to main.
