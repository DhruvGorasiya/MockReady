# Testing Strategy

## Philosophy: TDD for all core logic

Write failing tests first. Implement minimum code to pass. Refactor. This is not optional for services and agents — it is the required workflow.

## Backend (pytest)

- **Unit tests:** Every service function has a unit test. Mock all external dependencies (DB, Anthropic API, Supabase).
- **Integration tests:** Test the full route → service → DB path using a test database. Use Supabase local or a dedicated test schema.
- **Agent tests:** Mock the Anthropic API response. Test that the agent correctly parses structured outputs and handles malformed responses.
- **Coverage target:** >80% on all `services/` and `agents/` modules.
- **Run:** `pytest backend/app/tests/ -v --cov=app`

## Frontend (Jest + RTL)

- **Unit tests:** All utility functions in `lib/`.
- **Component tests:** All components that contain logic (forms, dashboards, session screen). Use RTL — test behavior, not implementation.
- **API mocks:** Use `jest.mock` for all `lib/api/` calls in component tests.
- **Run:** `npm test` from `frontend/`

## Commit pattern for TDD

```
test: add failing tests for session creation service    ← RED
feat: implement session creation to pass tests          ← GREEN
refactor: extract session state validation to helper    ← REFACTOR
```
