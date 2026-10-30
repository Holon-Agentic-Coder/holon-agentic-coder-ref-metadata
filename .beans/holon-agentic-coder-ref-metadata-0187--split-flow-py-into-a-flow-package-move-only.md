---
# holon-agentic-coder-ref-metadata-0187
title: "Split flow.py into a flow/ package, one module per stage and concern (move only, AST-verified)"
status: todo
type: task
priority: high
tags:
  - refactor
  - architecture
  - concurrency
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0185
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `sandbox_executor/flow.py` (`993b686`) is 5,157 lines with 94 free functions and 7 classes. It was
changed by 7 of the 14 flow PRs #94-#109 (#94 #95 #96 #97 #100 #102 #108) and by 26 commits since 2026-10-01;
`tests/test_flow.py` (5,798 lines) by 8. The PRs collided inside the same functions (`run_review_stage` and
`run_review_loop` in 4 PRs each, `run_execute_stage` and `FlowContext.to_dict/from_dict` in 3), which forced the sync
and re-review rounds Bean 0151 counts (141 passes). The function inventory already falls into nine clusters: checkpoint,
ledger reconciliation, git helpers, GitHub PR/CI, intent validation, the five stages, decomposition, review loop,
pipeline.

## Scope

1. Turn `flow.py` into a package without changing any function body: `flow/context.py` (`FlowStage`, `StageStatus`,
   `StageResult`, `FlowContext`), `flow/checkpoint.py`, `flow/ledger_reconcile.py`, `flow/git_refs.py`,
   `flow/github.py`, `flow/intent_questions.py`, `flow/stage_conflicts.py`,
   `flow/stages/{intent,plan,decomposition,execute,review,calibrate}.py`, `flow/review_loop.py`, `flow/pipeline.py`.
2. `flow/__init__.py` re-exports every public name that other modules and tests import today, so no caller changes.
3. Prove it is a move: a pytest (or a review-evidence script committed under `scripts/`) compares the `ast.dump` of
   every function and class before and after, keyed by qualified name.
4. Split `tests/test_flow.py` to mirror the new modules (`tests/flow/test_<module>.py`); test count unchanged or higher.
5. Patch targets in tests move to the module that defines the name; no behaviour change.

## Touch set

`apps/sandbox-executor/src/sandbox_executor/flow.py` (deleted), new `flow/` package, `tests/test_flow.py` (split),
`docs/architecture.md` (module map only).

## Dependencies

Blocked by 0185. Unblocks 0189, 0190, 0191, 0193, 0194 and 0197, which can then run in parallel on disjoint modules.

## Notes

- Run through the Holon flow on holon-agentic-coder, **alone**: no other flow PR touching `flow.py` or `test_flow.py`
  may be open (sequential overlapping flows). Sequence with 0158, 0160, 0161, 0179 and 0183, whichever starts first.
- Can run in parallel with 0188 (`cli.py`), because the re-exports keep `cli`'s imports valid.
- Reverses Bean 0152's "decompose before splitting": a move-only diff is mechanically reviewable and is what removes the
  shared file.
