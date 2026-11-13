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
- [.agents/skills/](.agents/skills/) - Project-specific agent skills.
- [todo/](todo/) - Git-ignored scratchpad for local notes; never committed.

---

## ⚖️ Hard Rules (every task)

These apply to every task. Each links to the file that holds the full rule.

- **Sole change path**: every change to `holon-agentic-coder` or `holon-coherence` is produced by the 5-stage Holon
  flow, driven with `holon flow <intent.json>`; never hand-patch a target repository outside it. The harness files in
  this repository (`.beans/`, `.agents/`, `AGENTS.md`) stay directly editable. See
  [holon-flow.md](.agents/holon-flow.md).
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

---

## 🚀 Incoming Agent Checklist

1. **Verify your environment**: check the working directory and locate `.beans`. If `apps/holon-agentic-coder/` or
   `apps/holon-coherence/` is missing, follow the checkout steps in [README.md](README.md).
2. **Pick up a task**: list [.beans/](.beans/) for your assignment, or log a new bean if none exists.
3. **Load constraints**: [.agents/rules.md](.agents/rules.md), then the task lifecycle in
   [.agents/workflows.md](.agents/workflows.md).
4. **Report**: summarise changes concisely and point to the updated files.

---

## 📦 The Beans Task System

Beans in [.beans/](.beans/) track one task or request each (config: [.beans.yml](.beans.yml)). IDs are strictly
sequential 4-digit integers (next = highest + 1, never random base36). Valid statuses: `draft`, `todo`, `in-progress`,
`completed`, `scrapped`; set `in-progress` when you start and `completed` with a summary when done. Full rules:
[.agents/workflows.md](.agents/workflows.md).
