# MockReady — Memory Index

> This file is the index for Claude's persistent memory across sessions.
> Each entry points to a memory file in `.claude/memory/`. Read relevant files before starting work.

## User
- [user_profile.md](memory/user_profile.md) — Who Dhruv is, skill level, working style

## Project
- [project_overview.md](memory/project_overview.md) — What MockReady is, tech stack, current state
- [db_connection.md](memory/db_connection.md) — Supabase connection setup (Session Pooler, not direct)
- [auth_setup.md](memory/auth_setup.md) — Custom JWT auth, bcrypt without passlib
- [known_bugs.md](memory/known_bugs.md) — Pre-existing failures and known tech debt
- [p3_requirements.md](memory/p3_requirements.md) — Project 3 rubric gaps and what still needs to be built

## Feedback
- [feedback_errors.md](memory/feedback_errors.md) — How to handle errors (log before swallowing, never silent 503s)
- [feedback_python_env.md](memory/feedback_python_env.md) — Always use `uv run` to invoke commands inside the venv
