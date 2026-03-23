# MockReady — project context for Claude

## What this is

**MockReady** is an AI-assisted mock technical interview product. It targets candidates who need structured feedback on **explanation quality**, **reasoning**, and **communication under pressure**—not just binary correctness.

## Source of truth

- **`MockReady_PRD.md`** — requirements, user stories, API sketch, data models, UI/UX, and out-of-scope items. Prefer the PRD over assumptions when implementing or changing behavior.

## Repo layout

- **`frontend/`** — web client
- **`backend/`** — API and services (agents, evaluation, persistence as specified in the PRD)

## Working agreements

- Keep changes aligned with the PRD and call out conflicts or gaps instead of silently diverging.
- Prefer small, reviewable changes; match existing patterns in each package once code exists.
