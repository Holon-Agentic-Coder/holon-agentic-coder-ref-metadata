---
# holon-agentic-coder-ref-metadata-0296
title: "Stage 5 rebuilds a stale calibrated branch itself instead of stopping after a conflict merge"
status: completed
type: bug
priority: high
tags:
  - stage-5
  - calibration
  - holon-agentic-coder
created_at: 2026-11-13T13:00:00Z
updated_at: 2026-11-14T00:46:41Z
---

## Problem

When a flow is resumed after the pull request branch moved (a conflict merge with `main`, a resolver push), Stage 5
finds the `calibrated` branch from the earlier run, which no longer contains the execution head, and stops with
`Calibrate stage failed: existing '.../calibrated' does not contain the execution head ... Delete it (git branch -D ...) and resume`.
This is the fail-loudly rule from the Stage 5 sync work, but the recovery is manual. Seen on holon-agentic-coder PR
#190: the flow ended with a failed Stage 5, the pull request merged with a calibration report that predates the final
head, and nothing in the report-back said so.

## Goal

1. When the existing `calibrated` branch is a strict ancestor of the execution head, or no longer descends from it, and
   holds only the flow's own calibration commits, Stage 5 deletes and rebuilds it from the origin execution head, logs
   what it replaced, and continues.
2. When the branch holds commits that are not calibration commits, keep failing loudly with the existing message.
3. The flow's final report states which head the calibration report covers.
4. Hermetic tests: a stale calibrated branch is rebuilt; one with foreign commits still stops; the report names its
   head.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths. Touches `flow/calibrate_sync.py` and `flow/stages/calibrate.py`.
- Related: Beans 0253 (the check) and 0292 (the final-head CI check).

## Resolution

Delivered via [PR #193](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/193) and merged into `main`
(`291727e`, 2026-11-14T00:44:34Z, merged by the maintainer):

- **Key Architectural Deliverables**: Stage 5 deletes and rebuilds a stale `calibrated` branch that holds only the
  flow's own calibration commits, from the origin execution head, and logs what it replaced
  (`flow/calibrate_rebuild.py`, `flow/calibrate_sync.py`, `flow/stages/calibrate.py`). A `calibrated` branch holding
  foreign commits still fails loudly with the existing message. The final report names the head the calibration report
  covers.
- **Verification & Tests**: Hermetic tests added in `apps/sandbox-executor/tests/test_calibrate_rebuild.py`, with
  updates to `test_calibrate_sync.py`. The flow reported a first review loop approval 3/3 at head `e7f38cf`; this is not
  visible in GitHub reviews or the state files. The calibration report covers evaluated head `cb55140` (predicted EV
  45.46, actual 62.03, delta +16.57). Recorded state is weaker for the final head: a conflict merge with `main` voided
  the votes, and a second review loop ran with resolver fixes to final head `0e183d8`.
  `.subagent/holon-agentic-coder_pr193_state.json` still records iteration 3 at `4c389e4`, and `_loop_history.md` ends
  at iteration 5 with iteration 6 resolver output at `0e183d8`. GitHub records only one `COMMENTED` review, at
  `cb55140`. No fresh 3/3 approval and no calibration report for `0e183d8` are recorded.
- **Holon Flow Traversal**: The flow ran on `claude-opus-5-5`; Fable pre-flight hit a limit with no reset time. Stages 1
  to 5 ran with a conflict-merge rerun. The calibration report covers `cb55140`, not the final merged head `0e183d8`.
