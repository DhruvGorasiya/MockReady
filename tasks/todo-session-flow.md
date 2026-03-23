# Task: Interview Session Flow (US-C01, US-C02, US-C03)

**PRD Reference:** US-C01 — Select Interview Type and Role, US-C02 — Conduct a Practice Interview Session, US-C03 — Receive Multi-Dimensional Feedback
**Branch:** `feature/session-flow`
**Status:** Planning

---

## Acceptance Criteria (from PRD)

### US-C01
- [ ] Candidate can select from 3 interview types: behavioral, technical, system_design
- [ ] Candidate can select from 3 roles: SWE, PM, DS
- [ ] Selection is passed to the Question Generation Agent as context
- [ ] Questions returned are demonstrably different across role/type combinations

### US-C02
- [ ] Session presents one question at a time with a visible countdown timer
- [ ] Candidate submits a text response per question
- [ ] Session ends when all questions are answered
- [ ] Candidate cannot edit a submitted answer
- [ ] Session state is persisted (created → in_progress → completed)

### US-C03
- [ ] Each response is scored on 5 dimensions: Clarity, Depth, Structure, Relevance, Communication Quality
- [ ] Each dimension scored 1-10
- [ ] Each dimension score has a 1-3 sentence behavioral explanation
- [ ] A composite score is derived as weighted average
- [ ] Feedback displayed within 5 seconds of answer submission
- [ ] Feedback references the candidate's actual answer (not generic)

---

## Implementation Plan

### Phase 1 — Backend: AgentLog Model + Migration

- [ ] **1.1** Create `backend/app/models/agent_log.py` — `AgentLog` ORM model (id, agent_id, session_id FK, session_question_id FK nullable, input_payload JSONB, output_payload JSONB, latency_ms int, model_version str, success bool, error_message str nullable, created_at)
- [ ] **1.2** Add `AgentLog` to `backend/app/models/__init__.py`
- [ ] **1.3** Write Alembic migration for `agent_logs` table
- [ ] **1.4** Run `alembic upgrade head`

---

### Phase 2 — Backend: New Schemas

- [ ] **2.1** Add to `backend/app/schemas/session.py`:
  - `CreateSessionRequest` — interview_type, role, question_count (default 3)
  - `SessionCreatedResponse` — id, interview_type, role, status, questions: list[QuestionInSession]
  - `QuestionInSession` — id (SessionQuestion id), question_text, order_index
  - `SubmitAnswerRequest` — answer: str
  - `DimensionFeedback` — clarity, depth, structure, relevance, communication_quality (each str)
  - `AnswerFeedbackResponse` — session_question_id, ai_scores: DimensionScores, composite_score: float, feedback_summary: str, dimension_feedback: DimensionFeedback, improvement_suggestion: str

---

### Phase 3 — Backend: Agents (TDD)

- [ ] **3.1** Write failing tests in `backend/app/tests/test_question_generation_agent.py`:
  - `test_generates_questions_for_swe_technical`
  - `test_generates_questions_for_pm_behavioral`
  - `test_returns_requested_question_count`
  - `test_handles_anthropic_api_error`
  - `test_question_text_is_non_empty`
- [ ] **3.2** Implement `backend/app/agents/question_generation.py`:
  - `async def generate_questions(interview_type, role, question_count, exclude_ids) -> list[dict]`
  - Calls Claude API with structured prompt, returns list of `{text, interview_type, role}`
  - Logs invocation to AgentLog
- [ ] **3.3** Run question generation tests — all GREEN

- [ ] **3.4** Write failing tests in `backend/app/tests/test_answer_evaluation_agent.py`:
  - `test_returns_five_dimension_scores`
  - `test_scores_are_integers_1_to_10`
  - `test_returns_reasoning_per_dimension`
  - `test_handles_anthropic_api_error`
  - `test_reasoning_references_answer_content`
- [ ] **3.5** Implement `backend/app/agents/answer_evaluation.py`:
  - `async def evaluate_answer(question, answer, interview_type, role, rubric) -> dict`
  - Returns `{scores: DimensionScores, reasoning: dict[str, str]}`
  - Logs invocation
- [ ] **3.6** Run evaluation tests — all GREEN

- [ ] **3.7** Write failing tests in `backend/app/tests/test_feedback_synthesis_agent.py`:
  - `test_returns_feedback_summary`
  - `test_returns_dimension_feedback_for_all_five`
  - `test_returns_improvement_suggestion`
  - `test_handles_anthropic_api_error`
  - `test_feedback_is_not_generic`
- [ ] **3.8** Implement `backend/app/agents/feedback_synthesis.py`:
  - `async def synthesize_feedback(question, answer, scores, reasoning, interview_type, role) -> dict`
  - Returns `{feedback_summary, dimension_feedback, improvement_suggestion}`
  - Logs invocation
- [ ] **3.9** Run feedback synthesis tests — all GREEN

---

### Phase 4 — Backend: Service Layer (TDD)

- [ ] **4.1** Write failing tests in `backend/app/tests/test_session_service_write.py`:
  - `test_create_session_returns_session_with_questions`
  - `test_create_session_seeds_rubric_if_none_exists`
  - `test_create_session_snapshots_question_text`
  - `test_create_session_status_is_in_progress`
  - `test_submit_answer_saves_candidate_answer`
  - `test_submit_answer_stores_ai_scores`
  - `test_submit_answer_runs_evaluation_and_feedback_in_parallel`
  - `test_submit_answer_completes_session_on_last_question`
  - `test_submit_answer_raises_404_for_wrong_session`
  - `test_submit_answer_raises_409_if_already_answered`
