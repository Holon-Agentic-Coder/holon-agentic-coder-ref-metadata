---
# holon-agentic-coder-ref-metadata-0207
title: "holon-coherence: move A/B evaluation and metrics aggregation out of the command handlers and decompose them"
status: completed
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0203
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-31T09:12:00Z
---

## Problem

Spawned by Bean 0177. Measured on `68fdf67`: `commands/ab_test.evaluate_runs` **185 lines, CC 69**,
`evaluate_offline_ab_run` 167 lines, CC 44, `handle_ab_test` 100 lines, CC 22 (module 899 lines, MI grade C);
`commands/metrics.handle_metrics` 172 lines, CC 36, `_read_offline_metrics` 170 lines, CC 30. Domain computation lives
in CLI handlers.

## Scope

1. `ab_testing/evaluation.py` (`AbRun`, `AbEvaluation` with pure scoring over real run records) and
   `metrics/aggregation.py` (`OfflineMetrics.from_logs`); `metrics_math.py` stays the numeric core.
2. Command handlers only parse arguments, call the domain objects and render.
3. All functions within the 0186 limits; outputs unchanged on the existing fixtures (real recorded runs only, no
   synthetic benchmark data).

## Touch set

`commands/ab_test.py`, `commands/metrics.py`, new `ab_testing/` and `metrics/` modules, `tests/test_ab_testing.py`, the
metrics tests split out by 0203.

## Dependencies

Blocked by 0203. Parallel-safe with 0208.

## Notes

- Run through the Holon flow on holon-coherence.

## Progress (2026-10-31)

- Created dedicated worktree `apps/holon-coherence/flow-0207-decompose-ab-and-metrics` from `origin/main` (`ca43eb9`).
- Prepared intent file `todo/intent-0207-coherence-decompose-ab-test-and-metrics-commands.json`.
- Executed `holon flow`:
  - Stage 1 completed: intent branch `I-1793425546-coherence-decompose-ab-test-and-metrics-commands/_` created and
    pushed.
  - Stage 2 completed: planner produced `plans/P-1793425560-antigravity-agent-gemini-3.8-flash-medium.md` (predicted EV
    7.94).
  - Stage 3 completed: executor produced `E-1793425877-antigravity-agent-gemini-3.8-flash-medium` decomposing
    `commands/ab_test.py` and `commands/metrics.py` into `ab_testing/` and `metrics/` domain modules, adding 13 new unit
    tests.
- Opened Pull Request [#40](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/40) on `holon-coherence`.
- Stage 4 PR Review Loop:
  - Iteration 1: dry run caught unused imports in `tests/test_ab_testing_domain.py`; resolver fixed in `bb4cef2` with
    all tests and lint passing.
  - Iteration 2: 3-agent ensemble reached unanimous `APPROVED (3/3)` consensus with 0 findings; consensus review posted
    to GitHub. Recorded `ACT-REV` and `ACT-POST` in `executions.jsonl` under `88ed127`.
- Stage 5 Calibration completed (`ffd6c9e`, Predicted EV: 7.94, Actual EV: 8.41, $\Delta\text{EV} = +0.47$) and pushed
  to `/calibrated` and PR #40 head.
- Merged into `main` by maintainer as `d6f1655a09b00189b60bab11ec4b6cb0ad793522` (`d6f1655`) at 2026-10-31T09:10:59Z.
