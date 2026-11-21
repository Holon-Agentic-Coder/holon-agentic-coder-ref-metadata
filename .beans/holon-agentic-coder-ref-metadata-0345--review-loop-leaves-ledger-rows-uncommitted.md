---
# holon-agentic-coder-ref-metadata-0345
title: "The review loop leaves executions ledger rows uncommitted in the flow worktree"
status: completed
type: bug
priority: normal
tags:
  - flow
  - stage-4
  - review-loop
  - ledger
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-21T11:58:32+11:00
---

## Problem

On 2026-11-20 the `promoted-count-this-run-only` flow (PR #216) reached a Stage 4 merge conflict with 56 review-loop
rows written to `holon-knowledge/ledger/executions.jsonl` in the flow worktree but never committed. The subagent had to
set them aside, merge `origin/main`, and append them back by hand. The same pattern appeared earlier on the `shortref`
flow (PR #206), where uncommitted review ledger rows had to be kept by hand while re-attaching the branch. Rows that are
not committed are lost if the worktree is reset or removed, block a clean merge, and only reach the PR when someone
handles them.

## Action

Through the Holon flow on `holon-agentic-coder`:

- The review loop commits the ledger rows it writes at the end of each iteration (one commit per iteration, ledger files
  only, no co-author trailer) and pushes with the iteration's other changes, so the worktree is clean between
  iterations.
- Before a merge with the target branch (the conflict gate) and before Stage 5, any pending ledger rows are committed
  first.
- A stage exit (success, halt or failure) never leaves ledger files modified in the worktree.
- Hermetic tests: after a review iteration the worktree is clean and the rows are in the last commit; a conflict merge
  starts from a clean tree; a failed iteration still commits its rows.

## Notes

- Keep exactly the three ledgers; rows are append-only.
- Related: Bean 0336 (review keeps the worktree on its branch), Bean 0213 (conflict gate in the review loop).

## Progress

- 2026-11-21: started; flow `review-commits-ledger-rows` launched (claude-agent, claude-opus-5-5).
- 2026-11-21: flow done; PR #224 approved 3/3 at iteration 5, calibrated (EV 63.70 predicted, -7.11 actual), CLEAN and
  mergeable; awaiting human merge.

## Resolution

Delivered via [PR #224](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/224) and merged into `main`
(`c38a883`):

- The review loop now commits its executions ledger rows each iteration, and again before the conflict merge and before
  Stage 5, so no review ledger row stays uncommitted in the flow worktree.
- New modules `review/ledger_commit.py` (commits the pending ledger rows) and `review/git_identity.py` (commit identity
  for those commits).
- The PR's own calibration (predicted EV 63.70, reported actual -7.11) is known wrong. Calibration read the ledger at
  the reviewed commit `95a45bc`. That commit held the earlier 'failed' review summary row (committed by hand before a
  conflict merge) but not the final approved row, which was still uncommitted. This PR's change closes that gap.
- Review approved 3/3 at iteration 5; hermetic tests cover the ledger commits, the conflict gate and the review loop.
