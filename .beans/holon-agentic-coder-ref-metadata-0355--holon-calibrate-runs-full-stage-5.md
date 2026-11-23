---
# holon-agentic-coder-ref-metadata-0355
title: "holon calibrate runs the full Stage 5 (report, reconciliation, knowledge promotion), like the flow"
status: completed
type: bug
priority: high
tags:
  - calibration
  - stage-5
  - cli
  - knowledge
  - holon-agentic-coder
created_at: 2026-11-21T18:45:00+11:00
updated_at: 2026-11-23T11:51:44+11:00
---

## Problem

The flow's Stage 5 (`run_calibrate_stage` in `flow/stages/calibrate.py`) does three things, each with its own commit:

1. `run_calibrate` writes and commits the calibration report;
2. `reconcile_records` reconciles the execution outcome in the executions ledger ("record stage 5 reconciliation");
3. `promote_pending_candidates` promotes knowledge and wisdom candidates ("record stage 5 promoted knowledge and
   wisdom").

The standalone `holon calibrate` command (`cli/commands/calibrate.py`) calls only `run_calibrate`. A calibration run by
hand, such as the one on PR #219 on 2026-11-21 after its review loop stalled, therefore produces the report but quietly
skips the reconciliation and the knowledge promotion. Nothing warns about it. The ledger never records the outcome, and
the knowledge base misses that flow's lessons.

## Action

Through the Holon flow on `holon-agentic-coder`:

- Extract one Stage 5 function, used by both the flow stage and `holon calibrate`, that runs `run_calibrate`, then
  `reconcile_records`, then `promote_pending_candidates`, with the same commits on the `/calibrated` branch.
  `run_calibrate_stage` and the CLI become thin callers, so the two paths cannot drift apart again.
- `holon calibrate` runs the full Stage 5 by default. A `--report-only` flag keeps the old behaviour and says so in its
  output. `--no-commit` still means no commits for every step.
- `--json` output includes the reconciliation outcome and the number of candidates newly promoted.
- Re-running is idempotent: calibrating the same execution twice appends no duplicate reconciliation rows and promotes
  nothing new (Stage 5 promotion already reports only new items).
- Hermetic tests:
  - `holon calibrate` produces the same commits and ledger rows as the flow's Stage 5 for the same execution;
  - `--report-only` skips reconciliation and promotion;
  - a second run is a no-op;
  - `--no-commit` leaves the tree with no commits.
- Update the CLI help and docs.

## Notes

- Follow-up for PR #219: its Stage 5 reconciliation and promotion did not run. Once this lands, re-run `holon calibrate`
  for that execution, or run the two missing steps by hand before it merges.
- Related: Bean 0342 (promotion counts only new items), Bean 0354 (stale local test gate, which caused the hand-run).
- PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/240 (flow run `calibrate-runs-full-stage-5`;
  review consensus APPROVED 3/3, calibrated, awaiting human merge).

## Resolution

Delivered via [PR #240](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/240) and merged into `main`
(`192c6e8`):

- **Key Architectural Deliverables**: Stage 5 is one shared function (`flow/stage5.py`) used by both
  `run_calibrate_stage` and `holon calibrate`. It runs `run_calibrate`, then `reconcile_records`, then
  `promote_pending_candidates`, with the same commits on the `/calibrated` branch. `holon calibrate` runs the full Stage
  5 by default; `--report-only` keeps the old behaviour and says so; `--no-commit` means no commits; `--json` reports
  the reconciliation outcome and newly promoted count. Re-runs are idempotent.
- **Verification & Tests**: Hermetic `tests/test_calibrate_full_stage5.py` covers CLI/flow parity, `--report-only`,
  second-run no-op, and `--no-commit`.
- **Holon Flow Traversal**: The flow ran through Intent, Plan, Execute, Review Loop (consensus APPROVED 3/3) and
  Calibration on branch `I-1795388477-calibrate-runs-full-stage-5/...`.
