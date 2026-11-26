---
# holon-agentic-coder-ref-metadata-0551
title: "Flow review stage drops uncommitted edits left in the flow worktree"
status: todo
type: bug
priority: normal
tags:
  - flow
  - review-loop
  - worktree
  - holon-agentic-coder
created_at: 2026-11-27T00:00:00Z
updated_at: 2026-11-27T00:00:00Z
---

## Problem

Bean 0532 (secret-bundle-private-files, PR #356) was halted with one uncommitted edit in the flow worktree
(`apps/sandbox-executor/src/sandbox_executor/agent_runner.py`: move `os.fchmod` inside the `try`). The log said
"uncommitted changes remain in the worktree after Stage 5; they are carried over". Resumed from checkpoint with
`--from-stage review` after merging origin/main (clean merge, edit kept). The resumed run approved 3/3 and calibrated,
but the worktree was clean at the end and HEAD (ad02a02f) still has the original `fchmod` placement. The edit was
silently discarded by the flow, not committed. A backup patch was saved to the scratchpad before the resume.

## Expected

Uncommitted edits in the flow worktree are either committed as a flow row, refused up front, or preserved; never
silently dropped.

## Follow-up

Decide with the maintainer whether the reordered `fchmod` is still wanted on PR #356 (it would change the approved head
and need a fresh review). Backup patch: flow-secret-bundle-private-files-uncommitted-0532.patch in the scratchpad.
