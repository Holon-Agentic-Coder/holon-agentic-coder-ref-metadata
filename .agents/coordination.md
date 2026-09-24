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

- **Context Isolation**: When a task requires many search, review, and file-reading steps that would otherwise pollute
  the main context window (e.g. PR reviews in `pr-review-loop`).
- **Specialization**: Spawning a specialized agent (e.g. "PR Reviewer", "Security Auditor", "Lint Fixer") to execute a
  narrow, focused task.
- **Parallel Work**: Running independent tasks concurrently (e.g. 3-agent ensemble review).

### 2. Generic Subagent Protocol (Any Coding Agent)

For any coding agent runner operating in this workspace (Antigravity/AGY, Claude Code, Codex, Pi, OpenCodeInterpreter):

- **Role**: Assign a clear 2-5 word job description (e.g. `PR Reviewer (Iteration 1)`).
- **Self-Contained Actionable Prompt**: Provide all necessary context, target branch names, repository paths under
  `apps/` (`apps/holon-agentic-coder` or `apps/holon-coherence`), explicit input parameters, and output format.
- **Target Artifacts**: Direct child agents to persist structured output to `.subagent/` (git ignored) or task
  artifacts.
- **Context Isolation**: Always spin off each iteration in a clean, fresh child context to prevent prompt degradation.

### 3. Antigravity (AGY) Runtime Instructions

When executing within the **Antigravity (AGY)** environment:

- **Invocation Tool**: Use `invoke_subagent` to spawn child tasks.
- **Subagent Type**:
  - `TypeName: "self"`: Use for coding, fixing, reviewing, and testing tasks that require full tool access (file
    reading, file writing, terminal commands, web search). It inherits the parent agent's configuration and system
    prompts.
  - `TypeName: "research"`: Use for read-only codebase exploration and reference lookups.
  - `define_subagent`: Use when custom tool groupings or specialized system prompts are strictly required.
- **Model Configuration**: Always set `Model: "inherit"` to maintain model parity across parent and child sessions
  unless explicitly requested otherwise.
- **Reactive Wakeup (Zero Polling)**: AGY resumes parent execution automatically upon child message arrival or task
  completion. **Never poll, sleep, or loop on task status.**

### 4. Monitoring & Completion

- Review the subagent's report upon reactive resumption.
- In multi-turn workflows, inspect output artifacts (e.g. `.subagent/dry_run_review_iter_*.md`) and verify commits
  before proceeding to subsequent phases.
