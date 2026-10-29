---
# holon-agentic-coder-ref-metadata-0195
title: "Route the executor entrypoint's raw git subprocess calls through a GitRepository adapter"
status: todo
type: task
priority: high
tags:
  - refactor
  - ports-and-adapters
  - git
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0185
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `entrypoint/executor.py` (`993b686`, 2,270 lines) contains **81** raw `git` subprocess call sites
(`["git", ...]`) although `sandbox_executor/git.py` (285 lines: `run_git`, `resolve_ref`, `branch_exists`,
`changed_paths`, `has_effective_diff`) exists. `_repair_git_repo` (CC 24) and `sync_and_reconcile_pre_push` (CC 28) mix
git plumbing with policy. Tests for it (`test_executor.py`, 5,088 lines) patch `subprocess` directly.

## Scope

1. Grow `git.py` into a `GitRepository` class (repo path bound once) with intention-revealing methods (`current_branch`,
   `commit_all`, `push`, `fetch`, `merge_base`, `rebase_onto`, `is_clean`), keeping the existing functions as delegating
   wrappers until callers move.
2. Replace every raw `git` call in `entrypoint/executor.py` with adapter calls; no other behaviour change.
3. A pytest asserts no `subprocess` call with a literal `"git"` remains in `entrypoint/executor.py` (extend to other
   modules later).
4. An in-memory or temp-repo `GitRepository` fake for the executor tests where it removes `subprocess` patches.

## Touch set

`sandbox_executor/git.py`, `entrypoint/executor.py` (call sites only), `tests/test_git.py`, `tests/test_executor.py`.

## Dependencies

Blocked by 0185. Blocks 0196. Parallel-safe with 0187 and 0188.

## Notes

- Run through the Holon flow on holon-agentic-coder. Also groundwork for 0183 (engine git checks in a sandboxed clone).
