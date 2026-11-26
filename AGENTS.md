# Agent Landing Page & Entrypoint

> [!NOTE] **Bootstrapping Harness Intent** This repository is a temporary control plane and metadata store. It will only
> be used until the bootstrap process for
> [holon-agentic-coder](https://github.com/Holon-Agentic-Coder/holon-agentic-coder) is fully completed. Until that
> repository is fully bootstrapped, it does not possess enough autonomous power to develop or maintain itself. This
> repository serves as the external harness to bridge that gap.

Welcome, Agent. This document is your starting point for operating within this workspace. Read this document in its
entirety before performing any operations or modifying any code.

---

## 🎯 Quick Navigation

- [README.md](README.md) - Architecture and overview.
- [.agents/instructions.md](.agents/instructions.md) - Operating principles.
- [.agents/rules.md](.agents/rules.md) - Coding standards, file handling, sandbox.
- [.agents/workflows.md](.agents/workflows.md) - Task cycle, beans, git, PRs.
- [.agents/submodules.md](.agents/submodules.md) - Submodules and embedded repositories.
- [.agents/coordination.md](.agents/coordination.md) - Delegation and peer coordination.
- [.agents/model-tiers.md](.agents/model-tiers.md) - Model tiers; skills name a tier, never a model.
- [.agents/holon-flow.md](.agents/holon-flow.md) - The 5-stage Holon flow and `holon flow`.
- [.agents/worktrees-and-git.md](.agents/worktrees-and-git.md) - Worktrees, naming, formatting, squash rules.
- [.agents/pr-merging.md](.agents/pr-merging.md) - Human-only PR merging, post-merge protocol.
- [.agents/engineering-rules.md](.agents/engineering-rules.md) - Benchmarks, tokens, isolation, tests, ledgers.
- [.agents/subagents.md](.agents/subagents.md) - Subagent invocation, Antigravity runtime.
- [.agents/self-improvement-audit.md](.agents/self-improvement-audit.md) - Self-improvement audit at session start and
  every fifth merge.
- [.agents/skills/](.agents/skills/) - Project-specific agent skills.
- [todo/](todo/) - Git-ignored scratchpad for local notes; never committed.

---

## ⚖️ Hard Rules (every task)

These apply to every task. Each links to the file that holds the full rule.

- **Sole change path**: every change to `holon-agentic-coder` or `holon-coherence` is produced by the 5-stage Holon
  flow, driven with `holon flow <intent.json>`; never hand-patch a target repository outside it. The harness files in
  this repository (`.beans/`, `.agents/`, `AGENTS.md`) stay directly editable. See
  [holon-flow.md](.agents/holon-flow.md).
- **Never pass `--skip-review`** (to `holon flow` or any wrapper). No case needs it (maintainer, 2026-11-21); if Stage 4
  fails or stalls, halt and report instead of bypassing review. See [holon-flow.md](.agents/holon-flow.md).
- **Default Holon coding model**: use `antigravity-agent` with `gemini-4-neon` for all Holon coding tasks until tokens
  run out, then fall back to `gemini-4-argon` $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash`
  (maintainer, 2026-11-24). See [holon-flow.md](.agents/holon-flow.md).
- **Never merge a PR that targets `main`**, enable auto-merge or use the merge queue; the human maintainer merges. Stop
  after consensus approval and calibration, and report. See [pr-merging.md](.agents/pr-merging.md).
- **One worktree per agent**, named for the flow or bean; the `main` worktrees are off-limits (never edit, stage, commit
  or build in them). Hand-authored harness branches: squash once at the very end, never over commits you did not author;
  never rewrite or force-push a flow branch. See [worktrees-and-git.md](.agents/worktrees-and-git.md).
- **Tests**: only `uv run pytest`; never `unittest`, bare `pytest` or a `PYTHONPATH` override. See
  [engineering-rules.md](.agents/engineering-rules.md).
- **Target repositories** never reference harness paths (`.beans/`, `todo/`, `.agents/`); keep exactly three append-only
  ledgers (`intents`, `plans`, `executions`); no synthetic data for benchmarks; keep updates dense and token-cheap. See
  [engineering-rules.md](.agents/engineering-rules.md).
- **Format before commit**: `npx prettier --write "**/*.md"` in the harness; only changed files in a target worktree.
- **Subagents** follow [subagents.md](.agents/subagents.md) and the model tiers in
  [model-tiers.md](.agents/model-tiers.md); post-merge steps run through the `post-pr-merge` skill.
- **Flow concurrency & merge backfill**: up to **4 concurrent `holon-flow` background subagents** may run at once on
  hosted runtimes (local runtimes stay at 1). Once a target-repo PR merges and `post-pr-merge` completes, automatically
  pick up and launch the next highest-priority ready bean (honouring `blocked_by`, solo-sweep rules, and disjoint touch
  sets) to keep up to 4 flows running (maintainer, 2026-11-24). A blocked flow (Stage 3 overlap refusal or waiting on
  another flow's PR) does not hold a slot: park it, backfill at once, and resume parked flows from their checkpoint
  ahead of new beans (maintainer, 2026-11-26). See [coordination.md](.agents/coordination.md) and
  [pr-merging.md](.agents/pr-merging.md).
- **Coordinator failure ledger**: every coordinator failure (halt, park, wasted run, false readiness, wrong brief) is
  appended to [.agents/ledger/coordinator-failures.jsonl](.agents/ledger/coordinator-failures.jsonl) with its preventive
  rule before moving on (maintainer, 2026-11-27). See [coordination.md](.agents/coordination.md).
- **Self-improvement audit**: at the start of every session and after every fifth merge, a dedicated subagent runs a
  comprehensive audit for self-improvement (pipeline, flow, coding standards, architecture standards, harness) and logs
  one bean per suggestion; the brief says plainly that it is a self-improvement audit (maintainer, 2026-11-24). See
  [self-improvement-audit.md](.agents/self-improvement-audit.md).

---

## 🚀 Incoming Agent Checklist

1. **Verify your environment**: check the working directory and locate `.beans`. If `apps/holon-agentic-coder/` or
   `apps/holon-coherence/` is missing, follow the checkout steps in [README.md](README.md).
2. **Run the self-improvement audit**: spawn the audit subagent described in
   [.agents/self-improvement-audit.md](.agents/self-improvement-audit.md) and carry on; do not wait for it.
3. **Read the coordinator failure ledger**: read
   [.agents/ledger/coordinator-failures.jsonl](.agents/ledger/coordinator-failures.jsonl) and apply its rules to every
   brief, readiness check and launch.
4. **Pick up a task**: list [.beans/](.beans/) for your assignment, or log a new bean if none exists.
5. **Load constraints**: [.agents/rules.md](.agents/rules.md), then the task lifecycle in
   [.agents/workflows.md](.agents/workflows.md).
6. **Report**: summarise changes concisely and point to the updated files.

---

## 📦 The Beans Task System

Beans in [.beans/](.beans/) track one task or request each (config: [.beans.yml](.beans.yml)). IDs are strictly
sequential 4-digit integers (next = highest + 1, never random base36). Valid statuses: `draft`, `todo`, `in-progress`,
`completed`, `scrapped`; set `in-progress` when you start and `completed` with a summary when done. Full rules:
[.agents/workflows.md](.agents/workflows.md).
