---
# holon-agentic-coder-ref-metadata-0054
title: "Make holon calibrate survive the execution branch being deleted on merge"
status: completed
type: bug
priority: normal
tags:
  - flow
  - calibration
  - git
  - ci
created_at: 2026-09-27T11:35:00Z
updated_at: 2026-10-05T09:50:00Z
---

Stage 5 (`holon calibrate <execution_branch>`) is a **pre-merge** stage -- `STAGE_ORDER` in `sandbox_executor/flow.py`
runs `CALIBRATE` after `REVIEW` and the pipeline halts for the human without merging -- but in the Bean 0019 incident it
could only be run **after** the PR was merged, and merging a flow PR deletes the execution branch. The command therefore
cannot run at the moment the lifecycle calls for it.

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
- Premise corrected during PR #47 review: the lifecycle places stage 5 before the merge (see the merge-boundary ordering
  note in `AGENTS.md`), so the defect is that the incident ran it after the merge and the branch was already gone -- not
  that the lifecycle asks for a post-merge calibration.

## Second face of the same defect (2026-09-28, Bean 0019 slice A/B closeout)

Running stage 5 **before** any merge still fails when the execution branch exists only as
`refs/remotes/origin/<I-...>/P-.../E-.../_`. `run_calibrate` shells out to
`git checkout -B <branch>/calibrated <execution_branch>`, and a name ending in `/_` is not resolved through
`refs/remotes/origin/*` by that command, so stage 5 dies with:

```text
Error during calibration: Failed to checkout calibrated branch '.../calibrated' from '.../_':
fatal: '.../_' is not a commit and a branch '.../calibrated' cannot be created from it
```

Workaround used twice (slices A and B): create the local ref first -- `git branch -f "<E-branch>" <sha>` -- then re-run.

So the requirement is broader than "survive branch deletion": **`calibrate` must resolve its input against the remote
namespace, a SHA, or a PR head ref, not against local branch names only.** Remedy 1 above covers it; the local-ref
workaround should not be the documented answer, because a human running stage 5 in a fresh worktree will hit it exactly
the way an agent did.

## Third face: the failure is silent (2026-09-28, PR #60/#61 closeout)

A missing ref does not always kill stage 5. When the ref resolves but the _plan_ branch ref is absent, or when the local
execution ref is merely stale, `parse_actual_metrics` swallows the non-zero `git diff --shortstat` and publishes a
calibration that measures nothing -- "`0 files modified`", SSA `0.2`, and an inflated `EV_actual`. It happened on both
slices of Bean 0019 (PR #60 and PR #61) and both wrong numbers went into the bean ledger and the PR prose before anyone
82: checked. Tracked as [bean 0060](holon-agentic-coder-ref-metadata-0060--make-calibrate-resolve-fresh-remote-refs.md),
whose remedy 2 ("fail loudly, never treat an unresolvable ref as zero files changed") is the part this bean still lacks.

## Resolution

Resolved via the 5-stage Holon flow (Batch B) in PR
[#63](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63):

1. **Stage 1 (Intent)**:
   - Branch `I-1791151674-calibration-integrity-resilience-and-staleness-detection/_` logged in `intents.jsonl`.
2. **Stage 2 (Plan)**:
   - Branch `I-1791151674-.../P-1791151683-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Artifact `plans/P-1791151683-antigravity-agent-gemini-3.8-flash-medium.md` logged in `plans.jsonl`.
3. **Stage 3 (Execute)**:
   - Branch `I-1791151674-.../E-1791151927-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Core implementation:
     - `apps/sandbox-executor/src/sandbox_executor/calibration.py`: Added `resolve_git_ref` and
       `fetch_remote_ref_if_needed` supporting remote tracking refs (`origin/<branch>`), commit SHAs, and PR head
       references (`pull/<n>/head`).
     - In `run_calibrate`, creating a new calibrated branch uses
       `start_point = report.evaluated_commit_sha or resolve_git_ref(execution_branch, repo_dir=repo_dir) or execution_branch`,
       resolving cleanly even when the execution branch has been deleted or exists only remotely.
     - Added comprehensive unit tests in `apps/sandbox-executor/tests/test_calibration.py`.
4. **Stage 4 (PR Review Loop)**:
   - PR [#63](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63) opened.
   - Iteration 1 ensemble review flagged start-point resolution on branch checkout; resolved in commit `1171601`.
   - Iteration 2 ensemble review achieved unanimous approval (3/3 `APPROVED`, 0 Critical, 0 Important).
   - Consensus review posted to PR #63.
   - GitHub CI: 10/10 checks green.
5. **Stage 5 (Calibration)**:
   - Generated calibration report with predicted EV 85.95, actual EV 93.89 (ΔEV: +7.94).
   - Pushed to `/calibrated` branch.
6. **Merge Boundary**:
   - Preserved human-only PR merge constraint; halted with consensus approval and calibration complete. Ready for human
     merge at https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/63.
