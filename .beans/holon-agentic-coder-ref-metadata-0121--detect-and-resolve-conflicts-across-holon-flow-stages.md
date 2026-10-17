---
# holon-agentic-coder-ref-metadata-0121
title: "Detect and resolve conflicts proactively across all Holon flow stages"
status: todo
type: feature
priority: high
tags:
  - holon-flow
  - git
  - concurrency
  - rebase
  - conflict-resolution
created_at: 2026-10-18T00:31:00Z
updated_at: 2026-10-18T00:31:00Z
---

## Summary

Implement proactive conflict detection and resolution across all 5 stages of the Holon flow
(`intent -> plan -> execute -> pr review loop -> calibration`). Because parallel flow runs and concurrent developer PRs
merge to `main` at unpredictable times, upstream branches can diverge at any point in a flow run. Each stage must detect
divergence and merge/rebase conflicts early, resolve them safely (or fail fast with clear diagnostic reporting), and
prevent broken PR merges.

## Context & Problem Statement

In a multi-agent or concurrent workflow environment:

1. Multiple Holon flows execute concurrently against base branches (`main`).
2. An intent branch created at $T_0$ may be cleanly branched off `main`, but by the time `holon plan` runs at $T_1$,
   another PR has merged to `main`.
3. By the time `holon execute` completes at $T_2$, further commits have landed on `main`.
4. During the autonomous PR review loop (Stage 4), subsequent PR merges to `main` can introduce merge conflicts on
   GitHub, making the PR unmergeable.
5. In Stage 5 (Calibration), merging the calibration commit back into the PR branch or reconciling against updated base
   history can fail if conflict checks were not performed.

Without proactive conflict detection and automated resolution mechanisms at each stage boundary:

- Agents can spend significant time and tokens planning or executing against stale baselines.
- Ledger files (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`) can encounter append collisions if not handled
  hermetically.
- Pull Requests get blocked with "This branch has conflicts that must be resolved" on GitHub.

## Tasks & Scope

### 1. Stage Boundary Conflict Detection

- **Stage 1 (Intent)**:
  - Verify that the target base branch (`origin/main`) is fetched and up to date before creating the `I-.../_` branch.
- **Stage 2 (Plan)**:
  - Before spawning the planner agent, check if `origin/main` has advanced since the intent branch was cut.
  - Test for mergeability / rebase cleanliness against updated `origin/main`.
- **Stage 3 (Execute)**:
  - Check whether `origin/main` has advanced since the plan branch was created.
  - Automatically rebase or merge upstream changes into the execution branch before generating code changes, or
    prompt/fail fast if code conflicts exist.
- **Stage 4 (PR Review Loop)**:
  - At the beginning of each review iteration, check `gh pr view <pr> --json mergeable` to detect if the PR has become
    `CONFLICTING`.
  - If conflicting, invoke conflict resolution (rebase onto updated `origin/main`, resolve trivial or ledger conflicts,
    push updated branch).
- **Stage 5 (Calibration)**:
  - Ensure the `/calibrated` branch cleanly merges or fast-forwards into the PR branch without conflict before
    completing the flow.

### 2. Automated Conflict Resolution Strategies

- **Append-Only Ledgers (`*.jsonl`)**:
  - Implement a dedicated union/append merge driver or reconciliation strategy for ledger files (`intents.jsonl`,
    `plans.jsonl`, `executions.jsonl`) so concurrent appends never cause merge aborts.
- **Source Code Conflicts**:
  - Distinguish between clean auto-merges, non-conflicting divergent edits, and semantic code conflicts.
  - If conflicts cannot be resolved automatically, surface structured diagnostic diffs and halt with clear instructions.
