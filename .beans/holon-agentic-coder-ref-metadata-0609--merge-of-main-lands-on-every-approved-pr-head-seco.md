---
# holon-agentic-coder-ref-metadata-0609
title: "Merge of main lands on every approved PR head seconds before the human merge"
status: todo
type: task
priority: normal
tags:
  - holon-flow
  - pr-merging
created_at: 2026-11-27T04:43:40Z
updated_at: 2026-11-27T04:43:40Z
---

## Evidence (audit 2026-11-27T04:43Z)

- All ten merges of the window (#396, #393, #392, #390, #389, #385, #384, #382, #383, #380) landed on a head that was a
  "Merge branch 'main'" commit made after the last review: merge commit to PR merge 26 s (#392, 04:34:30Z to 04:34:56Z),
  #396 04:33:13Z to 04:33:40Z; the last review of each was 0.7 to 2 h earlier (#392 03:33:47Z, #380 02:37:28Z). Every
  merge moved main and so forced the next PR's merge-from-main.
- Bean 0372 (approval survives a merge of main) covers carrying the vote over; bean 0602 covers showing CI per head.
  Neither records, at merge, that the merged head's own diff equals the approved head's own diff, and CI on the new head
  cannot finish in 26 s.

## Goal

The merge-readiness report gives, per PR: approved head, head to merge, whether the PR's own diff (against the merge
base) is identical, and the CI state of the head to merge. A head with a changed own diff or a pending CI is flagged, so
the maintainer merges only after seeing it.

## Acceptance

- [ ] Report row shows approved sha, merge sha and own-diff identical yes or no.
- [ ] Test covers a main-only merge (identical) and a resolver code push (not identical).

## Notes

## Resolution
