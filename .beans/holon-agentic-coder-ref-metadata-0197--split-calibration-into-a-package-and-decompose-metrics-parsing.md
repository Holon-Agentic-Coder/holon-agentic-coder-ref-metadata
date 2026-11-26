---
# holon-agentic-coder-ref-metadata-0197
title: "Split calibration.py into a calibration package and decompose metrics parsing and report generation"
status: in-progress
type: task
priority: normal
tags:
  - refactor
  - complexity
  - calibration
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-26T04:00:00Z
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

Was blocked by 0187, now scrapped; no longer applies. Sequence **after 0146** (picks the predicted metrics in the same
parser) and 0162; sequence with 0183 (calibration moves into a sandbox).

## Notes

- Run through the Holon flow on holon-agentic-coder.

## Audit (2026-11-20)

Calibration is still one `calibration.py` module (1642 lines); the Bean 0187 blocker is scrapped and no longer applies.

## Audit (2026-11-21)

Partly done: helpers were extracted into `calibration_diff.py`, `calibration_ev.py`, `calibration_execution_owner.py`,
`calibration_outcome.py` and `calibration_touch_set.py`
([PR #213](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/213) and earlier), but `calibration.py` is
still one large module with `parse_actual_metrics` under noqa. Remaining scope: the package split and decomposing the
metrics parsers. Do not run concurrently with Bean 0146 (same parser).

## Audit (2026-11-23)

Bean `0146` merged in PR #221 (extracting `calibration_predicted.py`). `calibration.py` is 1,637 lines with
`parse_actual_metrics` still under noqa. Unblocked and disjoint from PR #230 (which edits `calibration_outcome.py`, not
`calibration.py` or `flow/stages/calibrate.py`); sequence with `0355` on `flow/stages/calibrate.py`.

> 2026-11-23: stale worktree deleted 2026-11-23; restart from current main. Backup:
> todo/stale-worktree-backups/flow-split-calibration-package-2026-11-23.bundle

## Progress (2026-11-24)

- Flow started from this Claude Code session: intent `todo/intent-0197-split-calibration-package.json`, slug
  `split-calibration-package`, `claude-agent` / `claude-fable-5-2`, worktree `flow-split-calibration-package`.

Note (2026-11-25): stale plan `split-calibration-package` deleted after PR #309 merged; restart from current main via
the kept `todo/intent-0197-split-calibration-package.json`.

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- `PR #310` (`0371` sub-intent 1) and `PR #311` (`0371` sub-intent 2) were both blocked in Iteration 1 by all reviewers
  specifically because `calibration.py` (`1,634` lines, over `1,000`) grew by `+1` to `+2` lines and
  `test_calibration.py` (`1,780` lines) grew by `+16` lines.

## Progress (2026-11-26)

- Flow started from this Claude Code session on origin/main 4e358955: intent
  `todo/intent-0197-split-calibration-package.json`, slug `split-calibration-package`, `claude-agent` /
  `claude-opus-5-5` (`claude-fable-5-2` is over its monthly spend limit), worktree `flow-split-calibration-package`
  (created by the runner), log `todo/flow-split-calibration-package.log`.
- 2026-11-26 (flow `split-calibration-package`, runner on `claude-agent` / `claude-opus-5-5`): Stage 3 admission refused
  on overlap with local flow `no-unneeded-full-review` (PR #316 when it opened). Current run is intent `I-1795669744` /
  plan `P-1795669767`. Resume with `--checkpoint` after the overlap clears. Bug bean 0477 logs the fresh-restart
  relaunch.
