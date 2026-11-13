---
# holon-agentic-coder-ref-metadata-0296
title: "Stage 5 rebuilds a stale calibrated branch itself instead of stopping after a conflict merge"
status: todo
type: bug
priority: high
tags:
  - stage-5
  - calibration
  - holon-agentic-coder
created_at: 2026-11-13T13:00:00Z
updated_at: 2026-11-13T13:00:00Z
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
