---
# holon-agentic-coder-ref-metadata-0113
title: "Append granular execution and PR review loop actions to execution ledger"
status: completed
type: feature
priority: high
tags:
  - ledger
  - executions-ledger
  - holon-flow
  - pr-review-loop
  - provenance
created_at: 2026-10-17T05:30:00Z
updated_at: 2026-10-17T14:00:00Z
---

## Summary

Currently, `holon-knowledge/ledger/executions.jsonl` only records a single coarse-grained summary line per flow run
(from the planning/execution completion). The intermediate actions during the execution step (such as discrete code
changes, tool invocations, and test suites), as well as all actions across the PR review loop (review evaluations,
resolver fixes, formatting passes, and ensemble consensus reviews), do not append to `executions.jsonl`.

This task expands the Holon flow engine (`flow.py`), the execution harness (`executor.py`), and the PR review loop
skills (`pr-review-loop`, `pr-review-resolver`, `pr-reviewer`) so that discrete execution actions and all PR review loop
iterations append structured `entry_type: "action"` rows to `holon-knowledge/ledger/executions.jsonl`.

## Problem Statement

1. **Coarse-Grained Single-Line Logging**:
   - Only a single summary entry (`entry_type: "summary"`, e.g. `status: "success"`,
     `summary: "Plan executed successfully"`) is recorded in `executions.jsonl` at the end of the execution stage.
   - Individual plan step completions, environment configurations, and discrete test executions are absent from the
     permanent execution ledger.
2. **Missing PR Review Loop Actions**:
   - Stage 4 of the Holon flow executes an iterative PR review loop with reviewers and resolvers fixing defects and
     verifying CI.
   - These review findings, resolutions, and consensus approvals currently only write to local `.subagent/`
     markdown/json files and git commit trailers. None of these actions are appended to
     `holon-knowledge/ledger/executions.jsonl`.
   - As a result, downstream calibration and learning tools cannot query `executions.jsonl` to observe how many review
     iterations took place, what findings were resolved, or which review severity levels were triggered.

## Key Requirements & Scope

### 1. Unconditionally Enable Action Logging (`is_action_logging_enabled()`)

- Update `is_action_logging_enabled()` in `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` (and any
  related callers) so that action logging is **always enabled by default** (`return True`), rather than requiring
  special environment flags (`HOLON_ACTION_LOGGING`) or review trailers.
- Preserve optional override to suppress only when explicitly set to `0`/`false`/`off`.

### 2. Stage 3 (Execute) Action Logging in Flow Engine

- During Stage 3 (`stage_execute` in `flow.py` and `executor.py`):
  - Append an `entry_type: "action"` row for each discrete operation:
    - Pre-execution dependency and environment setup.
    - Test suite executions (with pass/fail outcome, duration, and test pass rate).
    - Code and documentation formatting passes (e.g. Prettier convergence).
    - Git commit operations with provenance trailers.
  - Schema must include: `entry_type: "action"`, `action_id`, `execution_id`, `event_type`, `action`, `category`,
    `labels`, `target`, `outcome`, and `action_origin: "initial_implementation"`.

### 3. Stage 4 (PR Review Loop) Action Logging

- During Stage 4 (`stage_review` in `flow.py` and `pr-review-loop` skills):
  - **Review Evaluation**: Append an action record for each review pass (recording iteration number, verdict
    `APPROVED | CHANGES_REQUESTED`, counts of Critical, Important, and Nit findings, and `action_origin: "pr_review"`).
  - **Resolver Fixes**: Append an action record for each applied resolution (recording `review_finding_ids`,
    `review_severity`, `review_iteration`, affected files, and verification test outcomes).
  - **Ensemble Consensus**: Append an action record when the 3-agent ensemble consensus review completes (recording
    voting breakdown across personas, consensus score, and GitHub review submission receipt).

### 3. Concurrency Safety & Storage Invariants

- All ledger appends to `holon-knowledge/ledger/executions.jsonl` must use atomic file locking (`atomic_ledger_append`)
  and preserve append-only immutability.
- Maintain full backward compatibility for consumers of `executions.jsonl` (`calibration.py`, `holon ledger query`, and
  knowledge indexing).

### 4. Tests & Documentation

- Add hermetic unit and integration tests verifying that flow runs and review loop cycles append both action and summary
  records to `executions.jsonl`.
- Update `docs/ledger_schema.md` to document the Stage 3 execution and Stage 4 review loop action record schemas.

## Resolution

Implemented via 5-stage Holon flow on `holon-agentic-coder` in PR
[#82](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/82).

- Extended `flow.py` review loop and executor harness to record granular `entry_type: "action"` rows to
  `holon-knowledge/ledger/executions.jsonl` for evaluations, findings detection, resolver passes, and PR review
  consensus dual-posting.
- Added comprehensive hermetic unit tests in `test_flow.py::test_review_loop_granular_ledger_records`.
- 3-agent ensemble consensus approved (0 Critical, 0 Important, 0 Nit). Calibration executed and included in PR.