- [ ] **4.2** Implement in `backend/app/services/session_service.py`:
  - `async def create_session(db, candidate_id, request: CreateSessionRequest) -> SessionCreatedResponse`
    - Seeds default RubricVersion if none exists for role
    - Calls `question_generation` agent
    - Creates Session (status=in_progress) + SessionQuestion rows (with question_text snapshot)
  - `async def submit_answer(db, session_id, question_id, candidate_id, answer) -> AnswerFeedbackResponse`
    - Validates session ownership + question belongs to session
    - Raises 409 if already answered
    - Saves `candidate_answer` to SessionQuestion
    - Calls evaluation + feedback agents via `asyncio.gather()`
    - Saves EvaluationScore (scored_by=ai)
    - Marks session completed if all questions answered
    - Returns AnswerFeedbackResponse
- [ ] **4.3** Run tests — all GREEN

---

### Phase 5 — Backend: Route Handlers (TDD)

- [ ] **5.1** Write failing tests in `backend/app/tests/test_sessions_router_write.py`:
  - `test_create_session_returns_201`
  - `test_create_session_requires_auth`
  - `test_create_session_invalid_type_returns_422`
  - `test_submit_answer_returns_200_with_feedback`
  - `test_submit_answer_requires_auth`
  - `test_submit_answer_404_wrong_session`
- [ ] **5.2** Add to `backend/app/api/v1/sessions.py`:
  - `POST /api/v1/sessions` → `session_service.create_session`
  - `POST /api/v1/sessions/{session_id}/questions/{question_id}/answer` → `session_service.submit_answer`
- [ ] **5.3** Run tests — all GREEN; full backend suite GREEN

---

### Phase 6 — Frontend: Types + API Client

- [ ] **6.1** Add to `frontend/lib/types/session.ts`:
  - `QuestionInSession`, `CreateSessionRequest`, `SessionCreatedResponse`
  - `SubmitAnswerRequest`, `DimensionFeedback`, `AnswerFeedbackResponse`
- [ ] **6.2** Add to `frontend/lib/api/sessions.ts`:
  - `createSession(request, token): Promise<SessionCreatedResponse>`
  - `submitAnswer(sessionId, questionId, answer, token): Promise<AnswerFeedbackResponse>`
- [ ] **6.3** Run `tsc --noEmit` — clean

---

### Phase 7 — Frontend: Session Setup Page (TDD)

- [ ] **7.1** Write failing tests — `__tests__/app/sessionSetup.test.tsx` (5 tests):
  - renders interview type selector with 3 options
  - renders role selector with 3 options
  - start button disabled until both selected
  - calls createSession on submit
  - redirects to /sessions/[id]/interview on success
- [ ] **7.2** Implement `frontend/app/(candidate)/sessions/new/page.tsx` + `SessionSetupClient.tsx`
- [ ] **7.3** Run tests — 5/5 GREEN

---

### Phase 8 — Frontend: Interview Session Screen (TDD)

- [ ] **8.1** Write failing tests — `__tests__/app/interviewSession.test.tsx` (7 tests):
  - renders question text
  - renders question counter (e.g., "Question 1 of 3")
  - renders countdown timer
  - answer textarea is editable before submit
  - submit button calls submitAnswer
  - answer textarea disabled after submit
  - renders feedback scores after submission
- [ ] **8.2** Implement `frontend/components/session/InterviewSessionClient.tsx` — fetches session detail, shows one question at a time, countdown timer (120s per question), text area, submit → calls submitAnswer → shows AnswerFeedback inline, Next button
- [ ] **8.3** Create `frontend/app/(candidate)/sessions/[id]/interview/page.tsx` — thin wrapper
- [ ] **8.4** Run tests — 7/7 GREEN

---

### Phase 9 — Frontend: Feedback Display Component (TDD)

- [ ] **9.1** Write failing tests — `__tests__/components/AnswerFeedback.test.tsx` (5 tests):
  - renders composite score
  - renders feedback summary
  - renders all 5 dimension scores
  - renders improvement suggestion
  - renders dimension feedback text
- [ ] **9.2** Implement `frontend/components/session/AnswerFeedback.tsx`
- [ ] **9.3** Run tests — 5/5 GREEN; full suite GREEN; `tsc --noEmit` clean

---

### Phase 10 — Verification

- [ ] **10.1** Run full backend test suite — target >80% on agents/ and services/
- [ ] **10.2** Run frontend tests — all GREEN
- [ ] **10.3** Run linters — `ruff check backend/` and `npm run lint`
- [ ] **10.4** Manual smoke test: create session → answer all questions → see scores → view in dashboard history
- [ ] **10.5** Confirm all US-C01/02/03 acceptance criteria met

---

## Architecture Notes

```
POST /api/v1/sessions
  └── sessions router
        └── session_service.create_session()
              └── question_generation agent (Claude API)
              └── Session + SessionQuestion rows created

POST /api/v1/sessions/{id}/questions/{qid}/answer
  └── sessions router
        └── session_service.submit_answer()
              └── asyncio.gather(
                    answer_evaluation agent,
                    feedback_synthesis agent
                  )
              └── EvaluationScore row saved (scored_by=ai)
              └── Session status → completed (if last question)
              └── Returns AnswerFeedbackResponse

Frontend session flow:
  /sessions/new         → SessionSetupClient (select type + role)
  /sessions/[id]/interview → InterviewSessionClient (Q&A + inline feedback)
  /dashboard            → DashboardClient (history now populated)
```

**Key constraints:**
- Evaluation + Feedback agents MUST run via `asyncio.gather()` — never sequentially
- Every agent invocation logged to `agent_logs` table
- `question_text` snapshotted into `SessionQuestion.question_text` at session creation — never re-fetched
- Default RubricVersion (equal weights: 0.2 each) seeded per role if none exists
- Session moves to `in_progress` on creation, `completed` when last answer submitted

---

## Review

_To be filled in after implementation._
