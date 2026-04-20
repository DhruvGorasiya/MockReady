# MockReady — Video Demo Script
**Duration:** 5–10 minutes (target ~7 min)
**Presenters:** Dhruv (first half) · Xing (second half)

---

## PART 1 — DHRUV (~3.5 minutes)

---

### [0:00 – 0:40] Introduction

> **[Screen: Landing page of MockReady]**

"Hey everyone. I'm Dhruv, and this is MockReady — an AI-powered technical interview prep platform that we built for our AI Engineering course at Northeastern.

The core problem we set out to solve is this: most interview prep tools give you binary feedback — right or wrong. They don't tell you *why* your explanation was unclear, or *how* your reasoning could be more structured. MockReady changes that.

Candidates do a full timed mock interview, and our AI evaluates every answer across five dimensions: Clarity, Depth, Structure, Relevance, and Communication — giving a score from 1 to 10 on each, plus written behavioral feedback. Coaches can then review those scores and override them with justification, building ground-truth training data over time."

---

### [0:40 – 1:10] Architecture in 30 Seconds

> **[Screen: Architecture diagram from README or a quick sketch]**

"Under the hood: Next.js 14 on the frontend, FastAPI on the backend, Supabase PostgreSQL for the database, and Anthropic's Claude Sonnet as our AI engine.

We run three parallel AI agents: one generates the interview question at session start, and when the candidate submits an answer, an Evaluation agent and a Feedback Synthesis agent run concurrently using asyncio.gather — so the candidate never waits longer than necessary.

Now let me show you the app."

---

### [1:10 – 2:00] Candidate Registration & Login

> **[Screen: /register page, then /login]**

"I'll register as a new candidate. I'll put in an email and password — nothing special here.

*[Fill in form and submit]*

And now I'll log in.

*[Log in and land on dashboard]*

This is the candidate dashboard. It shows my session history and score trends over time. Since this is a fresh account, it's empty — let me start a new session."

---

### [2:00 – 3:00] Running a Mock Interview Session

> **[Screen: Session setup page]**

"I'll click 'New Session'. I select my target role — let's say Software Engineer — and the interview type — Behavioral.

*[Submit session setup]*

The Question Generation agent fires here. It calls Claude Sonnet with the role and type as structured input, and within a couple of seconds, we get a question back. You can see it's a real, role-specific behavioral question — not a generic template.

*[Read the question out loud]*

Now I'll type my answer.

*[Type a moderately detailed answer — 3–4 sentences]*

And I'll submit."

---

### [3:00 – 3:30] Viewing AI Scores and Feedback

> **[Screen: Session detail / feedback view]**

"The Evaluation and Feedback agents ran in parallel the moment I submitted. Here are my results.

I can see a score on each of the five dimensions. *[Point to the dimension breakdown]* And below each score, there's specific written feedback that references what I actually said — not generic 'good job' comments.

This is the core value prop. A candidate can look at this, understand exactly what was weak, and work on it before the real interview.

I'll hand it over to Xing now, who will show the coach side and walk through how we used Claude Code to build this."

---

---

## PART 2 — XING (~3.5 minutes)

---

### [3:30 – 4:30] Coach Review Flow

> **[Screen: /coach/review — the coach queue]**

"Thanks Dhruv. I'm Xing, and I'll take you through the coach experience and our development workflow.

Here's the coach review queue. Coaches see sessions that have AI scores and are pending human review.

*[Click into a session]*

I can see the candidate's answer, the AI's dimensional scores, and the AI's written feedback. If I think the AI got something wrong — say the Depth score is too low because the candidate actually gave a sophisticated answer — I can override it.

*[Open the CoachScoreForm, change a score, add a justification, and submit]*

The key architectural decision here is that we never overwrite the AI score. Both scores persist — the AI score and the coach score live side by side in the database. The coach score is authoritative when present, but the AI score is kept as ground-truth training data for improving the model over time."

