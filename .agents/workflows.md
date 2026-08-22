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

## 📥 Reference Repository Setup (Git Worktree)

To work with the primary codebase repository
([holon-agentic-coder-ref](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref)) within this metadata
repository (at `holon-agentic-coder-ref/`), you must clone it as a Git bare repository and check out branches as Git
worktrees. This allows running multiple tasks on different branches simultaneously under a clean directory structure.

1. **Clone the repository as bare** into the hidden `.git` folder of the `holon-agentic-coder-ref` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git holon-agentic-coder-ref/.git
   ```
2. **Navigate into the git database directory**:
   ```bash
   cd holon-agentic-coder-ref/.git
   ```
3. **Set up worktrees for your branches**:
   - **For the `develop` branch** (checked out to `holon-agentic-coder-ref/develop`): This is the baseline active
     development branch tracking `origin/develop`. **Never develop or modify code directly on `develop`.** All feature
     changes must be made either in a separate dedicated worktree or as part of the Holon flow.
     ```bash
     git worktree add ../develop develop
     ```
   - **For the `main` branch** (checked out to `holon-agentic-coder-ref/main`): This branch is from the upstream
     repository and only contains documentation and specifications.
     ```bash
     git worktree add ../main main
     ```
   - **For a specific feature branch `{branch_name}`** (checked out to `holon-agentic-coder-ref/{branch_name}`): All
     development, manual fixes, and feature changes must be created in their own dedicated worktree off `origin/develop`
     with `--no-track` (so the branch does not track `origin/develop` and instead tracks its own remote branch
     `origin/{branch_name}` when pushed):
     ```bash
     git worktree add --no-track -b {branch_name} ../{branch_name} origin/develop
     ```

---

## 🌿 Git & Commit Guidelines

To maintain clean repository history, follow this Git workflow:

1. **Branching & Worktree Isolation**:
   - **Never develop or make code changes directly on the `develop` worktree.**
   - For all code changes in `holon-agentic-coder-ref/`, work must either: a) happen in a dedicated Git worktree (e.g.
     `holon-agentic-coder-ref/feat-<name>` branched off `origin/develop`), or b) execute autonomously through the Holon
     flow (`I-...` Intent -> Plan -> Execution branches).
   - In this metadata repository (`holon-agentic-coder-ref-metadata`), work on the active checked-out branch.
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
     relative to the target branch into a **single commit** (e.g., relative to `main` in this metadata repository, or
     `develop` in the reference repository).
   - Your feature branch should only ever contain exactly **one commit** differing from the target branch.
   - To perform the squash, execute:

     ```bash
     # For the metadata repository:
     git reset $(git merge-base main HEAD)

     # For the reference repository:
     git reset $(git merge-base develop HEAD)

     git add -A
     git commit -m "your-semantic-commit-message"
     ```

5. **Pull Requests & Pushing (No Autonomous Pushing)**:
   - **Never push to the remote repository (`origin`) unless explicitly instructed by the user.**
   - Once explicitly instructed to push, execute: `git push origin <branch-name> --force`.
   - **Do NOT push directly to `main` or `develop` under any circumstances.**
   - The human repository maintainer will review the changes, raise the Pull Request, and merge it.
