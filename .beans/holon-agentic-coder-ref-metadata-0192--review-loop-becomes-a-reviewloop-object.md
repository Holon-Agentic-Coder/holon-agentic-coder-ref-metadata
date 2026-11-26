---
# holon-agentic-coder-ref-metadata-0192
title: "Decompose run_review_loop and run_review_stage into a ReviewLoop object with named steps"
status: todo
type: task
priority: high
tags:
  - refactor
  - complexity
  - review-loop
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-23T08:05:48Z
---

## Problem

Spawned by Bean 0177. `run_review_loop` (`993b686`) is **528 lines, CC 131**, the most complex function after the two
`main`s; `run_review_stage` is 258 lines, CC 36. Both were the most-collided functions in `flow.py`: four of the flow
PRs #94-#109 edited each. Their state is hundreds of lines of locals passed between ad-hoc helpers (`_loop_status`,
`_ensemble_iteration`, `_reviewers_objected`, `_record_reviewer_rows` and others).

## Scope

1. `ReviewLoop` class in `flow/review_loop.py` holding the loop state (iteration, voted head, findings, budget) with one
   method per step: `resolve_target`, `wait_for_ci`, `run_ensemble`, `record_findings`, `decide`, `post_consensus`.
   `run_review_loop` becomes a thin wrapper for compatibility.
2. `run_review_stage` delegates to it; `run_review_loop_cli` moves to the CLI review command.
3. Iteration verdicts are pure functions over the reviewer results (functional core) and tested without git or `gh`.
4. All functions within the 0185 limits; existing review-loop tests green; fail-closed behaviour unchanged.

## Touch set

`flow/review_loop.py`, `flow/stages/review.py`, `cli/commands/review*.py` (one import), `tests/flow/test_review_loop.py`
and `tests/test_review_loop.py`.

## Dependencies

Its blocker 0191 completed (PR #260). Sequence with 0160 and 0179, which change the same loop.

## Notes

- Run through the Holon flow on holon-agentic-coder.

## Audit (2026-11-21)

Touch set refreshed: the loop is `flow/review/loop.py` (952 lines, module budget applies),
`flow/review/{cli,ensemble,resolver,records,verdict}.py` and `flow/stages/review.py`; tests are
`tests/flow/review/test_loop.py` and `tests/flow/stages/test_review.py`. The `flow/review_loop.py` path above does not
exist. Still blocked by 0191 (shared call sites).

## Run log (2026-11-23)

- Intent `todo/intent-0192-review-loop-object.json` (slug `review-loop-object`), intent branch
  `I-1795388459-review-loop-object/_`, pushed. No PR opened.
- Plan stage ok: `P-1795395413-CLA-CO5.5/_`.
- Execute stage blocked (two attempts: E-1795395756 exists on origin at c6cf760 as an unmerged execution branch,
  E-1795397253 is local only). Confirmed cause: the executor's pre-push sync merges `origin/main` (which has moved past
  the intent base `b22258dc`, including #239 and #240) and hits a non-ledger conflict in
  `apps/sandbox-executor/src/sandbox_executor/flow/__init__.py`. The reconcile step raises `ConflictResolutionError` and
  refuses to push. A checkpoint resume cannot change this base; the fix needs a fresh intent cut from current `main` (or
  a maintainer decision), not a hand patch.
- Checkpoint: `apps/holon-agentic-coder/flow-review-loop-object/.holon/flow/checkpoint-review-loop-object.json` at stage
  execute. Earlier checkpoint backed up under the scratchpad.
- Status stays `in-progress`; blocked_by 0191 is also still in progress and shares call sites.

> 2026-11-23: stale worktree deleted 2026-11-23; restart from current main. Backup:
> todo/stale-worktree-backups/flow-review-loop-object-2026-11-23.bundle

- 2026-11-23: unblocked. Its `blocked_by` bean 0191 is completed (parent PR #260 merged into `main` as `7225685d`).
  Status left as `todo`.
