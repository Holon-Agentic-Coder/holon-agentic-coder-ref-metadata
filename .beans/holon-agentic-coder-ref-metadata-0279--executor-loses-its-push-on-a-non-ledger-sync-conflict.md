---
# holon-agentic-coder-ref-metadata-0279
title: "Executor loses its push when syncing with `origin/main` hits a non-ledger conflict"
status: completed
type: bug
priority: high
tags:
  - flow
  - executor
  - resume
  - holon-agentic-coder
created_at: 2026-11-12T09:00:00Z
updated_at: 2026-11-13T00:00:00Z
---

## Problem

Before pushing, the executor merges `origin/main`; on a non-ledger conflict it aborts, commits a "record sync failure"
row and refuses to push ("Pre-push sync failed: Non-ledger merge conflicts detected"). The work then exists only in the
flow worktree: no execution branch on `origin`, and the checkpoint records `execute` as failed with
`execution_branch: null`, so `--from-stage review` fails ("Cannot run Review stage without an active execution_branch").
Seen 2026-11-11/12 with the flows for Beans 0274 and 0275 after PR #163 deleted a file they modified; recovered by hand
(merge `origin/main`, resolve, push, edit the checkpoint).

## Action

Run through the Holon flow. When the sync conflict is non-ledger, still push the executor's own commits (it is a
fast-forward of the plan branch) and record the conflict as a resumable state with the execution branch in the
checkpoint, so the flow can continue from review or hand the conflict to a resolver. Hermetic tests with a fixture
repository.

## Resolution (completed, 2026-11-13)

Delivered by flow `keeppush` as holon-agentic-coder PR #180, merged 2026-11-12T23:50:58Z (merge commit `583a230`, review
`PRR_kwDORMmd1c8AAAABXqzKHQ`). Calibration report
`plans/P-1794523636-de5c2107-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
+16.67 (actual 62.26). The executor's stray `uv.lock` edit did not reach the PR diff. The first two launches failed in
planning and execution because the installed CLI and images predated the id-collision fix (see Bean 0278); a rebuild
fixed it.
