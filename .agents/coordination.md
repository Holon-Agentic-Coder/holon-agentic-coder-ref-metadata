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
- **Parallel Work**: Running independent tasks concurrently (e.g. 3-agent ensemble review), subject to the dispatch
  concurrency policy in section 4 -- on a local model runtime this collapses to serial dispatch.

### 2. Generic Subagent Protocol (Any Coding Agent)

For any coding agent runner operating in this workspace (Antigravity/AGY, Claude Code, Codex, Pi, OpenCodeInterpreter):

- **Role**: Assign a clear 2-5 word job description (e.g. `PR Reviewer (Iteration 1)`).
- **Self-Contained Actionable Prompt**: Provide all necessary context, target branch names, repository paths under
  `apps/` (`apps/holon-agentic-coder` or `apps/holon-coherence`), explicit input parameters, and output format.
- **Target Artifacts**: Direct child agents to persist structured output to `.subagent/` (git ignored) or task
  artifacts.
- **Context Isolation**: Always spin off each iteration in a clean, fresh child context to prevent prompt degradation.
- **Worktree Ownership**: A delegated agent that mutates files must be given its own worktree and branch (named after
  that agent or its bean) and must work exclusively inside it. Never delegate two writers onto the same worktree, and
  never delegate work into a `main` worktree. Read-only reviewers and searchers need no worktree of their own.

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

### 4. Dispatch Concurrency: Local vs Hosted Runtimes

Fanout is a property of the _work_, but whether it is safe is a property of the _runtime_. Every child inherits the
parent's model, so when that model is served locally all children contend for one inference backend on the operator's
own machine: requests queue or thrash, turns get dropped mid-generation (the child dies emitting reasoning with no
answer and no tool call), and a constrained host can be pushed into swap or crash outright.

**Classify the runtime before dispatching any fanout:**

| Runtime     | Detection                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local**   | The model is served on the operator's machine. In Pi, check `$PI_PROVIDER` / `$PI_MODEL` for a local server (`vmlx`, `ollama`, `llama.cpp` / `lmstudio` / `mlx`, or any provider whose base URL is `localhost` / `127.0.0.1`). For other agents, the configured model endpoint resolves to localhost, or the operator has stated the model is local. |
| **Hosted**  | The model is served by a remote API (Anthropic, OpenAI, Gemini, Antigravity, and similar).                                                                                                                                                                                                                                                           |
| **Unknown** | Ask the operator once, then honour that answer for the rest of the session. Never assume hosted.                                                                                                                                                                                                                                                     |

The rule:

- **Hosted runtime** -- dispatch independent children concurrently (the default in `pr-reviewer` and `pr-review-loop`).
- **Local runtime** -- dispatch LLM-inference children **serially**: launch one child, wait for it to finish, then
  launch the next. Concurrency for LLM work is capped at 1. Serialising changes **only the launch schedule**:
  - Each pass still runs in its **own fresh child context**, with its own prompt, its own report file and its own vote.
    Reusing one child for "all three" votes is not a serial ensemble; it is a single review and can never produce a 3/3
    consensus verdict.
  - Children must not be handed each other's findings. Reviewer 2 and 3 are written blind to reviewer 1 exactly as in a
    parallel ensemble; the ordering is invisible to them.
  - The per-PR artifacts, trailer blocks, coordination ledger and resume state in `.subagent/` are unchanged.
  - Non-LLM work (builds, `uv sync`, test runs, image builds, shell verification) is not bound by this cap and may still
    run concurrently.
- **Attrition is expected on a local runtime, and it is retried serially.** When a child dies mid-turn (timeout, or the
  "reasoning but no answer" abort), relaunch that single pass on its own -- never "run another in parallel while the
  first is still up", which is what turns one flaky pass into a wedged machine. See principle 9 of
  [`pr-review-loop`](skills/pr_review_loop/SKILL.md).

### 5. Monitoring & Completion

- Review the subagent's report upon reactive resumption.
- In multi-turn workflows, inspect output artifacts (e.g. `.subagent/<repo>_pr<N>_dry_run_review_iter_*.md`, namespaced
  per the `pr-review-loop` skill's artifact convention) and verify commits before proceeding to subsequent phases.
