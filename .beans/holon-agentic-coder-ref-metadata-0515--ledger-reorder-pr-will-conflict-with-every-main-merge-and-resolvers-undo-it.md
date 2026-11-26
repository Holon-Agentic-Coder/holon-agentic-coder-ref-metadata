---
# holon-agentic-coder-ref-metadata-0515
title: "Ledger reorder (0436) conflicts with every merge to main and the resolvers keep main order, silently undoing it"
status: todo
type: bug
priority: high
tags:
  - ledger
  - flow
  - conflicts
  - holon-agentic-coder
created_at: 2026-11-26T12:20:00Z
updated_at: 2026-11-26T12:20:00Z
---

## Evidence

Self-improvement audit 2026-11-26T12:20Z, question (4). Bean 0436's flow `ledgers-sorted-chronologically` started at
12:04Z (Stage 3 admitted at 12:11:26Z, "overlaps no flow in flight", 5 other flows in flight: ci-final-head,
fetch-execution-branch-retry, no-unneeded-full-review, plan-id-unique, settings-token-off-argv).

- The change rewrites every row of the three canonical ledgers. Every merge to `main` appends to
  `holon-knowledge/ledger/executions.jsonl` (#339, #338, #337 each changed it in the last 2 minutes), so the reorder PR
  conflicts on its first merge-in after any other PR lands; with the maintainer's merge cadence (4 merges in 80 s at
  12:04Z) it will conflict several times during review.
- Stage 3 admission excludes engine-owned ledger paths, so no other flow waits for it and it waits for none.
- The resolvers (`resolve_known.py`, `flow/ledger_reconcile.py`) now keep main's file byte for byte and append the
  branch's new rows. Applied to the reorder PR that discards the reordering and leaves a PR that looks resolved but
  changes nothing, and the review passes an empty or partial normalisation. A flow-owned reorder is also not rerun by
  any step after a conflict.

## Proposed fix

- Make normalisation re-runnable: the reorder PR carries the script (goal 1 of 0436) and the conflict step for that one
  PR re-runs it on the merged ledgers instead of keeping main's text; a hygiene check (goal 2) fails the PR if a ledger
  is out of order at the final head.
- Do not start the flow while other PRs are about to merge; land it when no PR is open (goal 3 of 0436 says so, but
  nothing enforces it). The main agent holds the other pickers until it merges, or merges it first in a burst.
- Add a final-head check that "rows(main) subset-of rows(PR) and the file is sorted" so a silent undo fails Stage 4.

## Expected gain

Avoids a review loop that approves an undone sort, and repeated conflict rounds (each about 5 to 15 min, plus a full
re-review under 0513). Cost: one re-run hook in the conflict step and one check.

## Notes

Related: 0436, 0371, 0513, 0494. Do not edit 0436's scope; this bean only adds the landing risk.
