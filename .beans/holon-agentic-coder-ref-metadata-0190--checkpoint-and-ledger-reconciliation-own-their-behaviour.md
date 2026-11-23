---
# holon-agentic-coder-ref-metadata-0190
title:
  "FlowCheckpoint and ledger reconciliation own their behaviour; container entrypoints stop importing the flow engine"
status: completed
type: task
priority: high
tags:
  - refactor
  - ledger
  - architecture
  - holon-agentic-coder
blocked_by:
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-21T18:40:07+11:00
---

## Problem

Spawned by Bean 0177. In `flow.py` (`993b686`) the checkpoint is a data class whose behaviour lives in free functions
(`_migrate_v`, `migrate_checkpoint_data`, `get_default_checkpoint_path`, `save_checkpoint`, `load_checkpoint`), and
ledger reconciliation is seven free functions (`extract_valid_ledger_rows`, `reconcile_ledger_rows`,
`reconcile_jsonl_ledger_conflict`, `reconcile_ledger_content`, `reconcile_ledger_file`, `reconcile_ledgers`,
`_parse_ledger_timestamp`) next to the engine. The container entrypoints import the host engine for them:
`entrypoint/executor.py` imports `sandbox_executor.flow` five times, `planner.py` and `intent_creator.py` import
`check_and_resolve_stage_conflicts`. A container change and a host change therefore meet in the same module.

## Scope

1. `FlowCheckpoint` gains `save`, `load` (classmethod), `migrate` and a path policy; behind a small `CheckpointStore`
   port (file store today) so Bean 0183 can add sandbox-owned storage as an adapter.
2. Reconciliation moves to `ledger/reconcile.py` as a `LedgerReconciler` (pure functions over rows plus a thin file
   shell); `ledger.py` becomes `ledger/` (`rows`, `lock`, `query`, `reconcile`) with re-exports.
3. `check_and_resolve_stage_conflicts` (CC 44) and `failed_partial_head` move to a module both host and entrypoints may
   import (`flow/stage_conflicts.py` is fine if it imports nothing host-only); add a pytest that fails if any
   `entrypoint/` module imports `flow.pipeline`, `flow.stages` or `cli`.
4. Decompose the moved functions to the 0185 limits. Reconciliation stays an exact union preserving existing row order.

## Touch set

`flow/checkpoint.py`, `flow/ledger_reconcile.py`, `flow/stage_conflicts.py`, `ledger.py` -> `ledger/`, import lines in
`entrypoint/{executor,planner,intent_creator,review_loop}.py`, the matching tests.

## Dependencies

Blocked by 0187. Land **0158** (reconciliation reorders `intents.jsonl` rows) first or carry its fix unchanged. Should
precede 0183 (checkpoint storage) and 0196, 0199.

- 2026-10-30: the 0158 prerequisite is satisfied. Bean 0158 is completed (holon-agentic-coder PR #111, pure-append
  ledger writes, merged as `8c9ff4d`); carry that behaviour unchanged. Still blocked by 0187.

## Notes

- Run through the Holon flow on holon-agentic-coder. The ledger layout and the three-ledger invariant are unchanged.

## Audit (2026-11-20)

Blocker Bean 0187 was scrapped; the `flow/` package split it covered landed through PR #147/#163, so this bean is not
blocked by it. Still open: no `CheckpointStore`/`LedgerReconciler`, and the entrypoints still import
`sandbox_executor.flow`.

## Resolution

Delivered via [PR #219](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/219) and merged into `main`
(`df3b0d1`):

- **Key Architectural Deliverables**: `FlowCheckpoint` owns save, load, migrate and its path policy behind a
  `CheckpointStore` port; ledger reconciliation moves into the `ledger/` package as `LedgerReconciler`; container
  entrypoints stop importing the host flow engine for these.
- **Verification & Tests**: consensus 3/3 APPROVED in iterations 13-19. The loop never auto-posted consensus because of
  the stale local test gate (Bean 0354); the approval was posted by hand as a PR comment.
- **Holon Flow Traversal**: Stages 1-4 ran. Plan and execution ran on `antigravity-agent` / `gemini-3.8-flash`. The
  review was resumed on `claude-agent` / `claude-opus-5-5` at the maintainer's request after an antigravity resolver
  defect. Stage 5 was run by hand with `holon calibrate` (report only): predicted EV 66.11, reported actual -9.11. That
  actual is misleading because it reflects the stalled review.
- **Not run**: the Stage 5 reconciliation and knowledge promotion did not run. They are a follow-up under Bean 0355.
