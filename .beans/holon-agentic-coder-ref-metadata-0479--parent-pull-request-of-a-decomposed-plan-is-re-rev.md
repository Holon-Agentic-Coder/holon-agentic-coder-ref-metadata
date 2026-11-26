---
# holon-agentic-coder-ref-metadata-0479
title: "Parent pull request of a decomposed plan is re-reviewed in full after every child was approved"
status: todo
type: feature
priority: normal
tags:
  - flow
  - stage-4
  - review
  - decomposition
  - holon-agentic-coder
created_at: 2026-11-26T05:25:00Z
updated_at: 2026-11-26T05:25:00Z
---

## Problem

When a plan is decomposed, each child flow is reviewed, approved and merged into the parent plan branch. The parent's
own pull request into `main` then runs a full three-reviewer review of the union of all children's changes, which
reviewers have already approved child by child.

## Evidence

Evidence: flow time audit of 2026-11-26 (git-ignored `todo/flow-time-audit-2026-11-26.md`, scripts and data in
`todo/flow-time-audit-2026-11-26/`), sample PRs #296 to #316 of holon-agentic-coder.

- Bean 0371 (`ledger-fragments-and-promotion`): children #310, #311, #312, #313 (76, 117, 41 and 23 files) were each
  approved; parent #314 changed 218 files, of which 209 were already in a child PR. Only 2 code files were new to the
  parent (`flow/conflict_classes_resolve.py` and its test, the integration fix), plus knowledge-base records and the
  parent plan and calibration report.
- Parent review: 2026-11-26 03:36:58 PR created, iteration 1 (reviewers 4.5 min, host `review_local` 2.3 min, resolver
  4.5 min), iteration 2 approving (9.9 min, CI-bound): 21.7 min, plus a pipeline on the 218-file diff.
- Iteration 1 did raise three Important findings, so an integration pass has value; the cost is re-reading the
  already-approved child diffs with three reviewers.

## Proposed change

1. The parent review is scoped to what no child review covered: the integration delta (the parent head against the merge
   of the approved child heads), the parent plan and calibration report, and cross-child consistency.
2. Children's approvals are recorded on the parent (fingerprints of their own diffs, as Bean 0407 keys approvals), and a
   parent diff equal to the union of approved child diffs plus bookkeeping needs one reviewer, not three.
3. Keep the full pipeline on the parent head (the CI gate is unchanged).

## Expected gain

About 10 to 15 min per decomposed flow (one scoped iteration instead of a full one, and fewer findings to resolve),
growing with the number of children.

## Cost

Medium: approval carry-over from children to parent in the review loop; tests with a decomposed fixture.

## Notes

- Related: Bean 0407 (approval keyed to the reviewable diff; its first child is PR #316), Bean 0446 (admission of split
  parents), Bean 0474 (parent integration rejects append-only ledger merge, 5.5 min lost in the same parent run).
