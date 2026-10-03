---
# holon-agentic-coder-ref-metadata-0060
title: "Stage 5 calibrates a stale base: holon calibrate resolves branch names against stale local refs"
status: todo
type: task
priority: medium
tags:
  - flow
  - calibration
  - git
  - review-loop
created_at: 2026-09-28T07:45:00Z
updated_at: 2026-09-28T07:50:00Z
---

## The defect

`holon calibrate` (stage 5) measures the change it is calibrating by branch _name_, resolved against whatever the local
repository happens to hold. Nothing in the path fetches, and nothing verifies that the refs it resolved are the ones the
review loop approved. When the local repository is behind -- the normal case for a host worktree that only ever ran the
early stages -- stage 5 silently scores the wrong change and publishes a wrong artifact.

This happened on Bean 0019 / PR #60. Calibration ran at `2026-09-28T04:29:38Z`, one minute after the iteration-2
consensus review was posted. The local execution ref was still `4052853`, two review-iteration commits behind the PR
head `2552584` (`9a107f8` prettier, `2552584` lock/HEAD fixes), and the local plan branch ref
`I-1790562445-.../P-1790562483-.../_` did not exist at all. Consequences, all recorded in commit `4ce1baf`:

- `git diff --shortstat <plan_branch>..<exec_branch>` returned a non-zero exit (unknown ref) and was swallowed by the
  `except` in `parse_actual_metrics`, so patch size collapsed to zero;
- the report asserted `State Surface Area ... Observed 0.2 (0 files modified)` for a change that is **5 files, +976 /
  -103**;
- entropy error was recorded as `0.70` where the true value is `1.16`, and `EV_actual` as `69.52` where the true value
  is `68.96`.

Those numbers are what the EV accounting and the plan-quality feedback loop consume, so the mismeasurement is not
cosmetic.

**Second occurrence, same day (PR #61 / slice B).** There the execution ref happened to be current, but the plan-branch
ref was absent locally, so only the patch-size step failed and it still reported "`0 files modified`", SSA `0.2`,
`EV_actual` 74.27 for a 7-file / +777 / -116 change (true: SSA 5.9, `EV_actual` 73.76, `ΔEV` +3.78). Both were corrected
append-only: `47a9864` + `a086d8d` on `I-1790562445-.../E-1790563015-.../calibrated`, and `a41627b` on
`I-1790564113-.../E-1790564813-.../calibrated`.

## Where

`apps/sandbox-executor/src/sandbox_executor/calibration.py`:

- `parse_actual_metrics` step 3 (patch size): `subprocess.run(["git", "diff", "--shortstat", f"{base}..{target}"])` with
  `cwd=repo_dir`, branch names resolved against local refs, failure silently treated as "no change";
- `parse_actual_metrics` steps 1 and 2: reads `holon-knowledge/ledger/executions.jsonl` and `executions/<id>.md` from
  the **working tree** of `repo_dir`, i.e. whatever branch that checkout happens to have, not the execution branch being
  calibrated;
- `run_calibrate`: `git checkout -B <calibrated> <execution_branch>` (see the second defect below).

## Requested change

1. **Fetch before measuring.** Resolve the intent / plan / execution refs against `origin/<branch>` (or fetch the branch
   into the local ref first) instead of trusting the local ref. `git ls-remote`/`origin/...` is the source of truth for
   a flow branch.
2. **Fail loudly.** A non-zero `git diff` inside `parse_actual_metrics` must abort calibration with the branch name and
   the git stderr in the message. An unresolvable ref is never "zero files changed".
3. **Read the ledger from the ref, not the checkout.** Read the execution record and ledger rows with
   `git show <exec_ref>:<path>` so the measured values come from the execution branch under calibration.
4. **Assert the head.** Stage 5 should record the full `exec` sha it measured and compare it against the PR head
   (`gh pr view --json headRefOid`) when a PR exists, warning when they differ. Calibration of a head the review loop
   never saw -- or measurement of a head the review loop has since superseded -- must be visible, not silent.

## Second defect: `checkout -B` rewrites a published flow branch

`run_calibrate` does `git checkout -B <calibrated> <execution_branch>`. If the calibrated branch has already been pushed
(the normal case once a human or a previous run publishes it), re-running stage 5 discards the published commit and
publishing the result needs `--force`, which [.agents/rules.md](../../.agents/rules.md) and [AGENTS.md](../../AGENTS.md)
forbid on a flow branch. On PR #60 the correction had to be applied by hand, as a merge of the execution head plus an
appended corrected report, so the push stayed a fast-forward (see `47a9864`, `a086d8d` on branch
`I-1790562445-.../E-1790563015-.../calibrated`).

Requested: make re-running stage 5 append-only -- if the calibrated branch already exists, update the report in a new
commit on top of it (fast-forward) instead of re-branching from the execution branch, and report which of the two paths
it took.

## Notes

- Related: [bean 0054](holon-agentic-coder-ref-metadata-0054--make-calibrate-survive-exec-branch-deletion.md) (stage 5
  surviving a deleted `E-...` branch) -- same code path, different failure mode: 0054 is about the branch being gone,
  this one is about it being stale and the failure being silent.
- Ordering rule that this defect broke in practice: stage 5 runs **after** the review loop has finished pushing. Any
  review-iteration commit pushed after calibration starts makes the calibration stale. Worth encoding in the stage-5
  guard from point 4 above.
- Target repository: `holon-agentic-coder`, `apps/sandbox-executor/src/sandbox_executor/calibration.py` plus
  `apps/sandbox-executor/tests/test_calibration.py`. Changes must go through the flow, not a host-side hand edit.
