---
# holon-agentic-coder-ref-metadata-0118
title: "Implement explicit native holon review-loop CLI step after execute stage"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - cli
  - pr-review-loop
  - review
  - architecture
  - holon-agentic-coder
created_at: 2026-10-17T07:05:00Z
updated_at: 2026-10-17T08:15:00Z
---

## Summary

Promote the Pull Request review loop from an external agent harness skill (`pr-review-loop`) into an explicit, native
`holon review-loop` CLI command and pipeline stage within `holon-agentic-coder`, executing immediately after the initial
`holon execute` step.

## Context & Problem Statement

Currently, the 5-stage Holon flow lifecycle is split across two operational boundaries:

| #   | Stage              | Current Implementation                                                     | Target Implementation                                   |
| --- | ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------- |
| 1   | Intent             | `holon intent <intent.json>`                                               | `holon intent <intent.json>`                            |
| 2   | Plan               | `holon plan <intent_branch>`                                               | `holon plan <intent_branch>`                            |
| 3   | Execute            | `holon execute <plan_branch>`                                              | `holon execute <plan_branch>`                           |
| 4   | **PR Review Loop** | External agent skill (`.agents/skills/pr_review_loop/`) + manual subagents | **`holon review-loop <execution_branch>` (Native CLI)** |
| 5   | Calibration        | `holon calibrate <execution_branch>`                                       | `holon calibrate <execution_branch>`                    |

### Drawbacks of Using an External Harness Skill for Stage 4:

1. **Broken Autonomous Pipeline**:
   - `holon flow <intent.json>` cannot run end-to-end headlessly if Stage 4 requires an interactive, external agent
     harness skill to spin up subagents and resolve findings manually.
2. **Environment & Runtime Lock-In**:
   - Relying on the Antigravity `invoke_subagent` skill pattern makes headless CI/CD runs and execution across generic
     terminals or headless servers impossible without special prompt rigging.
3. **Ledger & Provenance Fragmentation**:
   - Reviews driven outside the Holon binary rely on the harness agent to accurately format git trailers and record
     events to `executions.jsonl` (Bean 0113). A native CLI command ensures atomic ledger commits and provenance
     guarantees directly from Python.

## Proposed Design & Lifecycle

The PR review loop becomes a first-class, explicit step executed immediately following the initial `holon execute`:

```text
holon intent  -->  holon plan  -->  holon execute  -->  holon review-loop  -->  holon calibrate
```

### CLI Command Specification:

```bash
holon review-loop <execution_branch_or_pr> [options]

Options:
  --max-iterations INT     Maximum review-and-resolve iterations (default: 25)
  --ensemble-size INT      Number of independent review passes (default: 3)
  --auto-pr                Automatically open GitHub PR if not already raised (default: true)
  --fail-fast              Halt on any critical non-resolvable failure
  --dry-run                Simulate review passes without pushing commits
```

### Operational Workflow:

1. **PR Association**: Resolves or raises the GitHub Pull Request targeting the base branch for the given execution
   branch (`I-.../P-.../E-.../_`).
2. **CI Health Gate**: Probes remote GitHub Actions status (`gh pr checks`) to ensure baseline checks have commenced and
   evaluates failure logs.
3. **Multi-Pass Review Ensemble**: Dispatches independent reviewer evaluations (Hygiene, Architecture/Security,
   Alignment/Testing) using configured agent runners.
4. **Autonomous Resolution Pass**: If findings are present, runs a sandboxed resolver agent to apply fixes, verifies the
   test suite, attaches `Review-Iteration`, `Review-Finding-Ids`, and `Review-Severity` trailers, and pushes updates to
   the execution branch.
5. **Consensus Termination**: Stops on unanimous approval or halts for human review under Bean 0034 safety policies
   before advancing to Stage 5 (`holon calibrate`).

## Tasks & Scope

- [x] Add `review-loop` (and aliases `review`, `pr-review-loop`) subcommand to `sandbox_executor/cli.py`.
- [x] Implement native review loop orchestration engine in `sandbox_executor/flow.py`:
  - Iterative review ensemble dispatch.
  - Resolver execution and git trailer appending (`Action-Origin: pr_review`).
  - GitHub PR comment synthesis and status updates via `gh` CLI.
- [x] Connect Stage 4 in `holon flow` to run `run_review_stage` using the native review loop engine.
- [x] Add unit and integration tests in `apps/sandbox-executor/tests/test_flow.py` and `tests/test_cli.py`.
- [x] Update `AGENTS.md`, `.agents/workflows.md`, and `README.md` to specify `holon review-loop <execution_branch>` as
      the standard Stage 4 invocation.
- [x] Route implementation through the 5-stage Holon flow.

## Resolution Summary

1. **Stage 1 (Intent)**: Created intent branch `I-1792220943-native-holon-review-loop-step/_` and recorded in
   `intents.jsonl`.
2. **Stage 2 (Plan)**: Created plan branch
   `I-1792220943-native-holon-review-loop-step/P-1792220973-antigravity-agent-gemini-3.8-flash-medium/_` and generated
   plan with predicted EV +35.00.
3. **Stage 3 (Execute)**: Sandboxed executor implemented `review-loop` CLI subcommand (and aliases `review`,
   `pr-review-loop`) in `cli.py`, `run_review_loop` and `run_review_loop_cli` in `flow.py`, added unit tests in
   `test_cli.py` and `test_flow.py`, and recorded in `executions.jsonl`.
4. **Stage 4 (PR Review Loop)**:
   - Raised PR #81 on `holon-agentic-coder`.
   - Iteration 1 ensemble review flagged empty commit creation and 4 Ruff lint errors.
   - Resolver applied fixes (commit `507c523`): removed empty git commits from `run_review_loop`, enforced
     `effective_dry_run`, isolated ledger SQLite database path, fixed Ruff errors, and added direct
     `run_review_loop_cli` tests. All unit tests (608) and workspace survival stress test passed.
   - Iteration 2 ensemble review unanimously approved with 0 Critical, 0 Important, 0 Nit. All 10 GitHub Actions checks
     passed. Posted consensus review to PR #81.
5. **Stage 5 (Calibration)**: Executed `holon calibrate` (Actual EV: 46.75, ΔEV: +11.75). Created and pushed
   `/calibrated` branch. Fast-forwarded calibration report into execution branch PR diff (`c026107`) and pushed to
   origin.
6. Awaiting manual human maintainer merge per Bean 0034.
