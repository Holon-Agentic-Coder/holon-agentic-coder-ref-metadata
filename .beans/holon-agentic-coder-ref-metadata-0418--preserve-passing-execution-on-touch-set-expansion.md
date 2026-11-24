---
# holon-agentic-coder-ref-metadata-0418
title: "Preserve passing executions on touch-set expansion and decompose re-plan failures"
status: todo
type: feature
priority: medium
tags:
  - flow
  - stage-2
  - stage-3
  - touch-set
  - holon-agentic-coder
created_at: 2026-11-24T11:05:00Z
updated_at: 2026-11-24T11:05:00Z
---

## Why

When Stage 3 finishes with a passing test suite and only a small out-of-touch-set companion edit (e.g. `README.md` or
tests), `pipeline._replan_after_over_budget` discards the entire passing execution branch and reruns Stage 2 and Stage 3
from scratch (and aborts decomposed parent flows if Stage 2 re-plan hits an error). Bean 0414 blocks out-of-set writes
_during_ an executor turn; this bean covers preserving passing work and safely resuming decomposed flows when
expansion/re-planning still triggers.

## Evidence

- `todo/flow-claude-code-mode-default-on.log` (lines 139–165): Stage 3 finished in `8.3 min` (`6437 passed, 0 failed`),
  then `touch_set_guard` discarded the execution over 1 file (`holon-config/metrics/README.md`) and reran Stage 2
  (`3.6 min`) + Stage 3 (`7.2 min`) from scratch.
- `todo/flow-resolve-conflicts-in-flow.log` (lines 1796–1833): sub-intent 3/5 ran `15.8 min` (`6350 passed`), hit
  `touch_set_guard` on 3 files, returned to Stage 2 (`re-plan attempt 1 of 2`), immediately hit
  `ConflictResolutionError` in `plan` stage, and aborted `198.7 min` of a decomposed flow.
- `apps/sandbox-executor/src/sandbox_executor/flow/pipeline.py` (lines 242–308) and `budgets.py`
  (`MAX_REPLAN_ATTEMPTS = 2`): on exhaustion, `touch_set_replan_exhausted` throws away the execution branch even when
  tests are green.

## Proposed change

1. When `touch_set_guard` triggers on a passing execution (`rate == 1.0`) and the out-of-set paths are bounded companion
   files (or the executor explicitly requests touch-set expansion), widen the plan's touch set and re-run admission
   against the expanded set **preserving the execution branch** rather than discarding it and re-executing from scratch.
2. When a decomposed sub-intent fails during re-plan (`_replan_after_over_budget`), persist the sub-intent
   checkpoint/branch state cleanly so resume continues from that sub-intent rather than throwing away earlier progress.

## Expected gain

Saves 10–30+ minutes per touch-set expansion on passing executions and prevents parent decomposed flow restarts.

## Cost

Medium change in `apps/sandbox-executor/src/sandbox_executor/flow/pipeline.py` and `flow/stages/touch_set_guard.py`.

## Notes

- Complementary to Bean 0414 (in-turn write guard) and Bean 0376 (in-flow conflict resolution in Stage 2).
