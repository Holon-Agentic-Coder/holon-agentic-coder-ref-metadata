---
# holon-agentic-coder-ref-metadata-0197
title: "Split calibration.py into a calibration package and decompose metrics parsing and report generation"
status: completed
type: task
priority: normal
tags:
  - refactor
  - complexity
  - calibration
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-26T20:59:39Z
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

## Progress (2026-11-27)

- Resumed (from parked state) from checkpoint `checkpoint-split-calibration-package.json` via
  `run_holon_flow.py --no-wait-on-overlap`; no runner was live for the slug. Stage 3 admission passed (no overlap); the
  plan was refreshed onto origin/main `f1e18bcd`.
- First Stage 3 run completed (26.9 min) but changed 3 files outside the plan touch set (golden fixture,
  `test_calibration_ev.py`, `test_calibration_touch_set.py`); engine returned to Stage 2 (re-plan 1 of 2) and produced
  plan `P-1795700156-CLA-CO5.5` (EV 36.90). Stage 3 is re-running on that plan.
- Stage 3 (second run, on plan `P-1795700156-CLA-CO5.5`, EV 36.90) completed: 29 paths changed; Stage 4 approved 3/3
  (iteration 2 scoped re-review); Stage 5 calibration ok (actual EV 59.19, delta +22.29), report
  `plans/I-1795669744-split-calibration-package/P-1795700156-CLA-CO5.5_calibration.md` included in the PR diff.
- PR [#347](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/347): OPEN, MERGEABLE, CLEAN, all checks
  green. Awaiting human maintainer merge. Bean stays in-progress until merge; post-merge protocol closes it.

## Resolution

Delivered via [PR #347](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/347) and merged into `main`
(`8b20863`):

- **Key Architectural Deliverables**: `calibration.py` (1,608 lines) is now the `calibration/` package of 12 modules
  (`predicted`, `actual`, `actual_evidence`, `branches`, `checkout`, `deltas`, `generate`, `physics`, `refs`, `report`,
  `run`, plus `__init__` re-exports); the largest module is 273 lines. `flow/stages/calibrate.py` delegates to
  `calibration.run`. Metric parsing is split into per-metric extractors. `resolve_git_ref` is decomposed.
- **Verification & Tests**: calibration tests split into `test_calibration_metrics.py` and `test_calibration_report.py`;
  reports byte-identical on the existing fixture (`calibration_report_golden.txt`).
- **Holon Flow Traversal**: Intent, Plan (re-planned once after Stage 3 touched files outside the plan touch set),
  Execute, Review Loop (approved 3/3 on iteration 2) and Calibration (actual EV 59.19, delta +22.29) completed.
- **Follow-up**: `holon-config/hygiene/module_budgets.json` still carries the stale `calibration.py` override (1608);
  the file no longer exists. The budget file is frozen, so the entry was left for the maintainer to remove.
