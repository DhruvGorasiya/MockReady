# Individual Reflection — Dhruv Gorasiya
**Project:** MockReady | **Course:** AI Engineering, Northeastern University (Spring 2026)

---

## From Prompt-and-Pray to Systematic AI-Assisted Engineering

Before this project, my mental model of working with Claude was simple: describe a problem, get code, paste it in, fix what breaks. MockReady forced me to throw that model out entirely.

The single most impactful shift was investing in `CLAUDE.md` before writing a line of application code. We modularized it into separate docs — architecture, conventions, security, testing, workflow — imported via `@` references. The upfront cost felt wasteful at hour two. By week three, it was the reason Claude could jump into any part of the codebase cold and immediately produce code that matched our patterns. Without it, I estimate we would have spent at least thirty percent more time correcting stylistic and architectural drift. The git history of `CLAUDE.md` tells its own story: it evolved through seven meaningful commits, each one encoding a lesson we had just learned the hard way.

**Hooks changed my relationship with feedback loops.** We configured a `PostToolUse` hook that runs `ruff --fix-only` automatically after every Python file edit. The first time I saw Claude edit a service file and watch the linter self-correct in the same step — without me doing anything — I understood what "ambient automation" means in practice. We also added a `Stop` hook that prints the last few lines of the test summary at the end of every session, so the state of the test suite is never ambiguous when I close the terminal. Two hooks, but they eliminated an entire category of interruptions.

**The security reviewer agent** was the piece I'm most proud of technically. We wrote a custom sub-agent in `.claude/agents/` that performs an OWASP Top 10 audit on any new route or service file, scoped to findings-only — it never auto-fixes. That constraint was intentional. Security output should always go through a human before merge. Having it scoped that way meant we actually read every finding rather than rubber-stamping an automated fix.

**The create-pr skill** taught me something unexpected about AI tooling: the value is not just speed, it's consistency. Every pull request in this project has the same structure — summary, test plan, C.L.E.A.R. checklist, risk assessment, AI disclosure percentage. That consistency made reviews faster because the reviewer always knew where to look.

**Where I struggled:** worktrees. The concept clicked immediately — parallel branches for parallel features — but the workflow of managing two active worktrees while keeping `CLAUDE.md` in sync between them took real discipline. I got it wrong twice: once by editing a shared config file in one worktree and forgetting to port the change, and once by running migrations from the wrong directory. Both were recoverable, but the lesson was that parallel development requires parallel discipline, not just parallel branches.

**The CI pipeline** became a safety net I genuinely trusted by the end of the project, not a checkbox. When the Prettier check failed on Playwright report artifacts, I didn't investigate manually — I described the CI output to Claude Code, it diagnosed the missing `.prettierignore` entries in under a minute, committed the fix, and pushed. That two-minute loop, start to finish, is what production-grade AI-assisted engineering actually looks like. Not magic. Just fast, reliable, low-friction iteration.

The thing I will carry forward: **the investment in project infrastructure pays compounding returns**. Every hour in `CLAUDE.md`, hooks, and memory files saved multiple hours of context re-establishment and rework over the project's lifetime. That ratio only improves as projects grow longer.

---

*Word count: ~520*
