# MockReady — Authentication PRD (Frontend + Integration)

**Purpose:** Single implementation spec so an agent (e.g. Claude Code) can add end-to-end candidate authentication without rediscovering the codebase.

**Status:** Draft for implementation  
**Scope:** Email/password auth against the **existing** FastAPI backend. No new backend auth endpoints required unless explicitly noted in “Future.”

---

## 1. Background

### 1.1 What already exists (backend)

The backend implements JWT-based auth:

| Endpoint | Method | Request body | Success response |
|----------|--------|--------------|------------------|
| `/api/v1/auth/register` | POST | `{ "email": string, "password": string }` | `201` — `UserResponse`: `id`, `email`, `role`, `created_at` |
| `/api/v1/auth/login` | POST | `{ "email": string, "password": string }` | `200` — `TokenResponse`: `access_token`, `token_type` (`"bearer"`) |

**Password rules (register only):** min 8 chars, max 128, at least one uppercase letter and one digit (see `backend/app/schemas/auth.py`).

**Protected routes:** Session and related APIs use `get_current_user` (`backend/app/core/security.py`). Clients must send:

```http
Authorization: Bearer <access_token>
```

Tokens are HS256 JWTs signed with `SUPABASE_JWT_SECRET` (see `backend/app/core/config.py`). No refresh endpoint exists; access tokens expire after **24 hours** (`backend/app/services/auth_service.py`).

**Local development:** If `DEV_BYPASS_AUTH=true`, the backend skips JWT validation and uses a fixed dev user. Frontend auth work should still function when bypass is off (normal integration testing).

### 1.2 What is missing (frontend)

- No login or register UI.
- No calls to `/api/v1/auth/*`.
- Client components read **`process.env.NEXT_PUBLIC_API_TOKEN`** only (empty in dev unless set), so protected APIs return **401** without env or bypass.

**Files that currently hardcode the env token pattern (must be migrated to shared auth):**

- `frontend/components/session/DashboardClient.tsx`
- `frontend/components/session/SessionSetupClient.tsx`
- `frontend/components/session/SessionDetailClient.tsx`
- `frontend/components/session/InterviewSessionClient.tsx`

**Shared API layer:** `frontend/lib/api/client.ts` (`apiFetch`) already accepts an optional `token` and sets `Authorization` when truthy. `frontend/lib/api/sessions.ts` passes `token` through to every call.

---

## 2. Goals and non-goals

### Goals

1. Users can **register** and **log in** in the browser.
2. After login, **all** session API calls use the stored **access token** (not `NEXT_PUBLIC_API_TOKEN`).
3. **Unauthenticated** users hitting protected app routes are **redirected to login** (or see a clear path to log in).
4. Users can **log out** (clear token and client state).
5. Basic **error handling**: wrong password, duplicate email, network errors — user-visible messages.

### Non-goals (this PRD)

- OAuth / Google / GitHub / Supabase hosted UI (can be a later PRD).
- HttpOnly cookie sessions with a Next.js BFF (optional hardening; MVP may use `localStorage`).
- Password reset / email verification flows.
- Refresh tokens or sliding sessions (backend has none; re-login after expiry is acceptable for MVP).

---

## 3. Recommended architecture (MVP)

### 3.1 Token storage

**MVP:** Store `access_token` in **`localStorage`** under a single key, e.g. `mockready_access_token`.

**Rationale:** Matches client-side `fetch`, no new API routes required, fastest to ship. Document that this is acceptable for a course/demo app; production hardening would move tokens to httpOnly cookies.

### 3.2 Auth state

Provide a **React context** (e.g. `AuthProvider`) that:

- On mount, reads token from `localStorage` and exposes `{ token, isAuthenticated, isLoading, userEmail? }`.
- For MVP, **optional:** decode JWT payload client-side only to read `sub` (user id) or `exp` — or skip and only store token; email can be shown only after login from form state until a future `GET /me` exists.
- Exposes `login`, `register`, `logout`.

**`logout`:** remove token from `localStorage`, clear context state, `router.push("/login")` (or `/`).

### 3.3 API layer

Add **`frontend/lib/api/auth.ts`**:

- `register(body)` → `POST ${API_BASE}/api/v1/auth/register` — no `Authorization` header.
- `login(body)` → `POST ${API_BASE}/api/v1/auth/login` — returns `{ access_token, token_type }`.

Use the same `API_BASE` as `client.ts` (`NEXT_PUBLIC_API_URL` default `http://localhost:8000`). Reuse fetch error handling patterns from `apiFetch` (parse JSON `detail` on failure) for consistency.

### 3.4 Wiring tokens into session calls

**Preferred:** Wrap the app (or candidate segment) with `AuthProvider`, then either:

- **Option A:** Change session API functions to read token from `useAuth()` inside components only — components pass `token` to `getSessionHistory(token)` etc. (minimal change to `sessions.ts`), **or**
- **Option B:** Add `getAuthToken(): string | null` used by thin wrappers — still explicit.

Do **not** leave `NEXT_PUBLIC_API_TOKEN` as the primary path; it may remain as an **override for E2E tests** only if documented (optional).

---

## 4. Routing and pages

### 4.1 New routes

| Route | Purpose |
|-------|---------|
| `/login` | Email + password form, link to register |
| `/register` | Email + password form (validate client-side to match backend rules), link to login |

### 4.2 Root and navigation

- Add **`app/page.tsx`**: redirect to `/dashboard` if authenticated, else to `/login` (or a minimal landing with two buttons: Log in / Register). Pick one pattern and apply consistently.

