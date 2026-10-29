---
# holon-agentic-coder-ref-metadata-0194
title: "Decompose run_execute_stage into an ExecuteStage with named steps"
status: todo
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0187
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `run_execute_stage` (`993b686`) is **306 lines, CC 40**, and was edited by three of the flow PRs
#94-#109 (#95 empty-diff guard, #97, #108 partial salvage). Helpers such as `_resumable_partial_branch`,
`_execution_effective_diff`, `_append_superseding_execution_row` and `_sync_local_execution_refs` share its state
through arguments.

## Scope

1. `ExecuteStage` class in `flow/stages/execute.py`: `resume_point`, `dispatch_executor`, `guard_empty_diff`,
   `salvage_partial`, `record_execution` as methods over one state object.
2. `run_execute_stage` stays as a thin wrapper used by the pipeline.
3. All touched functions within the 0185 limits; empty-diff guard, partial salvage and resume behaviour unchanged.

## Touch set

`flow/stages/execute.py`, `tests/flow/test_execute.py` (or the mirrored test module).

## Dependencies

Blocked by 0187. Parallel-safe with 0191, 0193, 0197. Sequence with 0151 (touch-set admission lands next to the
empty-diff guard) and 0183.

## Notes

- Run through the Holon flow on holon-agentic-coder.
