---
# holon-agentic-coder-ref-metadata-0369
title:
  "Stage 5 writes a wrong calibration report: recovered infra failures become bug drag, main's files count as the PR's"
status: in-progress
type: bug
priority: critical
tags:
  - flow
  - stage-5
  - calibration
  - holon-agentic-coder
created_at: 2026-11-23T05:55:00Z
updated_at: 2026-11-23T06:00:00Z
---

## Problem

PR #249's calibration report (`plans/I-1795409225-remove-token-reduction-copy/P-1795409242-CLA-CO5.5_calibration.md`,
merged in `c905a98e`) is wrong, and `holon calibrate` reproduces it exactly when re-run from a clean worktree off `main`
(2026-11-23). Three defects, each confirmed against `main` at `c905a98e`:

1. **A recovered infrastructure failure becomes 80 points of bug drag.** A Stage 4 review row (`REV-1795410989-…`,
   05:16Z, "Reviewer ensemble container dispatch exited with code 1") is a failed summary row for the plan.
   `calibration_ev.py:43-45` (`is_matching_record`) matches summary rows by plan branch, so review rows count as
   delivery rows. `calibration_outcome.py:80-87` (`has_unresolved_failure`) lets a later success supersede only a
   `sync_conflict` row, never a `failed` one. `calibration_ev.py:81-83` then sets P(success) and impact "with bugs" to
   0: observed EV −21.01 against a clean 58.99, although the review loop recovered and approved 3/3 with 0/0/0 findings.
2. **Files merged in from `main` are counted as the PR's own.** `calibration.py:780-785` diffs from the plan branch
   (`1915bbc1`) to the execution branch. The execution branch merged `origin/main` (`64af55f1`, bringing PR #244), so PR
   #244's files are counted: 63 files instead of 46, 18 "outside the touch set", recall 71.4%, SSA 10.0.
3. **The wrong commit is recorded as evaluated.** Given the branch name, the report's "Evaluated Commit SHA" is the
   `/calibrated` tip (`764cd3a0`, a calibration/ledger-only commit), not the final code commit (`e4024a6d`).

The same report is produced for every flow whose execution branch merges `main` before Stage 5, or whose Stage 4 hit one
transient container failure, so most calibrations since the dual-EV and review-ledger changes are suspect. Related: Bean
0367 (no fallback report) and Bean 0368 (container submodule gitfile).

## Goal

1. **Bug drag counts only delivery failures.** Only execution (Stage 3) summary rows of this plan feed the dual EV;
   Stage 4/5 pipeline rows never do. An infrastructure failure (container dispatch exit, usage-limit kill, timeout of
   the harness rather than the agent) never counts as a bug. A failed execution row followed by a later converged,
   zero-exit execution row of the same plan is resolved, like a superseded `sync_conflict`.
2. **Patch size measures the PR's own change.** The diff base is the merge-base of the execution head with the target
   branch (`origin/main`), recomputed after any merge of `main` into the branch, so files that arrived only through such
   a merge are never counted, listed outside the touch set, or used for SSA. The `diff_base` label records the base
   used.
3. **The evaluated commit is the last code commit.** Calibration/ledger-only commits on `/calibrated` or `_` are skipped
   when resolving the evaluated SHA; the report's Evaluated Commit SHA equals the head the review approved.
4. **Fail closed on an inconsistent report.** Before Stage 5 commits a report, a self-check fails the stage
   (`StageStatus.FAILED`, nothing committed or pushed, checkpoint left at CALIBRATE) when any of these hold:
   - bug drag > 0 with no unresolved execution failure row behind it;
   - any counted file is changed by the target branch since the plan branch but not by the PR's own commits;
   - the evaluated SHA is a calibration/ledger-only commit, or differs from the approved review head;
   - the report contains the fallback stub text.
5. **Correct PR #249's report** in the same PR: re-run the fixed `holon calibrate` on its execution branch and commit
   the replacement report and append-only ledger rows (expected: drag 0, 46 files, evaluated `e4024a6d`).

## Tests (required; the PR is not done without all of them)

- **PR #249 regression, end to end.** A temp git repo reproducing the exact topology: `main` → plan branch → execution
  commits; `main` advances with unrelated files; the execution branch merges `main`; Stage 4 ledger rows include one
  failed reviewer dispatch row followed by an approved row; `/calibrated` gets a ledger-only commit. Run Stage 5 and
  assert: bug drag 0 and EV with bugs == EV clean; counted files == exactly the PR's own files; no main-only file in
  "outside the touch set"; Evaluated Commit SHA == the last code commit; the report passes the self-check.
- **Dual EV unit matrix** (`calibration_ev` / `calibration_outcome`): parametrised over row kinds (execution, review,
  calibrate), statuses (`failed`, `sync_conflict`, success) and order (failure then success, success then failure,
  failure last). Assert drag only when an execution failure is unresolved; review/calibrate rows never move the
  with-bugs values; an infra failure row never counts.
- **Diff base property test** (Hypothesis, as the repo's fuzz tests do): random sets of files changed on `main` and on
  the PR, with zero to three merges of `main` into the execution branch at random points. Invariant: counted files ==
  files the PR's own commits change, for every case.
- **Evaluated SHA tests:** `/calibrated` tip with one or more ledger-only commits, an execution head that is itself a
  merge of `main`, and a branch with no ledger-only commit on top.
- **Self-check tests:** one failing test per self-check condition in Goal 4, asserting the stage fails, nothing is
  committed or pushed, and the log names the violated condition; plus one passing consistent report.
- **Golden report:** the PR #249 fixture's rendered report compared against a checked-in expected Markdown file, so any
  change to drag, file counts or evaluated SHA shows up as a diff.
- **Mutation check:** run the repository's mutation-testing gate on `calibration_ev.py`, `calibration_outcome.py` and
  `calibration_diff.py`; no surviving mutant in the changed lines.

## Touch set

`apps/sandbox-executor/src/sandbox_executor/calibration_ev.py`,
`apps/sandbox-executor/src/sandbox_executor/calibration_outcome.py`,
`apps/sandbox-executor/src/sandbox_executor/calibration_diff.py`,
`apps/sandbox-executor/src/sandbox_executor/calibration.py`,
`apps/sandbox-executor/src/sandbox_executor/flow/stages/calibrate.py`,
`apps/sandbox-executor/tests/test_calibration_dual_ev.py`, `apps/sandbox-executor/tests/test_calibration_ev.py`,
`apps/sandbox-executor/tests/test_calibration.py`, `apps/sandbox-executor/tests/test_calibration_touch_set.py`,
`apps/sandbox-executor/tests/test_calibrate_full_stage5.py`, `apps/sandbox-executor/tests/test_calibrate_rerun.py`,
`apps/sandbox-executor/tests/flow/stages/test_calibrate.py`, new
`apps/sandbox-executor/tests/test_calibration_regression_merge_main.py` and its golden file
`apps/sandbox-executor/tests/fixtures/calibration_merge_main_expected.md`,
`plans/I-1795409225-remove-token-reduction-copy/P-1795409242-CLA-CO5.5_calibration.md`.
