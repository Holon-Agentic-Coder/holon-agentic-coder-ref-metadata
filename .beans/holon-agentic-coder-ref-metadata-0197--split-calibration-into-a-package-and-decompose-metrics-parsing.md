---
# holon-agentic-coder-ref-metadata-0197
title: "Split calibration.py into a calibration package and decompose metrics parsing and report generation"
status: todo
type: task
priority: normal
tags:
  - refactor
  - complexity
  - calibration
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0187
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `calibration.py` (`993b686`) is 1,524 lines, radon MI grade C, 11 commits since 2026-10-01.
Measured: `parse_actual_metrics` **226 lines, CC 61**; `generate_calibration` CC 32; `resolve_git_ref` CC 29;
`parse_predicted_metrics` CC 25; `run_calibrate` CC 22; `compute_calibration_deltas` CC 21; the flow's
`run_calibrate_stage` CC 27.

## Scope

1. `calibration/` package: `predicted.py` (`PredictedMetrics.from_plan`), `actual.py` (`ActualMetrics.from_execution`),
   `deltas.py` (pure), `report.py` (rendering), `run.py` (I/O shell); re-exports from `calibration/__init__.py`.
2. Metric parsers become a table of small per-metric extractors instead of one 61-branch function.
3. `resolve_git_ref` uses the `git` adapter from 0195 if it has landed.
4. `flow/stages/calibrate.py` delegates to `calibration.run`; all functions within the 0185 limits; reports
   byte-identical on the existing fixtures.

## Touch set

`calibration.py` (becomes a package), `flow/stages/calibrate.py`, `tests/test_calibration.py` (split).

## Dependencies

Blocked by 0187. Sequence **after 0146** (picks the predicted metrics in the same parser) and 0162; sequence with 0183
(calibration moves into a sandbox).

## Notes

- Run through the Holon flow on holon-agentic-coder.