### 4.3 Protected routes

These should require a valid token (or redirect to `/login`):

- `/dashboard`
- `/sessions/new`
- `/sessions/[id]`
- `/sessions/[id]/interview`

**Implementation options:**

- **Middleware** (`middleware.ts`): check for token cookie — **only if** token is in cookie; with `localStorage`, middleware cannot read it. So for `localStorage` MVP, use **client layouts** or **client guards**: a small `ProtectedLayout` that shows children only when `isAuthenticated`, else redirects via `useRouter` + `useEffect`.

**Important:** Next.js App Router: avoid flash of protected content — show a loading skeleton until auth hydration from `localStorage` completes.

---

## 5. UI requirements

### 5.1 Login page

- Fields: email, password.
- Submit → `login` API → store token → navigate to `/dashboard` (or `callbackUrl` query param if implemented).
- Link: “Create an account” → `/register`.
- Display API errors (401 invalid credentials, 503, etc.) near the form.

### 5.2 Register page

- Fields: email, password, confirm password (client-side match check).
- Client validation aligned with backend (length, uppercase, digit).
- Submit → `register` → then either auto-login (`login` with same credentials) or redirect to `/login` with success message. **Prefer auto-login** after successful register for fewer steps.

### 5.3 Global affordance

- Add a **header** or **nav bar** on authenticated pages: app title, optional email, **Log out** button. If no shared layout exists under `(candidate)`, add `app/(candidate)/layout.tsx` wrapping dashboard and sessions with this chrome.

---

## 6. Step-by-step implementation plan (for Claude Code)

Execute in order; each step should be committable.

### Phase A — API client

1. Create `frontend/lib/api/auth.ts` with `login` and `register` using `fetch` to backend URLs, typed responses matching `TokenResponse` and `UserResponse`.
2. Export shared `API_BASE` from a tiny `frontend/lib/api/config.ts` if needed to avoid duplicating env logic between `client.ts` and `auth.ts` (refactor `client.ts` to import base URL).

### Phase B — Auth context

3. Add `frontend/lib/auth/AuthContext.tsx` (or `contexts/AuthProvider.tsx`) with `localStorage` key constant, `login`/`register`/`logout`, and hydration `useEffect`.
4. Wrap the app in `AuthProvider` in `app/layout.tsx` (or only under candidate routes if you want public pages outside — wrapping root `layout` is simpler).

### Phase C — Pages

5. Add `app/login/page.tsx` and `app/register/page.tsx` (can be server components wrapping client forms, or client pages).
6. Add `app/page.tsx` with redirect logic (client component or middleware-compatible pattern).

### Phase D — Replace env token usage

7. Update `DashboardClient`, `SessionSetupClient`, `SessionDetailClient`, `InterviewSessionClient` to use `useAuth().token` (or equivalent) instead of `NEXT_PUBLIC_API_TOKEN`.
8. Ensure empty token shows login redirect or error state, not silent 401 loops.

### Phase E — Protection

9. Add `ProtectedRoute` / layout guard for `(candidate)` routes so unauthenticated users go to `/login`.
10. Optionally: redirect authenticated users away from `/login` and `/register` to `/dashboard`.

### Phase F — Polish and tests

11. Manual test: register → dashboard → sessions flow with `DEV_BYPASS_AUTH=false` and real DB.
12. Update or add frontend tests: mock `AuthContext` or localStorage in existing component tests.
13. Document env vars in `README` or frontend README: `NEXT_PUBLIC_API_URL`, optional test override, **no requirement** for `NEXT_PUBLIC_API_TOKEN` for normal use.

---

## 7. Acceptance criteria

- [ ] New user can register and land on an authenticated experience (dashboard or sessions).
- [ ] Existing user can log out and log back in.
- [ ] With backend bypass **disabled**, session APIs succeed after login without `.env` token hacks.
- [ ] Invalid login shows a clear error without crashing.
- [ ] Duplicate registration shows backend conflict message (409).
- [ ] Direct navigation to `/dashboard` while logged out redirects to `/login` (after hydration).

---

## 8. Environment variables

| Variable | Role |
|----------|------|
| `NEXT_PUBLIC_API_URL` | Backend base URL (already used by `client.ts`). |
| `NEXT_PUBLIC_API_TOKEN` | **Deprecated for normal use** after implementation; optional for CI/E2E only if kept. |

Backend must have matching `SUPABASE_JWT_SECRET` for tokens issued by `/login` to validate on protected routes.

---

## 9. Future enhancements (out of scope for first pass)

- `GET /api/v1/auth/me` returning current user from JWT (cleaner than client-side JWT decode).
- Refresh tokens or shorter access TTL with silent refresh.
- HttpOnly cookie + Next.js Route Handlers for login proxy.
- OAuth providers.

---

## 10. Reference — backend files

- Routes: `backend/app/api/v1/auth.py`
- Logic: `backend/app/services/auth_service.py`
- Schemas: `backend/app/schemas/auth.py`
- JWT validation: `backend/app/core/security.py`
- Settings: `backend/app/core/config.py`

---

## 11. Reference — frontend files to touch

- `frontend/lib/api/client.ts` — optional refactor for shared base URL
- `frontend/lib/api/sessions.ts` — likely unchanged signature; callers supply token
- `frontend/app/layout.tsx` — `AuthProvider`
- `frontend/app/(candidate)/*` — guard + nav
- Components listed in §1.2

End of document.
