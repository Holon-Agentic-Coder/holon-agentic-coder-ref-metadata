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
- Commit the changes and push to the remote repository.

---

## 🌿 Git & Commit Guidelines

To maintain clean repository history, follow this Git workflow:

1. **Branching**:
    - Create a branch for your task: `git checkout -b <type>/<bean-id>-<short-description>` (e.g.,
      `feat/0001-add-agent-rules`).
2. **Commits**:
    - Write semantic commit messages. Example:
      ```text
      feat(agents): add core agent instructions and rules
 
      - Added .agents/instructions.md
      - Added .agents/rules.md
      - Configured landing page entrypoint in agents.md
      ```
    - Avoid generic commit messages like "update files" or "fix".
3. **Pull Requests**:
    - Push your branch to the remote: `git push origin <branch-name>`.
    - Provide a description summarizing the changes and referencing the related bean ID.
