---
# holon-agentic-coder-ref-metadata-0038
title: "Implement holon calibrate CLI command for post-execution plan calibration"
status: completed
type: task
priority: normal
tags:
  - cli
  - calibration
  - sandbox-executor
created_at: 2026-09-26T09:20:00Z
updated_at: 2026-09-26T10:22:00Z
---

Add the `holon calibrate <execution_branch>` CLI command to the `holon` host CLI tool in
`apps/holon-agentic-coder/apps/sandbox-executor/`.

## Context

In the Holon Flow lifecycle (Intent -> Plan -> Execute -> Calibrate), the calibration phase measures the accuracy of
predicted plan metrics against actual execution realities. Prior executions (such as Bean 0013) manually produced
`/calibrated` branches and `plans/P-..._calibration.md` reports. Automating this step as a first-class CLI command
(`holon calibrate`) enables systematic post-execution evaluation and feedback loops.

## Acceptance Criteria

1. Implement `holon calibrate` in `apps/sandbox-executor/src/sandbox_executor/cli.py` and supporting calibration module:
   - Accept `execution_branch` as a positional argument (e.g. `I-.../P-.../E-.../_`).
   - Create or check out the `/calibrated` branch: `I-.../P-.../E-.../calibrated`.
   - Parse predicted metrics from the plan markdown (`plans/P-...md`) or `holon-knowledge/ledger/plans.jsonl` (predicted
     success probability, predicted entropy, predicted cost, EV).
   - Ingest actual execution telemetry and metrics from `holon-knowledge/ledger/executions.jsonl` (and wire transaction
     logs where available): duration, token usage, exit code, test pass rate, and patch size.
   - Compute calibration deltas ($\Delta = |actual - predicted|$), accuracy score, and entropy deviation.
   - Generate and commit a calibration analysis report at `plans/P-{plan_id}_calibration.md` on the `/calibrated`
     branch.
2. Add comprehensive unit tests in `apps/sandbox-executor/tests/test_calibration.py`.
3. Support `--json` flag to output calibration metrics directly to stdout for automated tooling.
4. Verify all tests pass with `uv run pytest`.

## Resolution

- Fully implemented Phase 5 (`holon calibrate`) via the containerized Holon Flow:
  - **Intent**: `I-1790379374-add-holon-calibrate-command/_`
  - **Plan**: `I-1790379374-add-holon-calibrate-command/P-1790379384-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Execution**:
    `I-1790379374-add-holon-calibrate-command/P-1790379384-antigravity-agent-gemini-3.8-flash-medium/E-1790380653-antigravity-agent-gemini-3.8-flash-medium/_`
  - **Calibration**:
    `I-1790379374-add-holon-calibrate-command/P-1790379384-antigravity-agent-gemini-3.8-flash-medium/E-1790380653-antigravity-agent-gemini-3.8-flash-medium/calibrated`
- Implemented `calibration.py` module and `holon calibrate` CLI command in
  `apps/sandbox-executor/src/sandbox_executor/`.
- Implemented 20 unit tests in `apps/sandbox-executor/tests/test_calibration.py`.
- Resolved workspace isolation bug by patching `cleanup_repo_dir` in `test_intent_creator.py` and `test_planner.py`.
- Opened [Pull Request #56](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/56).
- Completed 3 iterations of the 3-agent ensemble consensus review; received unanimous 3/3 **APPROVED** verdict.
- All 9 GitHub Actions CI checks passed on head commit `0d2564b`.

## Notes

- Target repository: `apps/holon-agentic-coder/`
- Target files:
  - `apps/sandbox-executor/src/sandbox_executor/cli.py`
  - `apps/sandbox-executor/src/sandbox_executor/calibration.py`
  - `apps/sandbox-executor/tests/test_calibration.py`
