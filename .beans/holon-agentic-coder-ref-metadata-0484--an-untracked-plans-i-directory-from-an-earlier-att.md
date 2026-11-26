---
# holon-agentic-coder-ref-metadata-0484
title: "An untracked plans/I-*/ directory from an earlier attempt makes the planner refuse the workspace as uncommitted"
status: completed
type: bug
priority: normal
tags:
  - flow
  - planner
  - worktree
created_at: 2026-11-26T06:00:00Z
updated_at: 2026-11-26T12:10:00Z
---

## Problem

An aborted flow attempt can leave an untracked `plans/I-<id>-<slug>/` directory in the flow worktree. The planner then
treats the mounted workspace as uncommitted and refuses to plan, so a later attempt for the same intent fails for a
reason it did not cause.

## Evidence

- Flow `split-calibration-package`, run for intent `I-1795668981-split-calibration-package`, failed at the plan stage
  (2026-11-26).
- Cause: the untracked `plans/I-1795668981-split-calibration-package/` directory left in the flow worktree made the
  mounted workspace count as uncommitted.
- Cleanup for the three abandoned duplicate attempts (`I-1795665972`, `I-1795666365`, `I-1795668981`) removed their
  remote intent and plan branches. No leftover untracked plan directory for them remained in the flow worktree.

## Proposal

Pick one, or both:

- The wrapper or engine removes or ignores its own untracked plan artefacts from an aborted attempt before the planner's
  cleanliness check runs.
- The cleanliness check ignores untracked paths owned by the flow (for example `plans/<intent id>/` for the intent being
  run), so only foreign uncommitted changes block planning.

## Notes

- Related: bean 0360 (resume after interrupted plan stage creates duplicate plan branch) and bean 0374 (sidecar scratch
  files committed to execution branch) touch the same abort and resume paths.
- Do not delete any `plans/I-*/` directory by hand. Verify it is untracked and from an aborted attempt first.

- In progress (2026-11-26): flow `planner-ignores-aborted-plan-dir` (claude-agent, claude-opus-5-5); scope
  `entrypoint/execution_workspace.py` plus a new test file.

## Resolution

Delivered via [PR #339](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/339) and merged into `main`
(`8ef1bfba`):

- **Key Architectural Deliverables**: `validate_mounted_workspace` (`entrypoint/execution_workspace.py`) no longer
  counts untracked files under the engine-owned `plans/I-*/` directory as uncommitted changes. Every other uncommitted
  change is still refused with the same message.
- **Verification & Tests**: `tests/test_execution_workspace_untracked_plans.py`.
- **Holon Flow Traversal**: flow `planner-ignores-aborted-plan-dir` completed all 5 stages. Its worktree and `I-*`
  branches were removed locally and on origin.
