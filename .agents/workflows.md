# Agent Workflows & Task Lifecycle

This document describes the workflow protocols you must follow when executing a task or coordinating code updates.

---

## 🔄 Task Lifecycle (The Bean System)

All work should be tracked under the `.beans/` directory. Each task has a matching text file named:
`.beans/<prefix><id>.yml` or `.beans/<prefix><id>.md` (e.g., `.beans/holon-agentic-coder-ref-metadata-0001.yml`).

### 1. Task Acquisition

- Look at the `.beans/` folder. Select a task with status `todo`.
- If no task matches the user's request, create a new bean file using the next available ID.
- Update the status field of the task file to `in_progress`.

### 2. Implementation Cycle

- **Plan**: Create a step-by-step plan. If the task is complex, document it in an artifact.
- **Implement**: Make changes to the code using the files and tools as prescribed in [rules.md](rules.md).
- **Test**: Run all relevant tests. Check for compilation errors or linters.
- **Document**: Add notes inside the task file explaining how the task was resolved.

### 3. Task Completion

- Change the status field to `done`.
- Format all markdown files by running `npx prettier --write "**/*.md"`.
- Commit the changes on the current active branch (**Do NOT create a new branch unless explicitly told**).
- Squash all branch commits relative to the `main` branch into a single commit.
- **Do NOT push to the remote repository (`origin`) unless explicitly instructed by the user.**

---

## 🌿 Git & Commit Guidelines

To maintain clean repository history, follow this Git workflow:

1. **Branching (Do NOT create branches autonomously)**:
   - **Never create a new branch unless explicitly instructed by the user.**
   - Work on the active branch that is currently checked out in the workspace.
   - If the user explicitly requests you to create a new branch, use the convention:
     `git checkout -b <type>/<bean-id>-<short-description>` (e.g., `feat/0001-add-agent-rules`).
2. **Formatting (Mandatory)**:
   - Always run `npx prettier --write "**/*.md"` to format markdown files before creating any commits.
3. **Commits**:
   - Write semantic commit messages. Example:
     ```text
     feat(agents): add core agent instructions and rules

     - Added .agents/instructions.md
     - Added .agents/rules.md
     - Configured landing page entrypoint in AGENTS.md
     ```
   - Avoid generic commit messages like "update files" or "fix".
4. **Squashing (Mandatory)**:
   - Before pushing your feature branch to the remote repository, you **MUST squash all commits** on your branch
     relative to the `main` branch into a **single commit**.
   - Your feature branch should only ever contain exactly **one commit** differing from `main`.
   - To perform the squash, execute:
     ```bash
     git reset $(git merge-base main HEAD)
     git add -A
     git commit -m "your-semantic-commit-message"
     ```
5. **Pull Requests & Pushing (No Autonomous Pushing)**:
   - **Never push to the remote repository (`origin`) unless explicitly instructed by the user.**
   - Once explicitly instructed to push, execute: `git push origin <branch-name> --force`.
   - **Do NOT push directly to `main` under any circumstances.**
   - The human repository maintainer will review the changes, raise the Pull Request, and merge it into `main`.
