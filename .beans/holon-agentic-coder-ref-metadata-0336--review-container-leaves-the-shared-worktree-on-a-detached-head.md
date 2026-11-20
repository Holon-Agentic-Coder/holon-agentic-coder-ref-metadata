---
# holon-agentic-coder-ref-metadata-0336
title: "A Stage 4 review container left the shared flow worktree on a detached HEAD, so the resolver refused to run"
status: completed
type: bug
priority: normal
tags:
  - flow
  - stage-4
  - review-loop
  - worktree
  - holon-agentic-coder
created_at: 2026-11-20T11:30:00+11:00
updated_at: 2026-11-20T18:45:15+11:00
---

## Problem

Seen on the `shortref` flow (Bean 0321, PR #206), 2026-11-19 23:54:54 UTC. During Stage 4 the host worktree
`flow-shortref` was left on a detached HEAD at `b043b35b` while only the review container had it mounted. The resolver
then refused to run. The command that detached it was not identified. The flow went on only after the execution branch
was re-attached by hand, keeping the uncommitted review ledger rows, and the flow was resumed from `review`.

## Action

Through the Holon flow on `holon-agentic-coder`: find which review-stage step checks out a commit in the mounted
worktree (reviewer checkout, CI evidence or diff collection) and make it work on a separate worktree or a
`git show`/`git diff` read instead. The review stage restores the branch on exit and the resolver re-attaches it when
the HEAD is detached at the branch tip, rather than refusing. Add a hermetic test that runs a review iteration and
asserts the worktree is on the execution branch afterwards.

## Notes

- Log: `todo/flow-shortref-resume6.log`.

## Progress

- 2026-11-20: Holon flow `review-keeps-worktree-on-branch` started (claude-agent, claude-opus-5-5) in worktree
  `flow-review-keeps-worktree-on-branch`; log `todo/flow-review-keeps-worktree-on-branch.log`.
- 2026-11-20: Flow completed all 5 stages. Stage 3 waited out overlaps (PR #210, then local flow
  `refresh-plan-after-overlap-wait`) and was admitted on its own with a refreshed plan. Stage 4 reached 3/3 consensus at
  iteration 3. PR #212 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/212) is OPEN, MERGEABLE/CLEAN,
  all checks green, calibration report in the diff; EV predicted 55.50, actual 71.68 (+16.18). Awaiting human merge.

## Resolution

Delivered via [PR #212](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/212) and merged into `main`
(`b6e46e0b`):

- **Key Architectural Deliverables**: new `worktree_head.py` with `reattach_branch`/`restore_branch`, wired into
  `flow/stages/review.py` and `entrypoint/review_loop.py`. The review stage restores the execution branch on exit, and a
  HEAD detached at the branch tip is re-attached instead of refused.
- **Verification & Tests**: hermetic tests `test_review_keeps_branch.py`, `test_review_loop_worktree_head.py` and
  `test_worktree_head.py` assert the worktree is on the execution branch after a review iteration.
- **Holon Flow Traversal**: all 5 stages completed (flow `review-keeps-worktree-on-branch`). Stage 3 waited out overlaps
  (PR #210, then `refresh-plan-after-overlap-wait`) and was admitted on a refreshed plan; Stage 4 reached 3/3 consensus
  at iteration 3; calibration EV 55.50 -> 71.68. First flow whose plan branch was refreshed onto `main` after an overlap
  wait, with no merge conflict.
