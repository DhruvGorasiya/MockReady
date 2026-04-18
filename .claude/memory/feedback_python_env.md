---
name: Feedback — Python Environment
description: Always use `uv run` to invoke Python commands so the correct venv is used
type: feedback
---

Use `uv run` to invoke uvicorn, pytest, and any other Python commands inside the backend.

**Why:** Running `uvicorn` directly uses the system Python (3.12), not the project venv (3.13 managed by uv). This caused bcrypt to load from the system site-packages instead of the venv, making the version pin in `pyproject.toml` ineffective.

**How to apply:**
```bash
# Correct
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd backend && uv run pytest app/tests/ -v

# Wrong — may use system Python
uvicorn app.main:app --reload --port 8000
pytest app/tests/ -v
```
