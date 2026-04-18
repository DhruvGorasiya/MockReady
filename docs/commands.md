# Development Commands

## Backend (from repo root)

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

## Frontend (from `frontend/`)

```bash
npm install
npm run dev        # dev server on :3000
npm test           # Jest + RTL
npm run lint       # ESLint + Prettier check
npm run build      # production build
```
