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

- [README.md](README.md) - Repository architecture and general overview.
- [.agents/instructions.md](.agents/instructions.md) - General operating principles and behavioral guidelines.
- [.agents/rules.md](.agents/rules.md) - Coding standards, file handling, and sandbox constraints.
- [.agents/workflows.md](.agents/workflows.md) - Task execution cycle, git guidelines, and PR procedures.
- [.agents/submodules.md](.agents/submodules.md) - Git submodules management and embedded repository workflows.
- [.agents/coordination.md](.agents/coordination.md) - Delegation, subagent communication, and peer coordination
  protocols.
- [.agents/skills/](.agents/skills/) - Project-specific agent skills and capability guidelines.
- [todo/](todo/) - Temporary scratchpad directory for local agent files, documents, and notes (git ignored).

---

## 🚀 Incoming Agent Checklist

When you are spawned or begin a new session, follow these steps sequentially:

1. **Verify Your Environment**: Check the current working directory, workspace structure, and locate the `.beans`
   configuration. If the target repositories (`apps/holon-agentic-coder/` or `apps/holon-coherence/`) are not set up,
   follow the checkout instructions in [README.md](README.md#-target-repositories-setup-git-worktree) to clone the bare
   repositories and configure worktrees.
2. **Review the Tasks**: List the tasks in the [.beans/](.beans/) directory to determine your current assignment or log
   a new task if none exists.
3. **Internalize Constraints**: Load [.agents/rules.md](.agents/rules.md) to understand linting rules, language choices,
   and test requirements.
4. **Execute Tasks Systematically**: Follow the lifecycle specified in [.agents/workflows.md](.agents/workflows.md) to
   transition tasks from `todo` to `in-progress` and finally `completed`.
5. **Per-Agent Worktrees (Autonomous Branches Are Allowed)**: Every agent gets **its own worktree per project** and
   works **exclusively** inside it. Creating that branch and worktree is autonomous -- no user instruction required:
   - For `apps/holon-agentic-coder/`, all development and feature work must be based off the `origin/main` branch.
   - For `apps/holon-coherence/`, all development and feature work must be based off the `origin/main` branch.
   - Name the worktree and branch after you or your bean (for example
     `apps/holon-coherence/fix-0027-host-local-llm-routing` for branch `fix/0027-host-local-llm-routing`) so concurrent
     agents never share a directory or a branch.
   - Create it from the bare repository directory with
     `git worktree add --no-track -b {branch} ../{branch} origin/main`. Note that `../` resolves relative to
     `<project>/.git`, which is what places the checkout at `<project>/{branch}`.
   - Each worktree needs its own environment: virtualenvs are per-directory and cannot be shared, so run
     `uv sync --group dev` inside the new worktree and never point at another worktree's `.venv/`.
   - Inside your own worktree you have full latitude to edit, commit, squash, test, rebuild images and push.
   - **The `main` worktree is the user's playground.** `apps/holon-agentic-coder/main` and `apps/holon-coherence/main`
     are off-limits to agents: never edit, stage, commit, stash, reset, clean or checkout in them, never build into or
     leave stray files there, and do not mutate their local state either (`.venv/`, caches, generated artifacts).
   - If changes have already landed in a `main` worktree, move them into a dedicated worktree and restore `main` to a
     pristine checkout of its committed state.
6. **Format Before Commit**: Always execute `npx prettier --write "**/*.md"` before committing to format all markdown
   files according to repository guidelines.
7. **Squash, Then Push Your Own Branch Freely**: Ensure all commits on your feature branch are squashed into a single
   commit relative to the `main` branch. Pushing **your own** feature branch is allowed autonomously, without waiting
   for instruction: `git push -u origin {branch}`, and `--force-with-lease` when you rewrite history on it.
   - Never push to `main` (or any branch you do not own), never force-push a shared branch, and never push from a `main`
     worktree.
   - Review, Pull Request creation and merge stay with the human maintainer unless the user instructs otherwise.
8. **Report and Document**: Summarize changes cleanly and concisely. Point both the user and successor agents to updated
   files or artifacts.
9. **Zero Synthetic Data for Benchmarking**: Absolutely never use synthetic or mock data to measure efficacy or
   benchmark token reduction. Official evaluations and scorecards must derive exclusively from authentic real data
   streams (live sandbox task executions, genuine wire logs, or real production payloads).

---

## 🌲 Managed Repositories & Git Worktree Structure

This metadata repository hosts bare clones of target codebases with checkout worktrees:

| Repository              | Worktree Directory              | Bare Git Location               | Base Branch   | Feature Branch Command                                            |
| ----------------------- | ------------------------------- | ------------------------------- | ------------- | ----------------------------------------------------------------- |
| **holon-agentic-coder** | `apps/holon-agentic-coder/main` | `apps/holon-agentic-coder/.git` | `origin/main` | `git worktree add --no-track -b {branch} ../{branch} origin/main` |
| **holon-coherence**     | `apps/holon-coherence/main`     | `apps/holon-coherence/.git`     | `origin/main` | `git worktree add --no-track -b {branch} ../{branch} origin/main` |

All code development must take place within the appropriate repository worktree. The metadata repository root is
strictly for coordination, task tracking (`.beans/`), and agent guidance.

> [!IMPORTANT] **One worktree per agent.** Each agent creates and owns its own worktree per project, named after its
> agent or bean id, and works exclusively inside it -- never in `main` (the user's playground) and never in another
> agent's worktree. Run the feature-branch command from the bare repository directory (for example
> `apps/holon-coherence/.git`): `../` resolves relative to that directory, which is what places the checkout at
> `apps/holon-coherence/{branch}`. Each worktree also owns its own virtualenv (`uv sync --group dev`).

---

## 🤖 Subagent Invocation & AGY Runtime

Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:

- **Invocation Tool**: Use the `invoke_subagent` tool to spawn child tasks, isolated review passes, and resolution
  passes.
- **Subagent Type**: Specify `TypeName: "self"` to inherit the full suite of parent capabilities, tools (file viewing,
  editing, command execution), instructions, and credentials. Use `TypeName: "research"` for read-only exploratory
  research.
- **Model Selection**: Set `Model: "inherit"` to inherit the parent agent's active model configuration.
- **Reactive Wakeup (Zero Polling)**: The AGY runtime automatically wakes up the parent agent upon subagent completion
  or message delivery. Never poll or loop on subagent status.
- **Generic Coding Agent Compatibility**: Skill workflows (such as `pr-review-loop`) define generic subagent task
  contracts so any coding agent (Claude Code, Codex, Pi, OpenCodeInterpreter) can spin off subagents using its native
  delegation mechanism (child process, task tool, or isolated session), while retaining explicit AGY invocation
  parameters for seamless native execution.

---

## 📦 The Beans Task System

This repository tracks work items using a lightweight file-based system in the [.beans/](.beans/) folder.

- Each bean represents a single task or user request.
- The metadata config [.beans.yml](.beans.yml) defines naming conventions (prefix `holon-agentic-coder-ref-metadata-`).
- **Strict Sequential Numbering**: Bean IDs MUST follow a strictly sequential 4-digit zero-padded integer format
  (`0001`, `0002`, ..., `0033`, `0034`, `0035`, etc.). Never generate random base36 IDs (e.g. `k4t7`, `1lh8`). To
  determine the next ID, inspect existing files in `.beans/`, find the highest integer ID, increment by 1, and zero-pad
  to 4 digits.
- When picking up a task, update its status inside the task file to `in-progress`.
- Once finished, change the status to `completed` and add a summary of your resolution.
- Valid statuses are fixed by the [beans CLI](https://github.com/hmans/beans) and are `draft`, `todo`, `in-progress`,
  `completed` and `scrapped`. `done` and `in_progress` are **not** valid: the CLI rejects them on create and never
  archives them, because `beans archive` only moves `completed` and `scrapped` beans out of the active directory.

For details on how to create and manage task files, refer to [.agents/workflows.md](.agents/workflows.md).

---

## 📂 The Todo Directory (Temporary Scratchpad)

The `todo/` directory is a local, git-ignored workspace where agents and developers can store temporary scratch files,
draft documents, screenshots/images, and task notes.

- This folder serves as a transient workbench for staging thoughts and intermediate artifacts.
- **Strict Invariant**: None of the files in `todo/` should ever be committed to the repository (enforced via
  `.gitignore`).
