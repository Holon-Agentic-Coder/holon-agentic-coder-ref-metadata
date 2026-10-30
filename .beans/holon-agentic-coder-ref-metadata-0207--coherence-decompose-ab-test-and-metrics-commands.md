---
# holon-agentic-coder-ref-metadata-0207
title: "holon-coherence: move A/B evaluation and metrics aggregation out of the command handlers and decompose them"
status: todo
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0203
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
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
