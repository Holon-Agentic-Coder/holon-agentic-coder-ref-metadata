---
# holon-agentic-coder-ref-metadata-0513
title:
  "Stage 5 restore of the starting branch fails on pending ledger rows and withdraws a fresh approval on a
  bookkeeping-only head"
status: todo
type: bug
priority: normal
tags:
  - flow
  - review
  - calibration
  - holon-agentic-coder
created_at: 2026-11-26T11:46:00Z
updated_at: 2026-11-26T11:46:00Z
---

## Evidence

Flow no-unneeded-full-review, parent PR into main (intent-level execution branch
`I-1795665991-no-unneeded-full-review/P-1795666015-CLA-CO5.5/E-1795666317-CLA-CO5.5/_`), Stage 4 approved 3/3 at head
c9fc1fc, then Stage 5 ran:

- `Merged-head CI gate: head 6dd0020e ... not covered by the approval of c9fc1fc: PR-own change changed since approval`.
  The fingerprint moved from pf1:c7206394 to pf1:695a123f, on a head whose only change was ledger rows.
- `Warning: could not restore starting branch ... Your local changes to the following files would be overwritten by checkout: holon-knowledge/ledger/pending/executions/I-1795665991-no-unneeded-full-review.jsonl. Aborting`.
- `Consensus withdrawn` and `restarting Stage 4 at iteration 1 (restart 1 of 3)`, so a fresh 3/3 approval was
  re-reviewed in full.

Two defects:

1. The checkout back to the starting branch in Stage 5 is not preceded by committing or clearing the pending ledger
   file, so the restore aborts and leaves the worktree on the wrong ref with uncommitted ledger rows carried over.
2. Bookkeeping ledger rows written after approval change the PR-own fingerprint, so the approval is withdrawn for a
   change that is not reviewable. This is the same class as bean 0494 and goal 1 of bean 0407.

## Goal

- Stage 5 always commits or stashes its own ledger rows before switching branches, and fails loudly if restore is needed
  and not possible.
- The approval fingerprint excludes ledger and pending bookkeeping paths, so an approval survives ledger-only commits
  (see bean 0407, goal 1).
