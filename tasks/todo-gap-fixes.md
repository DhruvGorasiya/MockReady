# Gap Fixes — MockReady

**Status:** Planning
**Created:** 2026-04-17

---

## Gaps to fix (priority order)

### Gap 1 — Agent invocation logging (Backend)
**Priority:** Highest — called "non-negotiable" in CLAUDE.md
**Scope:** Backend only
**Complexity:** Low

- [x] **1.1** Add structured logging to `answer_evaluation.py`: log agent_id (uuid), input payload, output payload, latency_ms, model version, timestamp — before and after Claude API call
- [x] **1.2** Add structured logging to `feedback_synthesis.py`: same fields
- [x] **1.3** Add structured logging to `question_generation.py`: same fields
- [x] **1.4** Add tests verifying log output is emitted on successful + failed agent calls

---

### Gap 2 — Agent retry logic (Backend)
**Priority:** High — CLAUDE.md says "retry once, then surface a user-facing error and log the failure event"
**Scope:** Backend only
**Complexity:** Low

- [x] **2.1** Implement `_agent_call_with_retry()` helper in session_service: attempts once, warns on failure, retries, raises HTTPException 502 on second failure
- [x] **2.2** Apply to `evaluate_answer()` call in `session_service.submit_answer()`
- [x] **2.3** Apply to `synthesize_feedback()` call in `session_service.submit_answer()`
- [x] **2.4** Apply to `generate_questions()` call in `session_service.create_session_with_questions()`
- [x] **2.5** Add tests for retry behavior (mock agent to fail once, then succeed; fail twice → 502)

---

### Gap 3 — Auth UI (Frontend)
**Priority:** High — app is unusable without real auth
**Scope:** Frontend only
**Complexity:** Medium
**Reference:** `docs/auth_PRD.md`

#### Phase A — API client
- [x] **3.1** Create `frontend/lib/api/config.ts` — export `API_BASE` from `NEXT_PUBLIC_API_URL`
- [x] **3.2** Refactor `frontend/lib/api/client.ts` to import `API_BASE` from config
- [x] **3.3** Create `frontend/lib/api/auth.ts` — `login(body)` and `register(body)` typed to `TokenResponse` / `UserResponse`

#### Phase B — Auth context
- [x] **3.4** Create `frontend/lib/auth/AuthContext.tsx` — `AuthProvider` with `localStorage`, `login`, `register`, `logout`, hydration `useEffect`
- [x] **3.5** Wrap `app/layout.tsx` with `AuthProvider`

#### Phase C — Pages
- [x] **3.6** Create `app/login/page.tsx` — email + password form, error display, link to register
- [x] **3.7** Create `app/register/page.tsx` — email + password + confirm fields, client validation, auto-login on success
- [x] **3.8** Create `app/page.tsx` — redirect to `/dashboard` if authenticated, else `/login`

#### Phase D — Replace env token
- [x] **3.9** Update `DashboardClient.tsx` to use `useAuth().token`
- [x] **3.10** Update `SessionSetupClient.tsx` to use `useAuth().token`
- [x] **3.11** Update `SessionDetailClient.tsx` to use `useAuth().token`
- [x] **3.12** Update `InterviewSessionClient.tsx` to use `useAuth().token`

#### Phase E — Route protection
- [x] **3.13** Add `ProtectedLayout` guard under `app/(candidate)/layout.tsx` — redirect to `/login` if no token (after hydration); show loading skeleton while hydrating
- [x] **3.14** Add nav bar to `(candidate)/layout.tsx` — app title + logout button

#### Phase F — Tests
- [x] **3.15** Add tests for `AuthContext` (login stores token, logout clears token, hydrates from localStorage)
- [x] **3.16** Update existing component tests to mock `AuthContext` instead of env token
- [x] **3.17** Add tests for login page (form submission, error state) and register page

---

### Gap 4 — Composite score respects RubricVersion weights (Backend)
**Priority:** Medium
**Scope:** Backend only
**Complexity:** Medium

- [x] **4.1** Write failing tests: 3 pure unit tests + 2 integration tests
- [x] **4.2** Add `_compute_weighted_composite(dims, weights)` helper with equal-weight fallback
- [x] **4.3** Update `submit_answer()` to eager-load `rubric_version` and use weighted composite
- [x] **4.4** `list_sessions()` / `get_score_trends()` use stored `composite_score` — no changes needed (stores the weighted value)
- [x] **4.5** N/A for MVP — weights validated at rubric creation time (future coach UI)

---

### Gap 5 — Coach override UI (Backend + Frontend)
**Priority:** Medium
**Scope:** Backend + Frontend
**Complexity:** High

#### Backend
- [x] **5.1** Write failing tests for coach score service + router
- [x] **5.2** `app/services/coach_service.py` — `submit_coach_score()` + `list_sessions_for_review()`
- [x] **5.3** `app/schemas/coach.py` — `CoachScoreRequest`
- [x] **5.4** `app/api/v1/coach.py` — `POST /score` + `GET /sessions` with `_require_coach` guard; registered in main.py

#### Frontend
- [x] **5.5** `lib/api/coach.ts` — `submitCoachScore()`, `getSessionsForReview()`
- [x] **5.6** `app/(coach)/layout.tsx` — auth guard + coach nav bar
- [x] **5.7** `app/(coach)/review/page.tsx` — session review queue
- [x] **5.8** `app/(coach)/review/[sessionId]/page.tsx` — per-question score form
- [x] **5.9** `components/coach/CoachScoreForm.tsx` — 6 tests, all passing

---

## Order of execution

1. Gap 1 (logging) — quick win, unblocks observability
2. Gap 2 (retry) — quick win, improves reliability
3. Gap 3 (auth UI) — makes the app actually usable end-to-end
4. Gap 4 (rubric weights) — correctness fix
5. Gap 5 (coach UI) — largest, builds on everything above
