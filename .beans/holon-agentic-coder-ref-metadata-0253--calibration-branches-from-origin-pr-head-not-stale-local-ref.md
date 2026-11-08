---
# holon-agentic-coder-ref-metadata-0253
title: "Stage 5 calibration branches from the origin PR head, not a stale local execution ref"
status: todo
type: bug
priority: high
tags:
  - stage-5
  - calibration
  - git
  - holon-agentic-coder
created_at: 2026-11-09T00:30:00Z
updated_at: 2026-11-09T00:30:00Z
---

## Problem

During the PR #143 flow (Bean 0241), Stage 5 created `I-1794136091-.../P-1794136106-.../E-1794141703-.../calibrated`
from the **local** execution branch in the host target worktree (`apps/holon-agentic-coder/main`), which was well behind
`origin`. Since that local ref was last updated, the PR head on `origin` had gained:

- two `merge origin/main` ledger-interleave commits (for PRs #142 and #144 landing on `main`), and
- two resolver commits (`fix(review): resolve findings FIND-CI-008 (iteration 8)`).

Those commits were pushed by containers and by out-of-band conflict resolution, so they never reached the host's local
branch. As a result:

1. The `/calibrated` branch did not descend from the PR head, so the Step 4 `git merge --ff-only <E>/calibrated` failed
   (`fatal: Not possible to fast-forward`).
2. Including the calibration report in the PR needed a real merge with a hand-resolved `executions.jsonl` conflict.
3. The calibration itself analysed a stale tree and ledger: it did not see the final resolver commits or the merged
   ledger entries it was meant to reconcile.

The flow also left the host worktree checked out on the execution branch afterwards, so post-merge sync first had to
check out `main` again (seen on both the PR #141 and PR #143 runs).

## Goal

1. **Sync before calibrating**: Before Stage 5 reads or branches anything, `git fetch origin` and base `/calibrated` on
   `origin/<execution_branch>/_` (or hard-sync the local execution ref to it when the worktree is clean), so calibration
   analyses exactly the reviewed and approved PR head.
2. **Fail loudly on divergence**: If the local execution ref has commits that are not on `origin`, stop with an
   actionable error instead of silently branching from it.
3. **Fast-forwardable result**: Guarantee that `/calibrated` fast-forwards onto `.../_`, so the calibration report can
   be included in the PR without a merge commit or conflict resolution.
4. **Restore the worktree**: After the flow finishes, return the host target worktree to the branch it was on when the
   flow started (normally `main`), leaving no flow branch checked out and no uncommitted ledger changes.
5. **Tests**: Add hermetic tests in which `origin/<E>/_` is ahead of the local ref, asserting that `/calibrated`
   descends from the origin head, fast-forwards onto it, and the worktree is restored afterwards.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Touches Stage 5 calibration and flow wrap-up in `flow.py`, so run it sequentially with other `flow.py` beans.
