---
# holon-agentic-coder-ref-metadata-0195
title: "Route the executor entrypoint's raw git subprocess calls through a GitRepository adapter"
status: completed
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
updated_at: 2026-11-08T22:04:38Z
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

## Resolution

Delivered via [PR #144](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/144) and merged into `main`
(`cc2ed3e`):

- **Key Architectural Deliverables**: Implemented the `GitRepository` adapter class in
  `apps/sandbox-executor/src/sandbox_executor/git.py` with intention-revealing methods (`run`, `current_branch`,
  `rev_parse`, `status_porcelain`, `is_clean`, `add`, `commit`, `push`, `fetch`, `checkout`, `merge_base`,
  `rebase_onto`, `config`, `reset`, `clean`) while preserving existing module-level wrappers; routed all git invocations
  in `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` through `GitRepository` without growing
  `executor.py` or adding inline `# noqa` suppressions.
- **Verification & Tests**: Added unit tests in `apps/sandbox-executor/tests/test_git.py` covering `GitRepository`
  methods and an AST/source check asserting no raw `["git", ...]` call literals remain in `entrypoint/executor.py`
  outside the low-level command runner.
- **Holon Flow Traversal**: All 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed in an
  isolated worktree (`task-0195-executor-git-adapter`) with unanimous 3/3 consensus approval on iteration 1 (0 findings,
  11/11 CI checks passed) and Stage 5 calibration included in the PR diff (EV predicted: 75.21, actual: 82.31,
  $\Delta\text{EV} = +7.10$).
