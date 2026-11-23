---
# holon-agentic-coder-ref-metadata-0339
title: "Calibration scores an approved flow as failed when Stage 3 recorded a sync conflict that was later resolved"
status: completed
type: bug
priority: high
tags:
  - flow
  - calibration
  - ledger
  - holon-agentic-coder
created_at: 2026-11-20T18:05:00+11:00
updated_at: 2026-11-20T19:25:00+11:00
---

## Problem

PR #211 (`refresh-plan-after-overlap-wait`, 2026-11-20) has 3/3 approval and green CI, yet calibration recorded actual
P(success) 0.00 and impact 0.00, so actual EV -18.21 against 44.16 predicted. Confirmed cause, from the flow's
`executions.jsonl` summary rows for plan `…/P-1795154100-CLA-CO5.5/_`:

| created_at | status             | ledger_revision |
| ---------- | ------------------ | --------------- |
| 06:24:05   | `success`          | 1               |
| 06:36:07   | `sync_conflict`    | 2               |
| 06:52:16Z  | `halted_for_human` | (absent → 1)    |

`evaluate_dual_ev_outcomes` (`calibration_ev.py`) sorts the matching rows by `(ledger_revision, created_at)` and takes
the last as the final outcome. Stage 3's `sync_conflict` row carries `ledger_revision: 2`; Stage 4's `halted_for_human`
consensus row carries none and defaults to 1, so the earlier conflict row outranks the later approval. It is not
converged, so `p_clean` and the impact drop to 0. `has_failure` also counts the resolved `sync_conflict` row as a
failure, zeroing the observed EV as well.

The same pattern fits the other negative calibrations today: `resumetip` (PR #208, 39.61 → -19.01) and `blockedflow` (PR
#209, 35.30 → -22.11) both stopped on a sync conflict before review, while `planner-api-error-not-a-plan` (PR #210) had
none and scored 53.40 → 73.52. The calibration record has been systematically wrong for every flow that hit a merge
conflict, which also corrupts the planner's EV feedback.

## Action

Through the Holon flow on `holon-agentic-coder`:

- The final outcome is the latest summary row in flow order: every summary row the flow writes (Stage 3 and Stage 4
  alike) carries a consistent `ledger_revision`, or the selection orders by `created_at` when revisions are not
  comparable. A Stage 4 consensus row after a Stage 3 `sync_conflict` row is the final outcome.
- A `sync_conflict` that a later row supersedes (the branch was merged and review converged) is not a failure for the
  observed EV; an unresolved one still is.
- Normalise `created_at` to one format (`+00:00` vs `Z` are both written today).
- Hermetic tests: `success` → `sync_conflict` → `halted_for_human` scores as converged with full impact; an unresolved
  `sync_conflict` as the last row scores as failed; the observed EV is not zeroed by a superseded conflict.
- Do not rewrite the append-only ledgers; past calibration reports stay as written.

## Notes

- Related: Bean 0338 (refreshing the plan branch removes most of these conflicts at the source), Bean 0264.

## Progress

- 2026-11-20 18:53 (+11:00): Holon flow started (`calibration-final-row-by-time`, claude-agent / claude-opus-5-5) in
  worktree `flow-calibration-final-row-by-time`.
- 2026-11-20 19:22 (+11:00): All 5 stages done. PR #213
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/213) 3/3 approved at review iteration 2 (iteration 1
  docs CHANGES resolved: `docs/ledger_schema.md`), EV predicted 52.10 / actual 63.28 (+11.18), calibration report in PR
  diff, MERGEABLE/CLEAN, all checks green. New module `calibration_outcome.py` (outside the flow package; first
  execution re-planned once to widen the touch set); `flow_module_budgets.json` untouched. Awaiting human merge.

## Resolution

Delivered via [PR #213](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/213) and merged into `main`
(`a450005`):

- **Key Architectural Deliverables**: calibration orders a flow's summary rows by parsed `created_at` (`+00:00` and `Z`
  both accepted), with `ledger_revision` only as a tie-break, so the Stage 4 consensus row after a Stage 3
  `sync_conflict` row is the final outcome. A `sync_conflict` that a later row supersedes no longer counts as a failure
  for the observed EV; an unresolved one still does. The selection lives in a new `calibration_outcome.py` outside the
  flow package. `flow_module_budgets.json` is untouched. Append-only ledgers were not rewritten.
- **Verification & Tests**: hermetic tests in `test_calibration_ev.py` cover `success` → `sync_conflict` →
  `halted_for_human` scoring as converged with full impact, an unresolved `sync_conflict` as the last row scoring as
  failed, and a superseded conflict not zeroing the observed EV.
- **Holon Flow Traversal**: all 5 stages completed (Intent → Plan → Execute → Review Loop → Calibration). Review
  approved 3/3 at iteration 2. Calibration: expected value predicted 52.10, actual 63.28 (delta +11.18).
