---
# holon-agentic-coder-ref-metadata-0631
title: "Stage 3 resume skips refreshing stale plan_branch onto origin/main"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-3
  - target-sync
  - resume
  - holon-agentic-coder
created_at: 2026-11-27T12:11:44Z
updated_at: 2026-11-27T20:56:57Z
---

## Notes

### Evidence (2026-11-27T12:01Z, `CF-0061`)

- Resuming Coherence Bean `0527` (`coherence-provider-format-seam`) `--from-stage execute` after `PR #77` (`bfdb1fd`)
  merged failed with `module_budget_change_refused` (`E-1795780320`) because pre-`#77` plan branch `334357d` was never
  merged with `origin/main` before the executor container ran.
- Inspecting `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/flow/`:
  1. `pipeline.py:299` (`at_flow_start`) and `execute.py:175` (`at_stage_boundary(EXECUTE, STAGE_START)`) resolve the
     branch to sync via `target_sync_hooks.active_flow_branch(context, FlowStage.EXECUTE)` (`target_sync_hooks.py:52`),
     which returns `(context.execution_branch, context.plan_branch, context.intent_branch)` — prioritizing any prior
     failed `context.execution_branch` over `context.plan_branch`.
  2. `plan_refresh_stage_failure` (`plan_refresh.py:119-135`, gated by `AdmissionRecord.refresh_due` in
     `admission_state.py:74-77`) only merges `origin/<target>` into `context.plan_branch` when `record.waited_since` is
     truthy (set only after an admission overlap wait), skipping external or manual resumes after `main` advances.
  3. `execute.py:207,238` then passes `context.plan_branch` to `dispatch_executor`, running the container on stale code.

### Proposed Change

1. In `execute.py` (`admit_and_refresh_plan`) / `plan_refresh.py`, whenever `origin/<target_branch>` is not an ancestor
   of `context.plan_branch` (`git merge-base --is-ancestor`), merge `origin/<target_branch>` into `context.plan_branch`
   before `dispatch_executor` runs, regardless of `waited_since` or a prior failed `context.execution_branch`.
2. Ensure `target_sync_hooks.active_flow_branch` for `FlowStage.EXECUTE` (or pre-dispatch sync) does not mask a stale
   `plan_branch` behind a prior failed `execution_branch`, halting fail-closed on merge conflict instead of wasting a
   container run.

### Expected Gain & Cost

- Eliminates wasted Stage 3 executor passes (`~4–15 min` each) and manual branch re-cuts whenever `origin/main` advances
  while a flow is halted or externally parked (`CF-0061`).
- Cost: ~30 lines across `flow/stages/execute.py`, `flow/plan_refresh.py`, `flow/target_sync_hooks.py`, and hermetic
  tests.

## Acceptance Criteria

- [ ] Starting or resuming Stage 3 (`--from-stage execute` or `--checkpoint`) checks whether `origin/<target_branch>` is
      an ancestor of `context.plan_branch` and merges `origin/<target_branch>` into `context.plan_branch` before
      `dispatch_executor`, even when `admission.waited_since` is unset or a prior failed `execution_branch` is present.
- [ ] Merge conflicts during `plan_branch` refresh halt fail-closed before dispatching the executor container.
- [ ] Hermetic unit tests cover `--from-stage execute` after `origin/main` advances with and without a prior failed
      `execution_branch`; `uv run pytest` and `uv run task lint` pass.

## Resolution

- **Slice 1 (`stage3-plan-branch-refresh`):** Launched `todo/intent-0631-stage3-plan-branch-refresh.json` covering
  `flow/stages/execute.py`, `flow/plan_refresh.py`, `flow/target_sync_hooks.py`, and their unit tests.
