---
# holon-agentic-coder-ref-metadata-0336
title: "A Stage 4 review container left the shared flow worktree on a detached HEAD, so the resolver refused to run"
status: todo
type: bug
priority: normal
tags:
  - flow
  - stage-4
  - review-loop
  - worktree
  - holon-agentic-coder
created_at: 2026-11-20T11:30:00+11:00
updated_at: 2026-11-20T11:30:00+11:00
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
