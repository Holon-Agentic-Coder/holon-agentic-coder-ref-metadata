---
# holon-agentic-coder-ref-metadata-0212
title: "pr-review-loop delegates loop orchestration to a background subagent so the main agent stays free"
status: completed
type: task
priority: high
tags:
  - harness
  - pr-review-loop
  - subagents
  - coordination
created_at: 2026-10-30T01:37:45Z
updated_at: 2026-10-30T01:55:00Z
---

## Problem

When a user invokes `/pr-review-loop <pr_url_or_number>` in the main interactive session,
`.agents/skills/pr_review_loop/SKILL.md` currently instructs the receiving agent itself to execute
`Step 2: Main Loop Execution` across all iterations (up to `max_iterations: 25`).

Because each iteration wakes the orchestrator multiple times (Phase A dry-run reviewer, Phase B 3-agent ensemble
reviewers, Phase C resolver), running the loop orchestrator inside the main interactive agent hijacks the user's primary
conversation thread for the duration of the loop and prevents concurrent interactive work across other PRs or tasks.

## Scope

1. **Update `.agents/skills/pr_review_loop/SKILL.md`**:
   - Add a **Top-Level Orchestrator Delegation** rule in **Architecture & Principles** and **Step 0: Entrypoint
     Delegation — Spawn the Background Loop Orchestrator Subagent** before Step 1:
     - **When invoked on the main interactive agent**: The main agent MUST NOT execute the `Step 2` iteration loop
       directly in its own conversation turn loop. Instead, after parsing `<pr_url_or_number>` and `<max_iterations>`,
       it immediately spawns a dedicated background orchestrator subagent (`invoke_subagent` with `TypeName: "self"`,
       `Model: "inherit"`, `Role: "PR Review Loop Orchestrator (<repo> PR #<N>)"`) to run the entire loop autonomously,
       and immediately returns control to the user.
     - **Re-entrancy guard**: If the executing agent is _already_ the spawned `PR Review Loop Orchestrator` subagent (or
       a background flow orchestrator subagent executing Stage 4), it proceeds directly to Step 1 without spawning
       another nested loop orchestrator.
     - **When running inside the `PR Review Loop Orchestrator (<repo> PR #<N>)` subagent**: It owns the entire loop
       lifecycle (Steps 1–3: state tracking in `.subagent/`, spawning the dry-run and 3 `pr-reviewer` ensemble
       subagents, synthesising the consensus report, spawning `pr-review-resolver` when `CHANGES_REQUESTED`, verifying
       CI checks, posting the final consensus review to GitHub upon `APPROVED`, and running Stage 5 `holon calibrate`
       for Holon flow PRs) and notifies the main agent **only once** on terminal completion (`APPROVED` + calibrated) or
       an unresolvable blocker (`MAX_ITERATIONS_REACHED` / `DIVERGING`).
2. **Update `.agents/coordination.md`**:
   - Document the 2-tier subagent delegation architecture under `### 2. Review Loop Delegation`
     (`Main Interactive Agent -> PR Review Loop Orchestrator Subagent -> Per-Pass Reviewer / Resolver Child Subagents`)
     so multiple PR review loops can run concurrently in the background while the main agent remains responsive to the
     user.
3. **Add unit tests in `tests/test_pr_review_loop_convergence.py`**:
   - Assert that `.agents/skills/pr_review_loop/SKILL.md` defines Step 0 orchestrator subagent delegation, the
     re-entrancy guard, the `invoke_subagent` contract, and Principle 12 convergence rules, and that
     `.agents/coordination.md` documents the 2-tier review loop delegation hierarchy.

## Acceptance Criteria

- Invoking `/pr-review-loop <pr>` in the main chat spawns a single background
  `PR Review Loop Orchestrator (<repo> PR #<N>)` subagent and immediately returns control to the user.
- Multiple `/pr-review-loop` invocations across different PRs run concurrently in isolated subagents without blocking
  the main agent or colliding on `.subagent/<repo>_pr<N>_*` artifacts or worktrees.
- `npx prettier --check "**/*.md"` and `node .agents/scripts/validate-links.js` pass.

## Notes

- Target repository: `holon-agentic-coder-ref-metadata` (harness control plane).
- Related: Bean 0170 (`pr-review-loop` incremental convergence), Bean 0063 (durable `.subagent/<repo>_pr<N>_state.json`
  handoff).

## Resolution

Completed in `holon-agentic-coder-ref-metadata`:

1. Updated `.agents/skills/pr_review_loop/SKILL.md` with Principle 13 (Background Orchestrator Delegation) and **Step 0:
   Entrypoint Delegation — Spawn the Background Loop Orchestrator Subagent**, including the explicit re-entrancy guard,
   the `invoke_subagent` (`TypeName: "self"`, `Model: "inherit"`,
   `Role: "PR Review Loop Orchestrator (<repo> PR #<N>)"`) contract, and terminal-only parent notification via
   `send_message`.
2. Updated `.agents/coordination.md` with a dedicated `### 2. Review Loop Delegation` section documenting the 2-tier
   subagent delegation architecture (Tier 1: Main Interactive Agent -> `PR Review Loop Orchestrator` subagent; Tier 2:
   `PR Review Loop Orchestrator` -> per-iteration `pr-reviewer` ensemble and `pr-review-resolver` child subagents).
3. Added `tests/test_pr_review_loop_convergence.py` verifying Step 0 orchestrator subagent delegation, re-entrancy
   guard, `invoke_subagent` contract, Principle 12 convergence rules, and `.agents/coordination.md` 2-tier review loop
   delegation documentation.
