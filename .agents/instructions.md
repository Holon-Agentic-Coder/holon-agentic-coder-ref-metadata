# General Agent Instructions

As an autonomous AI agent in the Holon Agentic Coder ecosystem, you are responsible for maintaining high code quality,
system safety, and clean documentation. Follow these core guidelines in every session.

---

## 🧠 Core Agent Mindset

1. **Be Rigorous**: Do not make assumptions about the codebase structure or behavior. Always read the code and test
   suites before making changes.
2. **Be Minimalist**: Write clean, readable, and well-targeted code. Avoid introducing unnecessary dependencies or
   over-engineering solutions.
3. **Be Communicative**: Inform the user (or parent agent) of your plan before executing complex steps. Use artifacts to
   outline detailed multi-step plans.
4. **Preserve Context**: Maintain original documentation, comments, and structure unless explicitly tasked with changing
   them. Do not delete comments or rename files without justification.
5. **Avoid Absolute Paths**: Never use absolute file paths in code references, comments, tasks, or documentation. Always
   use paths relative to the project root (e.g. `.agents/instructions.md`) to ensure portability across developer
   workspaces.

---

## 🛠 Operational Guidelines

### 1. Research and Discovery

- Before modifying a file, read its entire contents (or at least the surrounding context up to 800 lines) using the file
  viewer tool.
- Use grep searches to locate all occurrences of a variable, class, or function you plan to change to avoid breaking
  downstream references.

### 2. Edits and Modifications

- Prefer making precise, targeted edits using specific search-and-replace tools rather than rewriting entire files.
- Ensure that the lines you are replacing are unique and match exactly, including leading whitespace and indentation.
- Always lint and/or compile files immediately after editing to catch syntax or logical errors early.

### 3. Verification and Safety

- Never assume your edits work. Always execute tests or verification scripts to prove correctness.
- If no test suite exists, write unit tests directly within the codebase to verify your changes, rather than relying on
  untracked external scratch files.
- Check git status and diff output to ensure only the intended changes have been made.

### 4. Workspace Structure (`apps/`)

- Target application codebases reside under the `apps/` directory (`apps/holon-agentic-coder` and
  `apps/holon-coherence`).
- All code modifications must occur within the appropriate repository worktree (e.g. `apps/holon-agentic-coder/main` or
  feature branch worktree).
- The repository root is strictly for control plane coordination, task tracking (`.beans/`), and agent guidance.

### 5. Subagent Delegation (AGY & Generic Coding Agents)

- Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:
  - Use `invoke_subagent` with `TypeName: "self"` so child agents inherit full tools (view, edit, bash execution) and
    environment settings. Use `TypeName: "research"` for read-only research.
  - Set `Model: "inherit"` to match the parent agent's configuration.
  - Never poll or sleep in a loop; AGY wakes the parent agent automatically when child tasks finish.
- Generic coding agents (such as Claude Code, Codex, Pi, OpenCodeInterpreter) can execute child tasks using their native
  subagent or child process delegation mechanisms following the same prompt contracts.
