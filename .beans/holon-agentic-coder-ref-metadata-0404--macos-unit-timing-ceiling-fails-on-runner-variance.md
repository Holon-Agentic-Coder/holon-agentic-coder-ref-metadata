---
# holon-agentic-coder-ref-metadata-0404
title: "The 600 s timing ceiling on the macOS unit job fails pull requests on runner variance"
status: in-progress
type: bug
priority: high
tags:
  - ci
  - timing-gate
  - flake
  - holon-agentic-coder
created_at: 2026-11-24T09:35:00Z
updated_at: 2026-11-27T00:56:56Z
---

## Problem

`unit (macos-latest)` has an absolute ceiling of 600 s in the CI Timing Gate (`test-unit.yml`, `--ceiling 600`), and the
`timing-regression-accepted` label does not lift it. The job's duration swings by a factor of two to three between runs
of the same code, and its normal value sits just under the ceiling, so the gate fails pull requests at random:

| Branch (2026-11-24, UTC)        | macOS unit job durations                |
| :------------------------------ | :-------------------------------------- |
| `main` (07:42)                  | 565 s                                   |
| `claude-code-mode-default-on`   | 576 s, 588 s, 549 s                     |
| `flow-e2e-test-teardown`        | 387 s, **744 s (failed)**, 555 s, 577 s |
| `ledger-temp-worktree-cleanup`  | 451 s, 598 s, 250 s                     |
| `claude-token-os-keychain-only` | 234 s, 257 s, **663 s (failed)**        |

