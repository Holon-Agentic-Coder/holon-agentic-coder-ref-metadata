---
# holon-agentic-coder-ref-metadata-0445
title: "End-of-flow sync leaves checkpoint stuck at completed during Stage 4/5 re-entry"
status: todo
type: bug
priority: high
tags:
  - flow
  - end-of-flow-sync
  - checkpoint
  - stage-4
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-25T04:02:00Z
updated_at: 2026-11-25T04:02:00Z
---

## Problem

When Stage 5 finishes cleanly, `PipelineEngine._run_stages` / `_handle_review_boundary` (`flow/pipeline.py:362-388`)
saves the checkpoint with `current_stage = "completed"` and `calibrate.status = "success"` before calling
`_finalize_approved_flow` $\rightarrow$ `finish_flow`. If `finish_flow` (`flow/end_of_flow_sync.py:160-173,199`) then
sees `CONFLICTING`/`DIRTY`, merges `origin/main`, and calls `_reenter_review_and_calibrate`,
`record(FlowStage.REVIEW, review)` runs only **after** `run_stage(FlowStage.REVIEW)` finishes. For the entire duration
of the re-entered Stage 4 (and Stage 5), the checkpoint on disk remains frozen at `current_stage: "completed"` with
stale Stage 5 `success` and frozen `context.logs`.

## Evidence (`2026-11-25T02:54Z–03:54:45Z` fifth-merge audit)

- On `holon-agentic-coder#308` (`workspace-survival-job-parallel`), Stage 5 exited and saved
  `apps/holon-agentic-coder/flow-workspace-survival-job-parallel/.holon/flow/checkpoint-workspace-survival-job-parallel.json`
  at `2026-11-25T03:39:19Z` (`current_stage: "completed"`, `90` entries in `context.logs`).
- At `03:39:20Z`, `End-of-flow sync round 1/3` detected `CONFLICTING/DIRTY` (ledger-only conflict after `#288` merged at
  `03:35:55Z`), merged `558646ae` (`adaf72a8` at `03:39:23Z`), and re-entered Stage 4 from `03:39:28Z` through
  `03:54:45Z+` (`15.3+ min` across `2` review iterations and `1` resolver pass in
  `todo/flow-workspace-survival-job-parallel.log`).
- Throughout those `15.3+ min`, `checkpoint-workspace-survival-job-parallel.json` still reported
  `current_stage: "completed"`, `calibrate.status: "success"`, and zero post-`03:39:19Z` log entries, making the live
  Stage 4 run appear finished to `bean_progress.py` and any checkpoint reader.

## Proposed change

1. In `end_of_flow_sync._reenter_review_and_calibrate` (and/or `PipelineEngine._finalize_approved_flow`), save a
   checkpoint marking the re-entered stage (`review` / `calibrate`) as active/in-progress before dispatching
   `run_stage(...)`, and flush `context.logs` during re-entry.
2. Add a hermetic unit test in `tests/flow/test_end_of_flow_sync.py` verifying the checkpoint transitions out of
   `completed` as soon as `finish_flow` re-enters Stage 4.

## Expected gain

Eliminates `15+ min` windows of false `completed` state in `checkpoint-*.json`, `bean_progress.py`, and resume safety
checks whenever end-of-flow target sync triggers Stage 4/5 re-entry.

## Cost

Small: checkpoint state transition before `run_stage` in `end_of_flow_sync.py` + unit test, delivered via the Holon
flow.

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0407` (mechanical `end_of_flow_sync` merges should carry approval without full Stage 4 re-entry), Bean
  `0388` (harness `bean_progress.py` stale stage display), Bean `0412` (step timing and logging).

## Audit evidence, 2026-11-25T05:07Z (self-improvement audit, fifth merge #290–#294)

- **`PR #308` (`workspace-survival-job-parallel`):** `checkpoint-workspace-survival-job-parallel.json` remained frozen
  at `current_stage: "completed"` (`calibrate.end_time: "2026-11-25T04:14:18Z"`) throughout the entire **`49.6+ min`**
  Round 2 Stage 4 re-entry (`04:14:18Z..05:04:00Z+`, Iters 1–3, `27.02 min` + `4.47 min` resolver turns, `2`
  `review_local` runs, live Iter 3).
