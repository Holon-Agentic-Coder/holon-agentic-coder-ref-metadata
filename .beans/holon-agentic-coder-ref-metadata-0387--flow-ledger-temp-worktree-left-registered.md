---
# holon-agentic-coder-ref-metadata-0387
title: "The flow leaves a detached temp ledger worktree registered in the repository"
status: completed
type: bug
priority: low
tags:
  - flow
  - git
  - cleanup
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T11:34:00Z
---

## Problem

`git worktree list` in `holon-agentic-coder` shows a detached worktree under the system temp directory,
`…/T/holon-flow-ledger-w_4qqobl/worktree` (`71b0befa`), left by a flow's ledger step (`flow/git_refs.py`:
`git worktree add --detach` for a ledger commit). It was there all day on 2026-11-23, outlived the flow that made it,
and every cleanup agent had to decide whether it was safe to touch.

## Goal

- The ledger step removes its temp worktree in a `finally` (and runs `git worktree prune` for an entry whose directory
  is gone), including when the step fails or the host is killed and the next run starts.
- A test kills the step midway and asserts the next run leaves no `holon-flow-ledger-*` worktree registered.

## Progress (2026-11-24)

- Flow started from this Claude Code session: intent `todo/intent-0387-ledger-temp-worktree-cleanup.json`, slug
  `ledger-temp-worktree-cleanup`, `claude-agent` / `claude-fable-5-2`, worktree `flow-ledger-temp-worktree-cleanup`.

## Resolution

Delivered via [PR #270](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/270) and merged into `main`
(`bfbd9f4`) on 2026-11-24:

- **Key Architectural Deliverables**: the ledger step now removes its temporary `holon-flow-ledger-*` worktree in a
  `finally` (including when the step raises or returns an error); a new `flow/ledger_worktree.py` runs
  `git worktree prune` and clears stale leftover ledger worktrees (no live owner) at the start of each step.
- **Verification & Tests**: `apps/sandbox-executor/tests/flow/test_ledger_worktree_cleanup.py` covers a step killed by
  `SIGKILL` midway and during `git worktree add`, asserting the next run leaves no `holon-flow-ledger-*` worktree
  registered.
- **Holon Flow Traversal**: the flow completed intent, plan, execute and review; the PR was merged through the merge
  queue while the calibrate stage was re-running.
