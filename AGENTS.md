# Agent Landing Page & Entrypoint

> [!NOTE] **Bootstrapping Harness Intent** This repository is a temporary control plane and metadata store. It will only
> be used until the bootstrap process for
> [holon-agentic-coder-ref](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref) is fully completed. Until
> that repository is fully bootstrapped, it does not possess enough autonomous power to develop or maintain itself. This
> repository serves as the external harness to bridge that gap.

Welcome, Agent. This document is your starting point for operating within this workspace. Read this document in its
entirety before performing any operations or modifying any code.

---

## 🎯 Quick Navigation

- [README.md](README.md) - Repository architecture and general overview.
- [.agents/instructions.md](.agents/instructions.md) - General operating principles and behavioral guidelines.
- [.agents/rules.md](.agents/rules.md) - Coding standards, file handling, and sandbox constraints.
- [.agents/workflows.md](.agents/workflows.md) - Task execution cycle, git guidelines, and PR procedures.
- [.agents/coordination.md](.agents/coordination.md) - Delegation, subagent communication, and peer coordination
  protocols.
- [.agents/skills/](.agents/skills/) - Project-specific agent skills and capability guidelines.
- [todo/](todo/) - Temporary scratchpad directory for local agent files, documents, and notes (git ignored).

---

## 🚀 Incoming Agent Checklist

When you are spawned or begin a new session, follow these steps sequentially:

1. **Verify Your Environment**: Check the current working directory, workspace structure, and locate the `.beans`
   configuration. If the reference repository is not set up, follow the checkout instructions in
   [README.md](README.md#-reference-repository-setup-git-worktree) to clone the bare repository and configure worktrees.
2. **Review the Tasks**: List the tasks in the [.beans/](.beans/) directory to determine your current assignment or log
   a new task if none exists.
3. **Internalize Constraints**: Load [.agents/rules.md](.agents/rules.md) to understand linting rules, language choices,
   and test requirements.
4. **Execute Tasks Systematically**: Follow the lifecycle specified in [.agents/workflows.md](.agents/workflows.md) to
   transition tasks from `todo` to `in-progress` and finally `done`.
5. **No Autonomous Branches**: Never create a new branch unless explicitly instructed by the user. Work on the active
   branch that is currently checked out. For the reference repository `holon-agentic-coder-ref/`, all development and
   feature work must be based off the `origin/develop` branch.
6. **Format Before Commit**: Always execute `npx prettier --write "**/*.md"` before committing to format all markdown
   files according to repository guidelines.
7. **Squash and Push (No Autonomous Pushing)**: Ensure all commits on your feature branch are squashed into a single
   commit relative to the `main` branch. **Never push to the remote repository (`origin`) unless explicitly instructed
   by the user.** Do NOT push directly to `main`.
8. **Report and Document**: Summarize changes cleanly and concisely. Point both the user and successor agents to updated
   files or artifacts.

---

## 📦 The Beans Task System

This repository tracks work items using a lightweight file-based system in the [.beans/](.beans/) folder.

- Each bean represents a single task or user request.
- The metadata config [.beans.yml](.beans.yml) defines naming conventions (e.g. prefix
  `holon-agentic-coder-ref-metadata-`).
- When picking up a task, update its status inside the task file to `in_progress`.
- Once completed, change the status to `done` and add a summary of your resolution.

For details on how to create and manage task files, refer to [.agents/workflows.md](.agents/workflows.md).

---

## 📂 The Todo Directory (Temporary Scratchpad)

The `todo/` directory is a local, git-ignored workspace where agents and developers can store temporary scratch files,
draft documents, screenshots/images, and task notes.

- This folder serves as a transient workbench for staging thoughts and intermediate artifacts.
- **Strict Invariant**: None of the files in `todo/` should ever be committed to the repository (enforced via
  `.gitignore`).
