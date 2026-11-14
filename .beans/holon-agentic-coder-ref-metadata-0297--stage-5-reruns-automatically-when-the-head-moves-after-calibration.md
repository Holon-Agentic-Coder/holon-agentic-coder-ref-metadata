---
# holon-agentic-coder-ref-metadata-0297
title: "Stage 5 reruns automatically when the pull request head moves after calibration"
status: todo
type: bug
priority: high
tags:
  - stage-5
  - calibration
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-14T01:00:00Z
updated_at: 2026-11-14T01:00:00Z
---

## Problem

A calibration report covers exactly one head. When the pull request branch moves after Stage 5 (a conflict merge with
`main`, a resolver push, a review-loop re-run), the report no longer covers the head that merges, and nothing reruns
Stage 5 or flags the report as stale. Bean 0296 only makes a rerun rebuild its stale `calibrated` branch; it does not
cause the rerun.

Seen on holon-agentic-coder PR #193: the flow calibrated head `cb55140`, a conflict merge and resolver fixes moved the
head to `0e183d8`, the second review loop never reached a clean approval (Stage 5 only runs after one posts), and the
pull request merged with a report for `cb55140`. PR #190 hit the same drift.

## Goal

1. Stage 5 is the final step for the head that merges: whenever the pull request head differs from the head the
   calibration report names, Stage 5 reruns automatically, with no human step. The trigger covers a conflict merge, a
   resolver push and a review-loop re-run, whether the move happens inside the flow or outside it.
2. A rerun rebuilds the `calibrated` branch (Bean 0296), appends its report and ledger rows, and fast-forwards them into
   the pull request branch, so the report names the final head.
3. While the report is stale (the pull request head is not the head it names), the pull request carries a visible stale
   signal and the flow's report-back says so, instead of reading "calibrated, ready to merge".
4. A rerun is idempotent: it adds no duplicate ledger rows when the head has not moved, and it never loops: a
   calibration commit does not by itself count as a head move.
5. Hermetic tests: a head move after calibration triggers a rerun; an unmoved head does not; the rerun's report names
   the new head; the stale signal appears while the report is behind and clears after the rerun.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths.
- Related: Bean 0296 (rebuilds a stale `calibrated` branch), Beans 0253 and 0292 (Stage 5 sync, final-head CI check) and
  Bean 0182 (the event watcher could supply the head-moved trigger).
- Design question for the planner: where the trigger lives (the flow's report-back, the review loop's pre-posting gate,
  or the watcher's `head_moved` event), and what a head move counts as when calibration commits themselves land on the
  branch.
- Merging stays with the human maintainer; this bean makes the report current when they merge, it does not merge.
