# MockReady — Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** March 2026  
**Authors:** Xuan Bai, Dhruv Gorasiya  
**Course:** CS Graduate AI Engineering, Northeastern University  
**Status:** Active — Sprint 1

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Mom Test Validation Summary](#2-mom-test-validation-summary)
3. [Product Vision](#3-product-vision)
4. [User Personas](#4-user-personas)
5. [User Stories and Acceptance Criteria](#5-user-stories-and-acceptance-criteria)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [AI Agent Architecture](#8-ai-agent-architecture)
9. [Evaluation System Design](#9-evaluation-system-design)
10. [Data Models](#10-data-models)
11. [API Design](#11-api-design)
12. [UI/UX Requirements](#12-uiux-requirements)
13. [Out of Scope](#13-out-of-scope)
14. [Success Metrics](#14-success-metrics)
15. [Open Questions](#15-open-questions)

---

## 1. Problem Statement

### The Core Problem

Candidates preparing for technical interviews have no reliable signal on whether their **explanation quality**, **reasoning process**, and **communication under pressure** are interview-ready. They practice in conditions that bear no resemblance to real interviews, receive binary correctness signals that tell them nothing about how they communicate, and receive zero dimensional feedback from actual interviews.

### Why Existing Tools Fail

| Tool            | What It Does                          | What It Misses                                                              |
| --------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| Leetcode        | Correctness grading                   | Explanation quality, communication, reasoning transparency                  |
| ChatGPT         | Answers questions, explains solutions | No adversarial coaching, no dimensional scoring, not realistic              |
| Pramp           | Peer mock interviews                  | Awkward pairing with strangers, scheduling friction, no structured feedback |
| Interviewing.io | Professional mock interviews          | Expensive, inaccessible for students                                        |

### The Specific Pain Points (Mom Test Validated)

1. No signal on whether explanation quality and reasoning process are interview-ready.
2. No structured post-interview debrief from companies or tools.
3. No simulation of real interview pressure and time constraints.
4. Existing AI tools lack adversarial coaching and dimensional scoring.
5. The feedback candidates want is specific, behavioral, and dimensional, not generic encouragement.

---

## 2. Mom Test Validation Summary

**Interview Date:** March 2026  
**Persona:** MS CS student at Northeastern, actively job hunting for SWE and AI/ML roles

### Key Validated Findings

**On preparation habits:**

- Prep is reactive and unstructured. Candidates rely on vibes, not systems.
- Tools like Pramp exist but create friction (peer awkwardness, cost, scheduling).
- The candidate had never done a full mock interview outside a classroom setting despite active job hunting.

**On feedback:**

- Companies give no actionable post-interview feedback.
- Human mentor feedback (when specific and behavioral) is highly valued.
- Candidates can self-assess dimensions like communication and clarity when prompted, but never do it naturally on their own.
- The "silence-while-thinking" behavior is a specific, known, and damaging pattern that candidates cannot fix without targeted feedback.

**On existing AI tools:**

- ChatGPT explanations are valued for interactivity but lack adversarial coaching.
- Typing answers to ChatGPT is not a realistic proxy for speaking under interview pressure.
- Binary pass/fail from Leetcode tells candidates nothing about readiness.

**Strongest validated quote:**

> "If it told me something I could not already tell myself — like your explanations are consistently unclear in the first 30 seconds, and here is what you should say instead — that is actionable. Generic feedback like 'good communication' is useless."

**Retention trigger identified:** Feedback must be specific, actionable, and not replicable through self-assessment alone.

---

## 3. Product Vision

MockReady is an AI-powered interview preparation platform that simulates realistic interview conditions and delivers specific, dimensional, behavioral feedback that candidates cannot generate on their own.

**One-line pitch:** Practice interviews with an AI that coaches like a mentor, not a grading rubric.

**What makes MockReady different:**

- Dimensional scoring across clarity, depth, structure, relevance, and communication quality — not binary pass/fail.
- Adversarial coaching: the AI pushes back, asks follow-up questions, and flags weak spots mid-session.
- Coaches can audit and override AI scores, creating a feedback loop that improves the system over time.
- Session history shows score trends over time, giving candidates a real signal on improvement.

---

## 4. User Personas

### Persona 1: The Candidate

**Name:** Target user is an MS CS or similar graduate student, or early-career SWE/PM/DS job seeker.  
**Goal:** Practice interviews and get specific, actionable feedback on explanation quality, reasoning transparency, and communication — not just correctness.  
**Frustrations:** No feedback from real interviews. Existing tools only grade correctness. Mock interviews with peers are awkward. Cannot tell if improvement is real.  
**Behavior:** Squeezes prep into gaps between classes and work. Practices reactively, not systematically. Has latent self-awareness that current tools do not surface.  
**Retention trigger:** Sees a specific, quantified pattern in their own behavior (e.g., "your first 30 seconds are consistently unclear") that they could not have identified themselves.

### Persona 2: The Coach/Reviewer

**Name:** Career advisor, TA, senior peer, or industry mentor.  
**Goal:** Review AI-scored sessions for candidates they are mentoring. Override scores where the AI misjudged. Add human context that the AI missed.  
**Frustrations:** No structured tool for giving interview feedback. Feedback is informal and not tracked over time.  
**Behavior:** Reviews sessions asynchronously. Adds written commentary alongside score overrides. Wants to see if their feedback is improving candidate outcomes.  
**Value to platform:** Their overrides become ground truth that calibrates the LLM-as-judge system.

### Persona 3: The Admin

**Name:** Platform operator or course instructor.  
**Goal:** Manage question banks, configure scoring rubrics per role and interview type, monitor AI evaluation accuracy at the platform level.  
**Frustrations:** No visibility into whether AI scoring is drifting or degrading over time.  
**Behavior:** Uses the Evaluation Dashboard to track AI-to-Coach agreement rate, detect score drift, and update rubrics when needed.

---

## 5. User Stories and Acceptance Criteria

### Candidate Stories

---

**US-C01: Select Interview Type and Role**

> As a Candidate, I want to select an interview type (behavioral, technical, system design) and a target role (SWE, PM, DS) so that I get questions relevant to my specific interview context.

**Acceptance Criteria:**

- [ ] Candidate can select from at least 3 interview types: behavioral, technical, system design.
- [ ] Candidate can select from at least 3 roles: SWE, PM, Data Science.
- [ ] Selection combination (e.g., "SWE + Technical") is passed to the Question Generation Agent as context.
- [ ] Questions returned are demonstrably different across role/type combinations.
- [ ] Selection UI is accessible before starting a session, not mid-session.

---

**US-C02: Conduct a Practice Interview Session**

> As a Candidate, I want to answer interview questions in a timed, realistic session so that I practice under conditions that resemble a real interview.

**Acceptance Criteria:**

- [ ] Session presents one question at a time with a visible countdown timer.
- [ ] Candidate submits a text response per question (voice input is out of scope for v1).
- [ ] AI may ask one follow-up question per answer to simulate real interviewer behavior.
- [ ] Session ends when all questions are answered or time expires.
- [ ] Candidate cannot edit a submitted answer.
- [ ] Session state is persisted so it can be resumed if interrupted.

---

**US-C03: Receive Multi-Dimensional Feedback**

> As a Candidate, I want to receive real-time AI evaluation of my responses with scores across multiple dimensions so that I know specifically where to improve.

**Acceptance Criteria:**

- [ ] Each response is scored on exactly 5 dimensions: Clarity, Depth, Structure, Relevance, Communication Quality.
- [ ] Each dimension is scored on a 1-10 integer scale.
- [ ] Each dimension score is accompanied by a 1-3 sentence behavioral explanation (not generic praise).
- [ ] A composite score is derived as a weighted average of the 5 dimensions.
- [ ] Feedback is displayed within 5 seconds of answer submission.
- [ ] Feedback language must be specific and reference the candidate's actual answer, not generic templates.

---

**US-C04: View Session History Dashboard**

> As a Candidate, I want a session history dashboard that shows my scores over time so that I can track real improvement across practice sessions.

**Acceptance Criteria:**

- [ ] Dashboard shows all past sessions with date, interview type, role, and composite score.
- [ ] Per-session view shows dimension-level scores for each question.
- [ ] Trend chart shows composite score over time (minimum last 10 sessions).
- [ ] Dimension-level trend is visible per dimension (e.g., "Clarity over last 10 sessions").
- [ ] Dashboard loads within 2 seconds.
- [ ] Empty state is handled gracefully with a prompt to start a first session.

---

**US-C05: View Detailed Per-Question Feedback**

> As a Candidate, I want to review detailed feedback for each question in a past session so that I can study what I did wrong and how to improve.

**Acceptance Criteria:**

- [ ] Each question in a session review shows: the original question, the candidate's answer, all 5 dimension scores, and the behavioral feedback per dimension.
- [ ] If a Coach has overridden a score, both the AI score and the Coach score are visible, with the Coach score marked as authoritative.
- [ ] Coach written commentary is displayed if present.
- [ ] Candidate can navigate between questions within a session review.

---

### Coach Stories

---

**US-K01: Review AI-Scored Sessions**

> As a Coach, I want to see a queue of AI-scored sessions assigned to me for review so that I can audit AI judgments efficiently.

**Acceptance Criteria:**

- [ ] Coach dashboard shows all sessions pending review, sorted by submission date.
- [ ] Each session in the queue shows: candidate name (or anonymized ID), interview type, role, composite AI score, and submission timestamp.
- [ ] Coach can open any session for detailed review.
- [ ] Coach can filter the queue by interview type, role, or score range.

---

**US-K02: Override Dimension Scores**

> As a Coach, I want to override individual dimension scores on a session so that the system learns from my judgment where the AI was wrong.

**Acceptance Criteria:**

- [ ] For each question in a session, Coach can override any or all of the 5 dimension scores.
- [ ] Override UI shows the AI score alongside the Coach input field.
- [ ] Coach must provide a written justification for each override (minimum 10 characters).
- [ ] Override is saved and immediately marked as the authoritative score for that dimension.
- [ ] Override data is persisted as a ground-truth record linked to the original AI scoring event.
- [ ] Coach can submit a partial review (override some questions, skip others).

---

**US-K03: Add Written Feedback to a Session**

> As a Coach, I want to add session-level written commentary so that the candidate receives qualitative feedback beyond score overrides.

**Acceptance Criteria:**

- [ ] Coach can add a free-text comment at the session level (not just per question).
- [ ] Comment is visible to the candidate in their session review.
- [ ] Comment supports a minimum of 1000 characters.
- [ ] Coach can edit the comment before marking the session review complete.

---

### Admin Stories

---

**US-A01: Manage the Question Bank**

> As an Admin, I want to add, edit, and deactivate questions in the question bank so that the platform always has high-quality, relevant questions available.

**Acceptance Criteria:**

- [ ] Admin can create a question with: text, interview type, role, difficulty (easy/medium/hard), and tags.
- [ ] Admin can edit any field of an existing question.
- [ ] Admin can deactivate a question so it is no longer surfaced by the Question Generation Agent.
- [ ] Admin can search and filter questions by type, role, difficulty, and tag.
- [ ] Deactivated questions are archived, not deleted, and remain linked to historical sessions.

---

**US-A02: View the Evaluation Dashboard**

> As an Admin, I want an Evaluation Dashboard that tracks AI scoring accuracy against Coach overrides so that I can monitor evaluation quality over time.

**Acceptance Criteria:**

- [ ] Dashboard shows: total sessions scored, total sessions reviewed by Coach, overall AI-Coach agreement rate (%), average score delta per dimension, and trend of agreement rate over time.
- [ ] Agreement rate is calculated per dimension and as an overall composite.
- [ ] Score drift (change in AI scoring patterns over time) is tracked and visualized.
- [ ] Admin can filter metrics by date range, role, and interview type.
- [ ] Dashboard data refreshes at least every 24 hours.
- [ ] All metrics are queryable via an internal API for export.

---

**US-A03: Configure Scoring Rubrics**

> As an Admin, I want to configure dimension weights per role so that the scoring reflects what actually matters for each role.

**Acceptance Criteria:**

- [ ] Admin can set a weight (0-100%) for each of the 5 dimensions per role.
- [ ] Weights per role must sum to 100%.
- [ ] Changes to weights apply to new sessions only, not retroactively.
- [ ] Current rubric configuration is visible and versioned (each change creates a new version record).

---

## 6. Functional Requirements

### 6.1 Authentication and Authorization

- Users authenticate via email/password or OAuth (Google).
- Role-based access control: Candidate, Coach, Admin. Roles are mutually exclusive in v1.
- Sessions are JWT-based with a configurable expiry.
- Candidates cannot access Coach or Admin views. Coaches cannot access Admin views.

### 6.2 Interview Session Engine

- Session is created with: candidateId, interviewType, role, configuredRubricVersion.
- Question Generation Agent is invoked at session start to produce a question set (3-5 questions per session in v1).
- Each answer submission triggers the Answer Evaluation Agent and Feedback Synthesis Agent in parallel.
- Session state machine: `CREATED -> IN_PROGRESS -> COMPLETED -> REVIEWED`.
- Incomplete sessions older than 48 hours are auto-expired and marked `ABANDONED`.

### 6.3 AI Agent Integration

- All three agents are invoked via an internal Agent Manager service.
- Agent calls are non-blocking where possible. Evaluation and Feedback agents run in parallel after answer submission.
- Every agent invocation is logged: agentId, input payload, output payload, latency (ms), model version, timestamp.
- Agent failures must be handled gracefully: retry once, then surface a user-facing error and log the failure event.

### 6.4 Scoring Engine

- Scores are stored as integers 1-10 per dimension per question.
- Composite score = weighted average using the active rubric for the session's role.
- If a Coach overrides a score, the override replaces the AI score in all candidate-facing views. Both values are stored in the database.
- Score history is immutable: no row is deleted, only superseded.

### 6.5 Coach Override Flow

- Override record contains: sessionId, questionId, dimension, aiScore, coachScore, coachJustification, coachId, timestamp.
- Override triggers a re-computation of the composite score for the affected question.
- Override data is fed into the LLM-as-judge calibration pipeline asynchronously.

### 6.6 LLM-as-Judge Pipeline

- Runs asynchronously after a Coach completes a session review.
- Inputs: original question, candidate answer, AI scores and reasoning, Coach scores and justification.
- Judge prompt instructs Claude to assess whether the AI score was justified given the Coach override.
- Output: agreement flag (agree/disagree), confidence score, reasoning text.
- Results are stored and surfaced in the Admin Evaluation Dashboard.

### 6.7 Notifications

- Candidate is notified (in-app) when a Coach review is complete on their session.
- Coach is notified (in-app) when a new session is assigned to their review queue.
- No email notifications in v1.

---

## 7. Non-Functional Requirements

### 7.1 Performance

- API responses (non-AI) must return within 500ms at the 95th percentile.
- AI agent responses (evaluation + feedback) must complete within 10 seconds per question.
- Session history dashboard must load within 2 seconds.
- System must support 50 concurrent users without degradation in v1.

### 7.2 Reliability

- Uptime target: 99.5% for v1.
- All agent calls include retry logic (1 retry with exponential backoff).
- Database writes are transactional. Partial state is not persisted.

### 7.3 Security

- No secrets or API keys stored in the repository. All credentials via environment variables or a secrets manager.
- OWASP Top 10 addressed prior to production deployment.
- User passwords hashed with bcrypt (minimum cost factor 12).
- All API endpoints require authentication except `/health` and `/auth`.
- Input validation on all user-submitted fields. No raw user input passed directly to LLM prompts without sanitization.
- Rate limiting on all API routes: 100 requests per minute per user.

### 7.4 Observability

- Structured logging (JSON) for all API requests and agent calls.
- APM instrumentation on all service endpoints.
- Error tracking integrated (e.g., Sentry).
- Uptime monitoring with alerting on downtime > 2 minutes.
- Key metrics tracked: session completion rate, agent latency p50/p95, evaluation agreement rate, error rate.

### 7.5 Scalability

- Architecture must support horizontal scaling of the API layer.
- Caching strategy required for: question bank queries, session history reads, rubric configuration.
- Cache invalidation strategy must be documented.

---

## 8. AI Agent Architecture

### 8.1 Question Generation Agent

**Trigger:** Session start  
**Inputs:**

- `interviewType`: behavioral | technical | system_design
- `role`: SWE | PM | DS
- `difficulty`: easy | medium | hard (set by candidate or defaulted to medium)
- `questionCount`: integer (default 3-5)
- `excludeQuestionIds`: list of previously seen question IDs for this candidate

**Outputs:**

- Array of question objects: `{ id, text, interviewType, role, difficulty, tags }`

**Behavior:**

- Generates questions dynamically using Claude, grounded by the active question bank.
- Does not repeat questions the candidate has seen in the last 5 sessions.
- Questions are logged and stored, not ephemeral.

**Parallelism:** Runs once at session start. Independent of other agents.

---

### 8.2 Answer Evaluation Agent

**Trigger:** Candidate submits an answer  
**Inputs:**

- `question`: full question text
- `answer`: candidate's submitted text
- `interviewType`: behavioral | technical | system_design
- `role`: SWE | PM | DS
- `rubric`: active rubric config (dimension weights)

**Outputs:**

- `scores`: `{ clarity: int, depth: int, structure: int, relevance: int, communicationQuality: int }`
- `reasoning`: `{ [dimension]: string }` — one sentence of reasoning per dimension

**Behavior:**

- Scores each dimension independently using a structured prompt.
- Reasoning must reference specific content from the candidate's answer.
- Must not score based on correctness alone. Communication quality and structure are evaluated regardless of answer correctness.

**Parallelism:** Runs in parallel with Feedback Synthesis Agent after answer submission.

---

### 8.3 Feedback Synthesis Agent

**Trigger:** Answer Evaluation Agent completes  
**Inputs:**

- `question`: full question text
- `answer`: candidate's submitted text
- `scores`: output from Answer Evaluation Agent
- `reasoning`: output from Answer Evaluation Agent
- `interviewType`, `role`

**Outputs:**

- `feedbackSummary`: 2-3 sentence overall summary of the answer
- `dimensionFeedback`: `{ [dimension]: string }` — 1-3 sentences of specific, behavioral, actionable feedback per dimension
- `improvementSuggestion`: one concrete action the candidate can take immediately

**Behavior:**

- Feedback must be behavioral and specific. It must reference what the candidate said or did not say.
- Must not produce generic phrases like "good job" or "needs improvement" without behavioral grounding.
- `improvementSuggestion` must be a single, specific, actionable sentence.

**Parallelism:** Runs in parallel with Answer Evaluation Agent. Waits on evaluation scores before synthesizing, but both are dispatched simultaneously and feedback waits on the evaluation result via async await.

---

## 9. Evaluation System Design

### 9.1 Scoring Schema

```
Dimension scores: integer 1-10
Composite score: weighted average, rounded to 1 decimal place
Score ownership: ai_score (initial), coach_score (override, authoritative if present)
```

### 9.2 LLM-as-Judge Flow

```
1. Coach completes a session review with at least one score override.
2. LLM-as-judge job is enqueued asynchronously.
3. Job invokes Claude with:
   - Original question
   - Candidate answer
   - AI scores + per-dimension reasoning
   - Coach override scores + justification
4. Claude outputs: agreement (bool per dimension), confidence (0.0-1.0), reasoning (string)
5. Output is stored in the eval_judgments table.
6. Admin dashboard aggregates judgment records for metrics.
```

### 9.3 Metrics Tracked

| Metric              | Description                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| Agreement Rate      | % of dimensions where AI score matches Coach score (within ±1 point)     |
| Average Score Delta | Mean absolute difference between AI and Coach scores per dimension       |
| Score Drift         | Rolling average of AI scores over time per dimension, tracked for trends |
| Judgment Confidence | Average LLM-as-judge confidence score over time                          |
| Override Rate       | % of sessions that receive at least one Coach override                   |

### 9.4 Ground Truth Data Model

Every Coach override becomes a labeled training example:

- Input: question + answer
- Label: Coach score + justification
- Context: AI score + AI reasoning

This data is queryable for future fine-tuning or few-shot prompt calibration.

---

## 10. Data Models

### User

```
id: uuid (PK)
email: string (unique)
passwordHash: string
role: enum (candidate, coach, admin)
createdAt: timestamp
updatedAt: timestamp
```

### Session

```
id: uuid (PK)
candidateId: uuid (FK -> User)
interviewType: enum (behavioral, technical, system_design)
role: enum (SWE, PM, DS)
status: enum (created, in_progress, completed, reviewed, abandoned)
rubricVersionId: uuid (FK -> RubricVersion)
startedAt: timestamp
completedAt: timestamp
createdAt: timestamp
```

### Question

```
id: uuid (PK)
text: string
interviewType: enum
role: enum
difficulty: enum (easy, medium, hard)
tags: string[]
isActive: boolean
createdAt: timestamp
updatedAt: timestamp
```

### SessionQuestion

```
id: uuid (PK)
sessionId: uuid (FK -> Session)
questionId: uuid (FK -> Question)
questionText: string (snapshot at time of session)
orderIndex: integer
candidateAnswer: string
submittedAt: timestamp
```

### EvaluationScore

```
id: uuid (PK)
sessionQuestionId: uuid (FK -> SessionQuestion)
scoredBy: enum (ai, coach)
coachId: uuid (FK -> User, nullable)
clarity: integer (1-10)
depth: integer (1-10)
structure: integer (1-10)
relevance: integer (1-10)
communicationQuality: integer (1-10)
compositeScore: decimal
reasoning: jsonb
justification: string (nullable, required for coach scores)
createdAt: timestamp
```

### AgentLog

```
id: uuid (PK)
agentId: string
sessionId: uuid (FK -> Session)
sessionQuestionId: uuid (FK -> SessionQuestion, nullable)
inputPayload: jsonb
outputPayload: jsonb
latencyMs: integer
modelVersion: string
success: boolean
errorMessage: string (nullable)
createdAt: timestamp
```

### EvalJudgment

```
id: uuid (PK)
sessionQuestionId: uuid (FK -> SessionQuestion)
aiScoreId: uuid (FK -> EvaluationScore)
coachScoreId: uuid (FK -> EvaluationScore)
dimension: string
agreementFlag: boolean
confidenceScore: decimal (0.0-1.0)
reasoning: string
createdAt: timestamp
```

### RubricVersion

```
id: uuid (PK)
role: enum
weights: jsonb (e.g., { clarity: 0.2, depth: 0.2, structure: 0.2, relevance: 0.2, communicationQuality: 0.2 })
createdBy: uuid (FK -> User)
createdAt: timestamp
```

---

## 11. API Design

All endpoints prefixed with `/api/v1`. All requests require `Authorization: Bearer <token>` except auth routes.

### Auth

```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
GET    /auth/me
```

### Sessions

```
POST   /sessions                        # Create new session (candidate)
GET    /sessions/:id                    # Get session details
PATCH  /sessions/:id/status             # Update session status
GET    /sessions/history                # Get candidate session history
POST   /sessions/:id/questions/:qid/answer   # Submit answer to a question
GET    /sessions/:id/feedback           # Get full session feedback
```

### Coach

```
GET    /coach/queue                     # Get review queue
GET    /coach/sessions/:id              # Get session for review
POST   /coach/sessions/:id/overrides    # Submit score overrides
POST   /coach/sessions/:id/comment     # Add session-level comment
PATCH  /coach/sessions/:id/complete    # Mark review as complete
```

### Admin

```
GET    /admin/questions                 # List questions
POST   /admin/questions                 # Create question
PATCH  /admin/questions/:id             # Edit question
PATCH  /admin/questions/:id/deactivate  # Deactivate question
GET    /admin/rubrics                   # List rubric versions
POST   /admin/rubrics                   # Create new rubric version
GET    /admin/evals/dashboard           # Get evaluation dashboard metrics
GET    /admin/evals/judgments           # List LLM-as-judge records
```

### Health

```
GET    /health                          # Liveness check (no auth required)
```

---

## 12. UI/UX Requirements

### Candidate Flow

1. **Onboarding screen:** Select role and interview type. Brief explanation of what to expect. Start session button.
2. **Session screen:** Question displayed prominently. Timer visible. Text input for answer. Submit button. Follow-up question appears inline after submission if triggered.
3. **Feedback screen:** Per-question dimension scores shown as a visual breakdown (e.g., bar or radar chart). Behavioral feedback per dimension. Improvement suggestion highlighted. Navigation between questions.
4. **Session history dashboard:** List of past sessions. Trend chart for composite score. Ability to drill into any past session.

### Coach Flow

1. **Review queue:** List of sessions awaiting review. Basic session metadata visible at a glance.
2. **Session review screen:** Original question, candidate answer, AI scores, and reasoning side by side. Override inputs inline. Written comment field at the bottom. Submit review button.

### Admin Flow

1. **Question bank management:** Table view with search and filter. Add/edit/deactivate actions.
2. **Rubric configuration:** Per-role weight sliders. Validation that weights sum to 100%. Version history visible.
3. **Evaluation dashboard:** KPI tiles for agreement rate, override rate, score drift. Time-series charts. Filter controls.

### General UI Requirements

- Responsive: Desktop and tablet. Mobile is not a v1 requirement.
- Accessible: WCAG 2.1 AA minimum.
- Loading states are required for all async operations (agent calls, dashboard loads).
- Error states are required for all API failures. Generic "something went wrong" is not acceptable — error messages must be actionable.

---

## 13. Out of Scope (v1)

- Voice input or audio recording of candidate answers.
- Real-time speech-to-text.
- Mobile-native application.
- Video interview simulation.
- Email notifications.
- Direct candidate-to-coach messaging.
- Public question submission by candidates.
- Fine-tuning or training custom models. (LLM-as-judge uses Claude via API only.)
- Multi-language support.
- Payment or subscription management.

---

## 14. Success Metrics

| Metric                        | Target (End of v1)                       |
| ----------------------------- | ---------------------------------------- |
| Session completion rate       | > 70% of started sessions completed      |
| Candidate NPS (informal)      | Positive sentiment in demo feedback      |
| AI-Coach agreement rate       | > 75% within ±1 point per dimension      |
| Agent latency p95             | < 10 seconds per answer evaluation       |
| Evaluation Dashboard coverage | 100% of Coach-reviewed sessions included |
| Test coverage                 | > 80% on all core service modules        |

---

## 15. Open Questions

| #   | Question                                                              | Owner        | Status                                                              |
| --- | --------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------- |
| 1   | Final tech stack: framework, database, hosting provider?              | Xuan + Dhruv | **Decided: Next.js + FastAPI + Supabase (PostgreSQL) + SQLAlchemy** |
| 2   | Monolith vs microservices decision?                                   | Xuan + Dhruv | Open — Sprint 1                                                     |
| 3   | Which deployment platform: Render, Railway, AWS?                      | Xuan + Dhruv | Open — Sprint 1                                                     |
| 4   | Should follow-up questions be generated dynamically or templated?     | Xuan + Dhruv | Open — Sprint 1                                                     |
| 5   | How are Coach assignments made — manual, round-robin, or self-select? | Xuan + Dhruv | Open — Sprint 1                                                     |
| 6   | Is the question bank seeded manually or via AI generation at launch?  | Xuan + Dhruv | Open — Sprint 1                                                     |
| 7   | What caching layer? Redis vs in-memory?                               | Xuan + Dhruv | Open — Sprint 1                                                     |

---

_This PRD is a living document. Update it as architectural decisions are made in sprint planning. Claude Code should treat this as the authoritative source of truth for feature requirements._