The last row is the same pull request (#271): 234 s and 257 s on two heads, then 663 s on a head that added only
calibration commits. The ubuntu job stayed between 204 s and 302 s throughout. On #271 the failure withdrew a 3/3
approval in Stage 5 and stopped the flow of Bean 0225; the engine's one automatic rerun failed the same way.

## Goal

- A slow runner does not fail a pull request: judge the gate on test time measured inside the job (the JUnit total)
  rather than on wall-clock time that includes runner start-up and dependency install, or take the best of the rerun
  attempts, or set the ceiling from the measured spread instead of a fixed 600 s.
- Find why the macOS job is bimodal (about 250 s or about 570 s for the same code): runner hardware class, cache hit or
  miss, or worker count.
- The engine's timing-noise rerun (`_retry_timing_noise`) covers this case: it should retry a ceiling failure on a head
  whose code did not change, more than once if needed, before withdrawing an approval.

## Acceptance

- [ ] A slow runner does not fail a pull request on the `unit (macos-latest)` timing gate: the gate judges summed JUnit
      test time, not job wall-clock time (delivered by PR #278).
- [ ] Every `--ceiling` timing-gate job, including `Workspace survival` in `test-stress.yml`, is covered by the same
      rule, so a job that is slow on wall-clock time with no test grown does not fail (the Workspace survival job runs
      at `--ceiling 900` with `--junit`).
- [ ] The engine's timing-noise rerun retries a ceiling failure on a head whose code did not change, more than once if
      needed and within a bound, before withdrawing an approval (delivered by PR #321).
- [ ] The cause of the bimodal macOS job (about 250 s or about 570 s for the same code) is found and named: runner
      hardware class, cache hit or miss, or worker count.
- [ ] The cancelled (not failed) `build (macos-latest)` and `unit (macos-latest)` jobs seen on #272 and #278 are
      explained.
- [ ] The closing banner of the flow follows the final state of the flow: it does not print "[REVIEW APPROVED] ... ready
      for the maintainer to merge" after "Not ready to merge. The approval covered ... no longer stands".
- [ ] `docs/git_flow.md` states the timing-gate rule (delivered by PR #321).

## Assumptions

- The closing-banner defect is listed under the second occurrence as a separate defect, not under Goal; it is included
  as an acceptance item. Validate: check whether a bean already tracks it; if so, move the item there.
- "Within a bound" for the rerun is inferred from the delivered bounded rerun in PR #321. Validate: read
  `ci_timing_rerun.py` for the bound.
- The bimodal cause is accepted as met when a cause is named with evidence from run data. Validate: the maintainer
  agrees the evidence suffices, or opts to scrap the item.
- Items marked as delivered are taken from the Progress section. Validate: the merge commits `0c933519` and `903aafe4`.

## Notes

- Overlap: Bean 0419 is the same defect (the timing gate failing a green job on a slow runner and withdrawing
  consensus). This bean owns the fix; Bean 0419 is covered by the same flow.
- Found on Bean 0225's flow, 2026-11-24. The flow subagent could not tell whether the pull request or the runner was
  slow; the table above shows it is the runner.
- Related: Bean 0168 (unit suite runs 1.7x slower on macOS), Bean 0400 (shorten the CI pipeline), Bean 0163 (the timing
  gate, completed), Bean 0403 (no full CI for bookkeeping-only commits would have avoided this run entirely).

## Second occurrence (2026-11-24T09:40Z, Bean 0387)

- Pull request #270 (`ledger-temp-worktree-cleanup`): 3/3 approval, then Stage 5 failed with "CI is red on final head
  6c7be9a after one automatic rerun of the timing gate: unit (macos-latest) (CI Timing Gate, 11.1 min)". The same branch
  ran that job in 250 s an hour earlier. Two flows were stopped by this gate within one hour, and Stage 5 ran 33 minutes
  against its 10-minute budget waiting for it.
- Separate defect seen in the same log: straight after "Not ready to merge. The approval covered 8605f54 and no longer
  stands" the flow prints "[REVIEW APPROVED] Review Loop reached consensus approval; the PR is ready for the maintainer
  to merge". The closing banner must follow the final state of the flow, not the Stage 4 result.

- 2026-11-24: the flows of Beans 0403 and 0405 attack the cause (fewer full pipeline runs and a faster unit suite); this
  bean still needs the maintainer's choice between judging test time and raising the ceiling.

## Third occurrence — Workspace survival (`ubuntu-latest`) also hits `--ceiling 600` (2026-11-24T10:59Z, Bean 0226)

- Pull request #269 (`flow-e2e-test-teardown`, Bean 0226): `Workspace survival (ubuntu-latest)` (`test-stress.yml`)
  failed at `2026-11-24T10:59:27Z` with `Job took 609 s, above the 600 s ceiling` while reporting
  `Per-test report: no test grew by more than 50 % and 5 s against its baseline median`.
- Recent `Workspace survival (ubuntu-latest)` durations were already near saturation: `513 s` on #267 and `554 s` on
  #268.
- Scope note: any fix for `unit (macos-latest)`'s fixed `--ceiling 600` (judging JUnit test time instead of runner
  wall-clock, raising the ceiling, or retrying ceiling-only noise) should cover all `--ceiling 600` timing-gate jobs
  including `test-stress.yml` (`Workspace survival`).

## Progress

- 2026-11-24: flow `timing-gate-judges-test-time` launched (`claude-agent` / `claude-fable-5-2`), covering this bean and
  Bean 0419 together. Approach taken, on the agent's recommendation after the maintainer asked for the highest-priority
  bean to be picked up: the gate judges summed test time from the JUnit report instead of job wall-clock time and treats
  a slowdown spread across the whole suite as runner variance; the 600 s ceiling value and the workflow file are
  unchanged. Not in this flow: the engine retrying a timing-only failure before withdrawing an approval (it touches the
  review and calibrate code that Beans 0376, 0407 and 0399 are changing).

## Fourth occurrence — PR #273 `unit (macos-latest)` ceiling failure (2026-11-24T12:17:52Z)

- `holon-agentic-coder#273` (`route-stage-4-and-stage-5`, Bean `0376` child 4), run `45390444554` on commit `8994dec5`:
  `unit (macos-latest)` failed `CI Timing Gate (compare with main)` with `Job took 634 s, above the 600 s ceiling` while
  all pytest cases passed (`test_child_halting_at_its_own_review_is_a_success_and_records_its_pr` `8.5 s` -> `13.7 s`).
- 2026-11-24: pull request #278 (flow `timing-gate-judges-test-time`) is approved, calibrated and green, awaiting the
  maintainer's merge. Remaining scope found on its own pipeline: the `Workspace survival (ubuntu-latest)` job has its
  own timing gate with a fixed 600 s ceiling on job wall-clock time and failed twice at 611 s and 602 s with no test
  grown; #278 does not change that job's gate. Also unexplained: `build (macos-latest)` and `unit (macos-latest)` were
  cancelled (not failed) once each on #272 and #278 and passed on a rerun.

- 2026-11-25: PR #278 merged into `main` as `0c933519`. Delivered: the CI Timing Gate (`scripts/ci_timing_gate.py`, with
  `scripts/ci_timing_noise.py`) judges summed JUnit test time, not job wall-clock, and treats a slowdown spread across
  the whole suite as runner variance. The 600 s ceiling value and the workflow files are unchanged. Still open, not
  delivered by #278: (1) the `Workspace survival (ubuntu-latest)` fixed 600 s wall-clock ceiling in `test-stress.yml`
  (see the scope note above); (2) the engine retrying a timing-only failure before withdrawing an approval
  (`_retry_timing_noise` in `apps/sandbox-executor/src/sandbox_executor/flow/github/ci_final_head.py` predates #278 and
  #278 did not change it); (3) why the macOS job is bimodal (about 250 s or 570 s on the same code); (4) the cancelled
  `build (macos-latest)` and `unit (macos-latest)` jobs on #272 and #278, unexplained.

## Flow launch, 2026-11-26

- 2026-11-26: flow `timing-gate-runner-variance` launched (`claude-agent` / `claude-opus-5-5`), covering the items still
  open here and in the other bean: the bounded rerun of a timing-gate-only failure on unchanged code in the final-head
  check (`ci_final_head.py`), and the CI timing section of `docs/git_flow.md`. Main already judges summed JUnit test
  time and the Workspace survival job runs at `--ceiling 900` with `--junit`, so no workflow file changes. Bimodal
  runner cause and the cancelled-job question stay open.

- 2026-11-26: flow `timing-gate-runner-variance` completed: PR #321 (head `b3ef0e4`) is OPEN, MERGEABLE/CLEAN, 11 of 11
  checks green, review approved (consensus score 1, ensemble of 3, two passes), calibration report in the PR diff,
  final-head CI success. Delivered: the final-head timing-noise rerun is bounded and covers unchanged-code heads
  (`ci_final_head.py`), the Workspace survival bare `Timing gate` step is recognised as a timing gate
  (`ci_failure_detail.py`, outside the intent scope, see bean 0492), and `docs/git_flow.md` states the rule. Awaiting
  the maintainer's merge.

- 2026-11-26: PR #321 merged into `main` as `903aafe4`; bean 0419 closed by it. Delivered: the final-head timing-noise
  rerun is bounded and covers unchanged-code heads (`ci_final_head.py`, `ci_timing_rerun.py`); the Workspace survival
  bare `Timing gate` step is recognised (`ci_failure_detail.py`); `docs/git_flow.md` states the rule. Still open, so the
  bean stays `in-progress`: (1) the bimodal macOS runner cause (about 250 s or 570 s on the same code); (2) the
  cancelled `build (macos-latest)` and `unit (macos-latest)` jobs on #272 and #278, unexplained.
