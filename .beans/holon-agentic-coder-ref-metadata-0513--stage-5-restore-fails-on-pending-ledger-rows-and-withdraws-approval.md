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

## Cost (audit 2026-11-26T12:20Z)

The decomposed 0407 flow (04:06Z to at least 11:43Z, PR #334) per child, from `todo/flow-no-unneeded-full-review.log`:
child 1 04:12 to 04:58 (46 min; 1 Stage 3 escape 15.6 min; 2 review iterations), child 2 04:59 to 06:22 (84; escape
11.8; 4 iterations, review 57 min), child 3 06:23 to 07:43 (80; escape 26.0; 4 iterations, 38 min), child 4 07:44 to
09:15 (91; 6 iterations, 62 min), child 5 09:15 to 10:42 (87; escape 13.3; 5 iterations, 64 min), parent 10:43 to 11:29
(4 iterations, 46 min) then the withdrawn approval restarted Stage 4 at 11:29:45Z and iteration 2 was still blocked at
11:42Z. Review loops were about 284 of the first 7.4 h (21 child iterations plus 4 parent), Stage 3 discards about 80
min with re-plans, and this withdrawal restarted a full review for a ledger-only head. Step times for pre-flight, pushes
and merge-ins are not measured (0412).

## Goal

- Stage 5 always commits or stashes its own ledger rows before switching branches, and fails loudly if restore is needed
  and not possible.
- The approval fingerprint excludes ledger and pending bookkeeping paths, so an approval survives ledger-only commits
  (see bean 0407, goal 1).
