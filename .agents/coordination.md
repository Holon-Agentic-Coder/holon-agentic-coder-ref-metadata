# Multi-Agent Coordination Protocol

This document outlines protocols for spawning, instructing, and coordinating with subagents and peers to execute complex
or concurrent workflows.

---

## 👥 Coordination & Roles

When multiple agents run in the same workspace, they must avoid conflicting changes:

1. **Task Locking**: Before starting a task, assign the task file in `.beans/` to your current `conversation_id` or
   unique agent name. Do not modify files related to tasks assigned to other active agents.
2. **Communication**: Use structured messages to pass state or report completion to other agents.

---

## 🤖 Subagent Delegation

Spawning subagents helps isolate execution contexts (e.g. running unit tests, scanning dependency files, or searching
external docs). Follow these rules:

### 1. When to Spawn a Subagent

- **Context Isolation**: When a task requires many search and file-reading steps that would otherwise fill your main
  context window.
- **Specialization**: Spawning a specialized agent (e.g. "Security Auditor", "Lint fixer") to run a single, narrow task.
- **Parallel Work**: Running independent tasks concurrently.

### 2. Instructing a Subagent

When using `invoke_subagent`, provide:

- **Role**: A clear 2-5 word job title (e.g. "Typescript Code Reviewer").
- **Actionable Prompt**: Be explicit about the inputs, expected outputs, constraints, and the format of the final
  report.
- **Reference Material**: Point the subagent to the target files using workspace-relative paths and line numbers if
  possible.

### 3. Monitoring & Completion

- Do not poll subagents continuously. Allow the platform to wake you up when a subagent sends a message.
- Upon subagent completion, review their report, merge any files/work if applicable, and terminate the subagent.
