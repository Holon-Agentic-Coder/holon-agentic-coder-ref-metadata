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
5. **No Autonomous Branches**: Never create a new branch unless explicitly instructed by the user. Work on the active
   branch that is currently checked out:
   - For `apps/holon-agentic-coder/`, all development and feature work must be based off the `origin/main` branch.
   - For `apps/holon-coherence/`, all development and feature work must be based off the `origin/main` branch.
6. **Format Before Commit**: Always execute `npx prettier --write "**/*.md"` before committing to format all markdown
   files according to repository guidelines.
7. **Squash and Push (No Autonomous Pushing)**: Ensure all commits on your feature branch are squashed into a single
   commit relative to the `main` branch. **Never push to the remote repository (`origin`) unless explicitly instructed
   by the user.** Do NOT push directly to `main`.
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
- The metadata config [.beans.yml](.beans.yml) defines naming conventions (e.g. prefix
  `holon-agentic-coder-ref-metadata-`).
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
