---
# holon-agentic-coder-ref-metadata-0368
title: "Submodule gitfile left with container paths breaks host-side git in the flow worktree"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - git
  - submodule
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-23T05:50:00Z
updated_at: 2026-11-27T20:56:58Z
---

## Problem

On PR #249's flow (`flow-remove-token-reduction-copy`), Stage 5's checkout of the `/calibrated` branch failed on the
host with `fatal: gitfile does not point to a valid repository: holon-coherence/.git` (2026-11-23 05:44:15Z). The
`holon-coherence` submodule had been initialised during a containerised stage, so its gitfile and `core.worktree` held
container-relative paths that do not resolve on the host. The flow subagent repaired both by hand in that worktree only;
Stage 5 then succeeded. The other flow worktrees of the same run have no initialised submodule, so only flows whose
agent runs `git submodule` commands inside the container hit this.

## Goal

1. Find where a role container initialises or updates the `holon-coherence` submodule in the mounted worktree, and
   either stop it (role containers do not need the submodule) or make it write host-valid, relative paths
   (`git submodule absorbgitdirs` / relative `gitdir:`).
2. Host-side stages (4 and 5) detect an unresolvable submodule gitfile before any checkout and repair it, or fail with a
   clear message naming the file, instead of failing mid-checkout.
3. Tests: a worktree whose submodule gitfile points at a container path is repaired or rejected before Stage 5 checks
   out.

## Touch set

To be fixed by the plan: the container entrypoint's git setup
(`apps/sandbox-executor/src/sandbox_executor/entrypoint/executor/repair.py`),
`apps/sandbox-executor/src/sandbox_executor/flow/stages/calibrate.py` (pre-checkout check), and their tests.

## Acceptance Criteria

- [ ] Find where a role container initialises or updates the `holon-coherence` submodule in the mounted worktree, and
      either stop it (role containers do not need the submodule) or make it write host-valid, relative paths
      (`git submodule absorbgitdirs` / relative `gitdir:`).
- [ ] Host-side stages (4 and 5) detect an unresolvable submodule gitfile before any checkout and repair it, or fail
      with a clear message naming the file, instead of failing mid-checkout.
- [ ] Tests: a worktree whose submodule gitfile points at a container path is repaired or rejected before Stage 5 checks
      out.

## Flow

- **Slice 1 (`submodule-gitfile-repair`):** Launched `todo/intent-0368-submodule-gitfile-repair.json` covering
  `entrypoint/executor/repair.py`, `flow/stages/calibrate.py`, `tests/test_executor_repair.py`, and
  `tests/flow/stages/test_calibrate.py`.
