# Security

## OWASP Top 10 Awareness

The following OWASP Top 10 risks are relevant to MockReady and must be actively mitigated.

### A01 — Broken Access Control

- Every protected route uses the `get_current_user` FastAPI dependency. No exceptions.
- Coach-only routes must additionally verify `user.role == "coach"` before proceeding.
- Candidates must never access another user's session data — all DB queries are scoped to `current_user.id`.

### A02 — Cryptographic Failures

- JWTs are signed with HS256 using a secret stored in environment variables. Never commit the secret.
- Passwords are hashed with `bcrypt` before storage. Plain-text passwords are never logged or stored.
- Auth tokens are stored in `localStorage` (known MVP tradeoff — httpOnly cookies would be more secure for production hardening).

### A03 — Injection

- Never pass raw user input directly to LLM prompts. Always sanitize and structure input before passing to any agent.
- All database operations use SQLAlchemy ORM. Raw SQL strings are never written in application code.
- No shell commands are constructed from user input.

### A04 — Insecure Design

- The Route → Service → Agent pattern ensures no business logic lives in route handlers where it could be bypassed.
- Rubric weight changes are validated to sum to 100% before persistence.
- Score records are immutable — supersede, never delete.

### A05 — Security Misconfiguration

- All secrets (API keys, DB URLs, JWT secret) are loaded from environment variables via `core/config.py`.
- Debug mode is never enabled in production.
- CORS origins are explicitly allowlisted — never use wildcard `*` in production.

### A06 — Vulnerable and Outdated Components

- `npm audit --audit-level=critical` runs in CI on every PR. Critical vulnerabilities block merge.
- Python dependencies are managed via `uv` with pinned versions in `pyproject.toml`.
- Dependency updates are reviewed before merging.

### A07 — Identification and Authentication Failures

- JWT expiry is set to 24 hours. Tokens are validated on every protected request.
- No session fixation risk — tokens are stateless JWTs, not server-side sessions.
- Failed login attempts return generic error messages (never reveal whether email or password was wrong).

### A08 — Software and Data Integrity Failures

- CI pipeline uses Gitleaks to scan for secrets before merge.
- All DB schema changes go through Alembic migrations — no manual table mutations.
- Agent outputs are parsed and validated via Pydantic schemas before any DB write.

### A09 — Security Logging and Monitoring Failures

- Every agent invocation is logged: agentId, input payload, output payload, latency (ms), model version, timestamp.
- Authentication failures are logged with timestamp and anonymized identifier.
- Never log raw passwords, tokens, or full PII fields.

### A10 — Server-Side Request Forgery (SSRF)

- The backend does not make user-directed HTTP requests to arbitrary URLs.
- All external calls go to known, hardcoded endpoints (Anthropic API, Supabase).

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

## CI Security Gates

The following security gates run in CI on every PR:

1. **Gitleaks** — secrets detection on all committed files
2. **`npm audit --audit-level=critical`** — blocks on critical dependency vulnerabilities
3. **`security-reviewer` agent** — OWASP Top 10 audit on new routes and services (`.claude/agents/security-reviewer.md`)