---

### [4:30 – 6:00] Claude Code Workflow

> **[Screen: VS Code or terminal with Claude Code open, CLAUDE.md visible]**

"Now let me show you how we actually built this — because using Claude Code was a core part of the assignment and it genuinely changed how we work.

Everything starts with CLAUDE.md. *[Open the file]* This is a project instruction file that Claude reads at the start of every session. We broke it into separate docs — architecture, conventions, security, testing, workflow — and import them with @ references. Claude always knows the full context before writing a single line of code.

**Hooks.** *[Open .claude/settings.json]* We configured post-edit hooks. Every time Claude edits a Python file, ruff runs automatically and fixes linting issues before we even see the change. That eliminated a whole category of back-and-forth.

**Memory.** *[Open .claude/MEMORY.md]* Claude maintains persistent memory across sessions. Here we have entries for our database connection config, our custom auth setup, known pre-existing bugs to avoid touching, and lessons learned from past mistakes. This meant we didn't have to re-explain context at the start of every session.

**Custom Agents.** *[Open .claude/agents/security-reviewer.md]* We built a security reviewer agent that runs an OWASP Top 10 audit on any new route or service file. It's scoped — findings only, no auto-fixes — so a human always reviews the security output before we merge.

**Custom Skills.** We have a create-pr skill that generates pull requests with a structured description, a test plan, a C.L.E.A.R. review checklist, and an AI disclosure statement. Every PR we merged during this project was created with that skill."

---

### [6:00 – 6:40] CI/CD Pipeline

> **[Screen: GitHub Actions on a recent PR]**

"On the CI side, every pull request runs: backend pytest with coverage gates, frontend ESLint, Prettier, TypeScript typecheck, Jest tests, a Gitleaks secrets scan, and an npm audit for critical vulnerabilities.

We also have an AI review job — *[point to the ai-review job]* — where Claude Code runs on the PR diff and posts a review as a comment. That was particularly useful for catching things like missing auth dependencies or improper error handling before a human reviewer even looked.

And here's something from earlier today — *[show the recent CI fix commit]* — Prettier was failing because it was trying to format generated Playwright report files. I asked Claude Code why CI was failing, it diagnosed it immediately, added two lines to .prettierignore, and committed. That kind of fast, low-friction debugging loop is what made Claude Code genuinely useful rather than just a code generator."

---

### [6:40 – 7:00] Closing

"To summarize: MockReady delivers dimensional AI feedback on mock interviews with a coach override layer. We built it fully test-driven, with Claude Code embedded into every step — from writing the first failing test, to reviewing PRs, to fixing CI.

The biggest insight from using Claude Code is that the investment in project instructions pays compounding dividends. Every hour we spent on CLAUDE.md, hooks, and memory saved us multiple hours of context-setting and rework later.

Thanks for watching."

---

## Timing Guide

| Section | Speaker | Approx. Time |
|---|---|---|
| Intro + problem | Dhruv | 0:00 – 0:40 |
| Architecture overview | Dhruv | 0:40 – 1:10 |
| Register + login | Dhruv | 1:10 – 2:00 |
| Session + AI feedback | Dhruv | 2:00 – 3:30 |
| Coach review flow | Xing | 3:30 – 4:30 |
| Claude Code workflow | Xing | 4:30 – 6:00 |
| CI/CD pipeline | Xing | 6:00 – 6:40 |
| Closing | Xing | 6:40 – 7:00 |

---

## Recording Tips

- Run the app locally before recording so there's no cold-start lag on the first API call.
- Have a session with answers already submitted so the coach review section has real data to show.
- Keep the browser zoom at ~110% so text is readable on screen.
- For the Claude Code section, have the terminal and VS Code side-by-side so viewers can see the file and the command output together.
- If the AI response takes more than 3 seconds during the live demo, narrate what's happening ("the evaluation and feedback agents are running in parallel right now") rather than sitting in silence.
