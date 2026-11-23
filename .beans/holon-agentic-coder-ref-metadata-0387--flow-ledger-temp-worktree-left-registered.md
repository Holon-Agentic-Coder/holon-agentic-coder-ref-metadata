---
# holon-agentic-coder-ref-metadata-0387
title: "The flow leaves a detached temp ledger worktree registered in the repository"
status: todo
type: bug
priority: low
tags:
  - flow
  - git
  - cleanup
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-23T12:40:00Z
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
