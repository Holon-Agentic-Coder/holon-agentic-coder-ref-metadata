---
# holon-agentic-coder-ref-metadata-0339
title: "Calibration scores an approved flow as failed when Stage 3 recorded a sync conflict that was later resolved"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - calibration
  - ledger
  - holon-agentic-coder
created_at: 2026-11-20T18:05:00+11:00
updated_at: 2026-11-20T18:05:00+11:00
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
