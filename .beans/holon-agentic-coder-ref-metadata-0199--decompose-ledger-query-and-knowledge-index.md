---
# holon-agentic-coder-ref-metadata-0199
title: "Decompose ledger query and the knowledge index (query_ledger, sync_ledger_incremental, action promotion)"
status: completed
type: task
priority: low
tags:
  - refactor
  - complexity
  - ledger
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0190
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-21T09:19:00Z
---

## Problem

Spawned by Bean 0177. Measured on `993b686`: `ledger.query_ledger` CC **53**, `ledger.parse_commit_trailers` CC 24,
`knowledge/index.sync_ledger_incremental` 196 lines CC 48, `knowledge/promotion.evaluate_action_promotion` 178 lines CC
28, `knowledge/consult.ConsultEngine.consult_records` CC 25. `ledger` has fan-in 9 and `knowledge` 10, so these are
widely shared.

## Scope

1. `LedgerQuery` built from composable filters (one small predicate per CLI filter) instead of one 53-branch function.
2. `sync_ledger_incremental` split into read-new-rows / index-rows / persist-watermark steps; promotion rules as a
   table.
3. All functions within the 0185 limits; query output unchanged on the real ledgers (`holon-knowledge/ledger/*.jsonl`).

## Touch set

`ledger/query.py` (after 0190), `knowledge/{index,promotion,consult}.py`, `tests/test_ledger_query.py`,
`tests/test_knowledge.py`.

## Dependencies

Blocked by 0190. Sequence with 0150 (knowledge index tests).

## Notes

- Run through the Holon flow on holon-agentic-coder.

## Audit (2026-11-21)

Still blocked by Bean 0190. Open PR #219 turns `ledger.py` into a `ledger/` package (`lock`, `query`, `reconcile`,
`rows`), so `ledger/query.py` is the target once it merges; `knowledge/{index,promotion,consult}.py` are unchanged.

## Progress

- 2026-11-21: Holon flow `ledger-query-knowledge-index` started (claude-agent, claude-opus-5-5).
- 2026-11-21: Flow completed; PR #227 approved 3/3 at iteration 1, calibrated (EV 37.20 -> 57.92), CI green,
  CLEAN/MERGEABLE; awaiting human merge.

## Resolution

- Delivered via [PR #227](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/227) and merged into `main`
  (`43d278cb`).
- Key deliverables: decomposition of `LedgerQuery` (`ledger/query.py`) and knowledge index/promotion/consult
  (`knowledge/{index,promotion,consult}.py`).
- Full 5-stage Holon flow traversal
  (`I-1795246929-ledger-query-knowledge-index/P-1795246947-CLA-CO5.5/E-1795247254-CLA-CO5.5/_`), 3/3 reviewer consensus
  approval at iteration 1, `11/11` passing CI checks, and calibration report
  (`plans/I-1795246929-ledger-query-knowledge-index/P-1795246947-CLA-CO5.5_calibration.md`; EV 37.20 predicted vs. 57.92
  actual).
