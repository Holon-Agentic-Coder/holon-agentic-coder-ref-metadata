---
# holon-agentic-coder-ref-metadata-0448
title:
  "end_of_flow_sync._reenter_review_and_calibrate leaves stale calibrate=SUCCESS, causing nested Stage 5 rerun and bogus
  consensus withdrawal"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - stage-5
  - end-of-flow-sync
  - calibration
created_at: 2026-11-25T05:07:00Z
updated_at: 2026-11-25T05:07:00Z
---

# `end_of_flow_sync._reenter_review_and_calibrate` leaves stale `calibrate=SUCCESS`, causing nested Stage 5 rerun and bogus consensus withdrawal

## Summary

When `end_of_flow_sync._reenter_review_and_calibrate` re-enters Stage 4 (`FlowStage.REVIEW`) after an end-of-flow target
merge, it leaves the prior Stage 5 `SUCCESS` result in `context.stage_results["calibrate"]` (and the prior `review`
result in `context.stage_results["review"]`). At the end of the re-entered Stage 4 loop (`run_review_loop`),
`review_calibration_freshness` sees `prior.status is StageStatus.SUCCESS`, immediately executes `run_calibrate_stage`
**inside Stage 4** before `record(FlowStage.REVIEW, review)`, and hits `stage5_merged_head_gate` comparing the new head
against the **stale prior** `review` entry — triggering a bogus `ACT-WITHDRAW` consensus withdrawal, a quadruple push
burst that cancels CI, and a redundant second full Stage 5 pass.

## Evidence

- `apps/sandbox-executor/src/sandbox_executor/flow/end_of_flow_sync.py:160-173`: `_reenter_review_and_calibrate` invokes
  `run_stage(FlowStage.REVIEW)` then `record(FlowStage.REVIEW, review)` without clearing
  `context.stage_results["calibrate"]` (`SUCCESS` from the completed prior Stage 5).
- `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py:773` & `calibrate_rerun.py:219-232`:
  `review_calibration_freshness(context, pr_number)` checks `prior = context.stage_results.get("calibrate")` and runs
  `run_calibrate_stage` inline inside Stage 4 before `record(FlowStage.REVIEW, review)` updates
  `context.stage_results["review"]`.
- `apps/sandbox-executor/src/sandbox_executor/flow/review_restart.py:119,130`: `stage5_merged_head_gate` reads the stale
  prior `review` result in `context.stage_results["review"]` and detects a head mismatch against the newly pushed Stage
  4 iteration head.
- **`holon-agentic-coder#308` (`workspace-survival-job-parallel`, 2026-11-25T04:01Z–04:14Z):**
  - At `04:01:25Z–04:02:13Z` (Round 1 Iter 2 after `end_of_flow_sync` Round 1), `review_calibration_freshness` triggered
    a nested `Stage 5 rerun` (`0.25 min`, `04:01:58Z..04:02:13Z`) inside Stage 4.
  - `stage5_merged_head_gate` issued a false consensus withdrawal (`ACT-WITHDRAW-1795579326-53dc30b3` at `04:02:08Z`)
    against the earlier `8f533e24` head even though reviewers had just passed Round 1 Iter 2 (`04:01:22Z`), creating a
    `4`-push burst (`60964f80` $\rightarrow$ `03b6dbe7` $\rightarrow$ `b95c09b7` $\rightarrow$ `3357edd2` in `39 s`)
    that cancelled CI on `03b6dbe7` and `b95c09b7`.
  - `_reenter_review_and_calibrate` then ran Stage 5 a **second time** (`04:02:13Z..04:14:18Z`, `12.08 min`: `7.97 min`
    `merged_head_ci` wait on `3357edd2` + `2.50 min` calibration + `1.08 min` `final_head_ci` wait on `f727226d`).

## Proposed Change

1. In `_reenter_review_and_calibrate` (`end_of_flow_sync.py`), before calling `run_stage(FlowStage.REVIEW)`, clear stale
   `context.stage_results.pop("calibrate", None)` (and supersede `context.stage_results["review"]` or mark calibration
   invalidated) because `_reenter_review_and_calibrate` itself runs Stage 5 immediately after Stage 4 finishes.
2. Guard `review_calibration_freshness` (`calibrate_rerun.py`) so it does not run nested `run_calibrate_stage` when
   called during an end-of-flow Stage 4/5 re-entry cycle (or only runs when Stage 4 is executed standalone after an
   earlier Stage 5).
3. Add a unit test in `apps/sandbox-executor/tests/` covering `end_of_flow_sync._reenter_review_and_calibrate` to assert
   `run_calibrate_stage` executes once after Stage 4 completes and `stage5_merged_head_gate` never withdraws the
   just-completed Stage 4 consensus against an outdated pre-reentry review head.

## Expected gain

Eliminates false `ACT-WITHDRAW` withdrawals, quadruple push bursts cancelling CI, and redundant nested `Stage 5 rerun` +
double Stage 5 cycles (`12.08 min` in `PR #308` Round 1) on every `end_of_flow_sync` re-entry.

## Cost

Small: state cleanup + guard in `end_of_flow_sync.py` / `calibrate_rerun.py` plus unit tests, delivered via the Holon
flow (`holon-agentic-coder`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0407` (skip full Stage 4 re-entry on ledger-only `end_of_flow_sync` merges), Bean `0443` (push
  batching), Bean `0445` (checkpoint status stale during re-entry).
- Audit source: `2026-11-25T05:07Z` fifth-merge self-improvement audit.
