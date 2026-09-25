---
# holon-agentic-coder-ref-metadata-0054
title: "Make holon calibrate survive the execution branch being deleted on merge"
status: todo
type: bug
priority: normal
tags:
  - flow
  - calibration
  - git
  - ci
created_at: 2026-09-27T11:35:00Z
updated_at: 2026-09-27T11:35:00Z
---

Stage 5 (`holon calibrate <execution_branch>`) runs **after** the PR is merged, but merging a flow PR deletes the
execution branch. The command therefore cannot run at the moment the lifecycle calls for it.

## Measured evidence (Bean 0019, PR #59, 2026-09-27)

- PR merged by the maintainer at `2026-09-27T11:14:03Z` as squash commit `cb1edfd`.
- `git ls-remote origin refs/heads/I-1790382620-.../E-1790401125-.../_` -> `fatal: couldn't find remote ref`; the plan
  ref `.../P-1790382661-.../_` (`4bbd17e`) and the intent ref (`163db30`) both still exist. Only the execution ref is
  consumed by the merge.
- `./holon calibrate <E-branch>` then fails inside `run_calibrate` (`calibration.py:701-707`), which shells out to
  `git checkout -B <calibrated> <execution_branch>`:
  `fatal: '.../E-1790401125-.../_' is not a commit and a branch '.../calibrated' cannot be created from it`.
- The squashed merge means the execution commits are not ancestors of `main` either, so `git branch -r --contains` finds
  nothing; the head is reachable only via the PR ref.

## Workaround used

Recreated the branch locally at the last known head (`90d0acc`, still present in the writer worktree), calibrated, and
pushed the new `.../calibrated` ref. That works only because a worktree still held the object -- a clean clone cannot do
it.

## Desired behaviour

`calibrate` should not depend on a branch that the merge consumes. Options:

1. Accept a commit SHA or a `refs/pull/<n>/head` ref, not only a branch name, and resolve a missing branch through the
   GitHub API (`gh pr view --json headRefOid`) when the branch is gone.
2. Have the execute stage tag the execution head (e.g. `E-<id>`) so provenance outlives branch deletion.
3. Stop deleting flow head branches on merge (repository/setting-level, or a documented precondition in the flow docs).

## Notes

- Target repository: `holon-agentic-coder` -- `apps/sandbox-executor/src/sandbox_executor/calibration.py`
  (`run_calibrate`) and `cli.py` (`calibrate_parser`). Route the change through the flow.
- Found while running stage 5 for Bean 0019; recorded there as a systemic finding.
