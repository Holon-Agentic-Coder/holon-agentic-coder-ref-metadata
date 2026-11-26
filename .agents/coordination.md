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
  concurrency policy in section 5 -- on a local model runtime this collapses to serial dispatch.

### 2. Review Loop Delegation

When `/pr-review-loop <PR_URL_OR_NUMBER>` is invoked, the harness uses a **2-tier subagent delegation architecture**
(Bean 0212; see
[`pr-review-loop` Step 0](skills/pr_review_loop/SKILL.md#step-0-entrypoint-delegation--spawn-the-background-loop-orchestrator-subagent))
so that long-running multi-iteration review loops never hijack the user's primary conversation thread:

- **Tier 1 (Main Interactive Agent -> Background Loop Orchestrator)**: The main interactive agent MUST NOT run the
  review loop inline. Instead, it immediately spawns 1 background **PR Review Loop Orchestrator** subagent via
  `invoke_subagent` (`TypeName: "self"`, `Model: "inherit"`, `Role: "#<N> - review loop orchestrator"`) and returns
  control to the user immediately. Multiple PR review loops across different PRs can run concurrently in isolated Tier 1
  orchestrator subagents without blocking the main agent.
- **Tier 2 (`PR Review Loop Orchestrator` Subagent -> Per-Pass Reviewer & Resolver Subagents)**: The background
  `PR Review Loop Orchestrator` subagent owns the entire loop lifecycle across all iterations (up to
  `max_iterations: 25`). Per iteration, it spawns the isolated dry-run reviewer, the 3 parallel `pr-reviewer` ensemble
  subagents (serial on local runtimes per section 5), and 1 `pr-review-resolver` subagent when `CHANGES_REQUESTED`,
  tracks state in `.subagent/<repo>_pr<N>_state.json`, verifies CI checks, posts the final consensus review to GitHub
  upon `APPROVED`, runs Stage 5 `holon calibrate` for Holon flow PRs, and notifies the Tier 1 parent agent via
  `send_message` **only once** on terminal completion (`APPROVED` + calibrated) or a terminal stop
  (`MAX_ITERATIONS_REACHED` / `DIVERGING`).
- **Re-Entrancy Guard**: If the executing agent is already the spawned `PR Review Loop Orchestrator` subagent (or a
  background flow orchestrator subagent executing Stage 4), it proceeds directly to Step 1 of `pr-review-loop` without
  spawning a nested loop orchestrator.

### 3. Holon Flow Delegation (Background Flow Subagent)

Executing the 5-stage Holon flow (`holon flow <intent.json>`) runs containerised agents through Intent, Plan, Execute,
Stage 4 Review Loop, and Stage 5 Calibration, requiring between 15 minutes and several hours. To ensure the main
interactive session remains responsive:

- **Interactive Agent Delegation**: The main interactive agent MUST NOT execute `holon flow` inline. Instead, it
  immediately spawns 1 background **Holon Flow Subagent** via `invoke_subagent` (`TypeName: "self"`,
  `Role: "bean <id> - holon flow <slug>"`, `Model: "inherit"`) and returns control to the user immediately (see
  [holon-flow Step 0](skills/holon_flow/SKILL.md#step-0-entrypoint-delegation--spawn-the-background-flow-subagent)).
- **Subagent Flow Ownership**: The background subagent executes `holon flow` directly, watches checkpoints
  (`.holon/flow/checkpoint-<slug>.json`), applies the automatic model fallback ladder on quota/session exhaustion,
  verifies PR creation and Stage 5 calibration inclusion in the PR diff, and notifies the parent agent via
  `send_message` **only once** upon terminal completion or an unresolvable blocker.
- **Re-Entrancy Guard**: If the executing agent is already the spawned `Holon Flow Subagent`, it proceeds directly to
  flow execution without spawning another nested subagent.
- **8-Flow Concurrency Cap & Merge Backfill (maintainer, 2026-11-24; 8 since 2026-11-27)**: On hosted runtimes, up to
  **8 concurrent `holon-flow` background subagents** may run at once, each in its own dedicated `flow-<slug>` worktree
  and honouring dependencies, solo-sweep rules, and disjoint touch sets. Once a target-repo PR merges, backfill open
  slots up to 8 by launching the next highest-priority ready bean via `holon-flow`.
  - **Slots must always be doing work (maintainer, 2026-11-26)**: only flows that are executing, reviewing or
    calibrating count toward the 4; check this on every progress report and after every merge.
  - **Park blocked flows**: a flow refused at Stage 3 admission on a touch-set overlap, or otherwise waiting on another
    flow's PR, does not hold a slot. Stop only that flow's own wrapper/poll loop, keep its worktree, branches and
    checkpoint, note on its bean
    `parked <date>: blocked by <PR/flow> on <files>; resume from checkpoint when <condition>`, and end its subagent.
  - **Backfill at once** with the next highest-priority ready bean whose touch set is disjoint from every live and
    parked flow.
  - **Resume from checkpoint**: once the blocker merges or releases the files, resume the parked flow with
    `--checkpoint` (never a fresh launch, which re-runs intent and plan and leaves duplicate `I-*` branches). Resuming
    takes the next free slot ahead of new beans.
  - **Intent goal carries the invariant (maintainer, 2026-11-27)**: every intent written for a backfilled or new flow
    includes this sentence in its `goal`: "Code is self-explaining: no docstrings and no comments except '# why:'
    comments that record a reason the code cannot show." Before reporting a PR ready, scan its diff for docstrings and
    non-`# why:` comments.

### 4. Generic Subagent Protocol (Any Coding Agent)

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

### 5. Antigravity (AGY) Runtime Instructions

When executing within the **Antigravity (AGY)** environment:

- **Invocation Tool**: Use `invoke_subagent` to spawn child tasks.
- **Subagent Type**:
  - `TypeName: "self"`: Use for coding, fixing, reviewing, and testing tasks that require full tool access (file
    reading, file writing, terminal commands, web search). It inherits the parent agent's configuration and system
    prompts.
  - `TypeName: "research"`: Use for read-only codebase exploration and reference lookups.
  - `define_subagent`: Use when custom tool groupings or specialized system prompts are strictly required.
- **Model Configuration & Credit Fallback**: Default to `Model: "inherit"` to maintain model parity across parent and
  child sessions. If credit, quota, or session allowance runs out on the higher-level model (for either **Claude** or
  **Antigravity**), automatically fall back to the next lower tier that has available credit (`Model: "inherit"` /
  `"pro"` $\rightarrow$ `"flash"` $\rightarrow$ `"flash_lite"` in AGY `invoke_subagent`; `claude-opus-5-5` $\rightarrow$
  `claude-sonnet-4-6` $\rightarrow$ `claude-haiku-4-5` in `claude-agent`; `gemini-4-neon` $\rightarrow$ `gemini-4-argon`
  $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash` in `antigravity-agent`; never switch `--agent`
  across runners on your own: if an account-wide session limit exhausts the runner's ladder, stay on it and ask the
  maintainer before switching) and continue the in-progress flow or review loop from its current stage/iteration without
  losing completed work.
- **Reactive Wakeup (Zero Polling)**: AGY resumes parent execution automatically upon child message arrival or task
  completion. **Never poll, sleep, or loop on task status.**

### 6. Dispatch Concurrency: Local vs Hosted Runtimes

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

- **Hosted runtime** -- dispatch independent children concurrently (the default in `pr-reviewer` and `pr-review-loop`);
  for target-repo `holon-flow` executions, up to **8 concurrent background flow subagents** are permitted (with
  automatic highest-priority bean backfill upon PR merge).
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

### 6. Monitoring & Completion

- Review the subagent's report upon reactive resumption.
- In multi-turn workflows, inspect output artifacts (e.g. `.subagent/<repo>_pr<N>_dry_run_review_iter_*.md`, namespaced
  per the `pr-review-loop` skill's artifact convention) and verify commits before proceeding to subsequent phases.

### 7. Skill Subagents and Delegation (maintainer rules)

- **Harness operations run through their skills in subagents, never inline** (maintainer, 2026-11-23): flows
  (`holon-flow`), conflict resolution (`resolve-conflict`), review loops and calibration (`pr-review-loop`). A quick
  manual check does not excuse skipping the skill. When a resolve-conflict subagent escalates a code conflict, spawn a
  new one a tier up with the decision in its prompt; the main session only decides and delegates.
- **Name every subagent**: description `#<PR> - <what>` (or `bean <id> - <what>` before a PR exists), and set its name
  field too (`pr<PR>-<what>` or `bean<id>-<what>`, letters, digits, `_` and `-` only).
- **Keep the main thread for coordination** (maintainer, 2026-11-24): diagnosing failures, measuring, reading across
  several files and editing or testing harness code go to subagents on the lowest tier that fits. Inline only: status
  checks, briefing subagents, single small edits and replies.

### 8. Coordinator failure ledger

`.agents/ledger/coordinator-failures.jsonl` records the coordinator's own mistakes (maintainer, 2026-11-27); the target
repositories' ledgers stay for flows and never reference harness paths. It is append-only, one JSON object per line;
corrections are new lines with `supersedes`. Fields: `id` (`CF-0001`...), `created_at` (ISO UTC), `session_date`,
`category` (brief, readiness-check, overlap-scheduling, intent-scope, measurement, conflict-handling, bookkeeping,
verification), `failure`, `my_part`, `cost`, `rule`, `refs`. Append an entry for every halt, park, wasted run, false
readiness or wrong brief before moving on. Check every brief, readiness check and launch against its rules. Validate
with `uv run python .agents/scripts/check_failure_ledger.py`.

After every subagent returns, run `uv run python .agents/scripts/check_main_worktrees.py`; a non-zero exit is a
coordinator failure to record in the ledger and report at once. The git-safety rules are enforced by a hook and a PATH
wrapper (see [worktrees-and-git.md](worktrees-and-git.md#enforcement-not-briefs)).
