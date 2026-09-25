---
# holon-agentic-coder-ref-metadata-0039
title: "Automate the end-to-end Holon flow lifecycle pipeline"
status: completed
type: task
priority: normal
tags:
  - automation
  - holon-flow
  - pipeline
created_at: 2026-09-26T09:20:00Z
updated_at: 2026-09-26T15:10:00Z
---

Design and implement the orchestration pipeline that automates the complete 5-stage Holon flow lifecycle: Intent
Creation -> Plan Generation -> Plan Execution -> PR Reviewer Loop -> Post-Execution Calibration.

## Context

Currently, the stages of the Holon lifecycle are executed as separate, manual steps (`./holon intent`, `./holon plan`,
`./holon execute`, running the `pr-review-loop` skill, and calibration). Automating this sequence into a unified
lifecycle pipeline allows autonomous agents and developer tooling to drive features from raw intent to verified,
reviewed, and calibrated branches without manual friction.

## Acceptance Criteria

1. Implement orchestration pipeline module in `apps/holon-agentic-coder/apps/sandbox-executor/`:
   - **Stage 1 (Intent)**: Ingest intent JSON file, validate schema, branch to `I-{timestamp}-{slug}/_`, and record
     entry in `holon-knowledge/ledger/intents.jsonl`.
   - **Stage 2 (Plan)**: Branch from intent to `I-.../P-{timestamp}-{agent}-{model}/_`, invoke planner agent container
     with prompt and repo structure, generate `plans/P-...md`, and record in `holon-knowledge/ledger/plans.jsonl`.
   - **Stage 3 (Execute)**: Branch from plan to `I-.../P-.../E-{timestamp}-{action}/_`, invoke execution agent container
     in isolated sandbox, perform codebase modifications, run test verification, commit changes, and record in
     `holon-knowledge/ledger/executions.jsonl`.
   - **Stage 4 (PR Reviewer Loop)**: Run the autonomous review loop (`pr-review-loop` ensemble model) on the execution
     branch. Resolve flagged issues via iterative review/resolver cycles until unanimous consensus approval is reached.
     - **Constraint Enforcement**: Strictly respect the Human-Only PR Merging constraint (Bean 0034) — the loop must
       stop at approval and notify the human maintainer; it must never merge autonomously.
   - **Stage 5 (Calibrate)**: Run post-execution calibration (Bean 0038) on the execution branch to compute predicted vs
     actual metric deltas and commit `plans/P-..._calibration.md` on the `/calibrated` branch.
2. Provide programmatic Python API for driving the lifecycle pipeline.
3. Include checkpointing and fault tolerance: if any stage fails, the pipeline aborts cleanly with descriptive error
   diagnostics and preserves all intermediate branches and ledger records.
4. Add unit and integration tests covering multi-stage transitions and mock agent runs.

## Notes

- Target repository: `apps/holon-agentic-coder/`
- Target files:
  - `apps/sandbox-executor/src/sandbox_executor/flow.py`
  - `apps/sandbox-executor/src/sandbox_executor/cli.py`
  - `apps/sandbox-executor/tests/test_flow.py`
- Dependencies: Bean 0038 (`holon calibrate`).

## Resolution

- **Pipeline Engine Implementation (`apps/sandbox-executor/src/sandbox_executor/flow.py`)**:
  - Implemented data models: `FlowStage`, `StageStatus`, `StageResult`, and `FlowContext` with JSON serialization
    roundtripping (`to_dict` / `from_dict`).
  - Implemented `PipelineEngine` state machine supporting atomic checkpoint persistence via `NamedTemporaryFile` +
    `os.replace`, pre/post stage lifecycle hooks, and resumption via `--from-stage` and `--checkpoint`.
  - Implemented 5 lifecycle stages:
    1. `run_intent_stage`: Validates schema, creates `I-{ts}-{slug}/_` branch, records intent in
       `holon-knowledge/ledger/intents.jsonl`.
    2. `run_plan_stage`: Branches to `I-.../P-{ts}-{agent}-{model}/_`, invokes planner, outputs `plans/P-...md`, appends
       to `plans.jsonl`.
    3. `run_execute_stage`: Branches to `I-.../P-.../E-{ts}-{agent}-{model}/_`, runs execution agent in isolated
       sandbox, verifies tests, records `executions/E-...md` and `executions.jsonl`.
    4. `run_review_stage`: Executes review loop. Upon consensus approval, sets status to `StageStatus.HALTED_FOR_HUMAN`,
       printing instructions for human maintainer merge without executing any automated merge commands (enforcing Bean
       0034).
    5. `run_calibration_stage`: Ingests telemetry, executes Bean 0038 calibration engine (`run_calibrate`), and commits
       `plans/P-..._calibration.md` to `.../calibrated` branch.
- **CLI Subcommand (`apps/sandbox-executor/src/sandbox_executor/cli.py`)**:
  - Added `holon flow` subcommand with support for `--from-stage`, `--checkpoint`, `--dry-run`, `--json`, and
    agent/model overrides without clobbering checkpoint defaults.
- **Comprehensive Test Suite (`apps/sandbox-executor/tests/test_flow.py`)**:
  - Added 25 unit and integration tests covering models, atomic checkpoints, each stage lifecycle, failure handling,
    negative edge cases, CLI ergonomics, Bean 0034 human halt assertions, and Bean 0038 calibration.
- **End-to-End Holon Flow Execution**:
  - Intent branch: `I-1790382419-automate-holon-flow-lifecycle-pipeline/_`
  - Plan branch:
    `I-1790382419-automate-holon-flow-lifecycle-pipeline/P-1790382430-antigravity-agent-gemini-3.8-flash-medium/_`
  - Execution branch:
    `I-1790382419-automate-holon-flow-lifecycle-pipeline/P-1790382430-antigravity-agent-gemini-3.8-flash-medium/E-1790397083-antigravity-agent-gemini-3.8-flash-medium/_`
  - Pull Request: [PR #58](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/58)
  - Ensemble Consensus Review: 3-agent ensemble unanimous approval (`3/3 APPROVED`), all 9 CI checks passing cleanly.
  - Calibration: Successfully generated and pushed to
    `I-1790382419-automate-holon-flow-lifecycle-pipeline/P-1790382430-antigravity-agent-gemini-3.8-flash-medium/E-1790397083-antigravity-agent-gemini-3.8-flash-medium/calibrated`
    (Predicted EV: 76.48, Actual EV: 82.65, ΔEV: +6.17).
