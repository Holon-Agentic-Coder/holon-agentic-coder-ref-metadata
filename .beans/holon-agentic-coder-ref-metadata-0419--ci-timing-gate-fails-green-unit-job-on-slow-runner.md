---
# holon-agentic-coder-ref-metadata-0419
title: "CI Timing Gate fails a green unit job on a slow runner and withdraws flow consensus"
status: completed
type: bug
priority: high
tags:
  - ci
  - flow
  - holon-agentic-coder
created_at: 2026-11-24T11:45:00Z
updated_at: 2026-11-26T08:49:03Z
---

## Problem

On 2026-11-24 the `unit (ubuntu-latest)` check of holon-agentic-coder PR #270 failed on head `c341f784` (run
45384726497, job 138412602406, finished 11:36:14Z). The failure was not a test failure. Every step before the gate
passed; pytest reported `6706 passed, 1 skipped, 678 subtests passed in 351.12s`. The failing step was
`CI Timing Gate (compare with main)`:

```text
Timing regression: job took 360 s against a baseline median of 229 s over 5 main runs (tolerance 50%, minimum delta
120 s).
```

The merge into the branch changed only ledger files under `holon-knowledge/ledger/`, so the code was identical to head
`2678fa5b`, whose run 45382741619 took 240 s and passed. The flow read the failed check, withdrew its consensus (ledger
row `ACT-WITHDRAW-1795520273-bfbde73b`) and restarted Stage 4, although the maintainer merged the PR through the merge
queue at 11:31:45Z, before the check finished.

### Evidence that the runner was slow, not the code

The per-test report lists tests that normally take under a second and took 6 to 13 s each. They are spread across
unrelated files, which points at a contended runner and not at one regressed test:

| Test (under `apps/sandbox-executor/tests/`)                                                                 | Baseline | Current |
| ----------------------------------------------------------------------------------------------------------- | -------- | ------- |
| `flow/stages/test_decomposition.py::TestEntropyBudgetHandoffInFlow::test_stage3_never_halts_for_a_human`    | 0.8 s    | 13.4 s  |
| `test_flow_default_branch_worktree.py::test_an_existing_flow_worktree_is_reused`                            | 0.1 s    | 11.1 s  |
| `flow/stages/test_plan_resume_adopts_branch.py::TestRecordPlanBranchBeforePush::test_checkpoint_records...` | 0.8 s    | 10.9 s  |
| `test_review_carried_findings.py::test_a_failed_carried_pass_records_its_rejected_attempt`                  | 0.1 s    | 8.5 s   |
| `test_git.py::test_has_effective_diff_reverted_change_is_empty`                                             | 0.0 s    | 6.2 s   |

Recent `unit (ubuntu-latest)` durations on the same workflow: 203 s, 226 s, 240 s, 283 s, 298 s, 302 s, then 368 s on
this run. The median-of-5 baseline is 229 s, so a 50% tolerance (344 s) sits inside the normal spread when the runner is
busy. The same job on main (run 45385001779, commit `bfbd9f4e`) was still running when this was written, so main's
health is not yet confirmed.

## Goal

- The gate does not fail a job whose pytest result is green on runner noise alone. Options: compare the sum of per-test
  times with a larger tolerance, require two consecutive breaches, retry the gate once on a fresh run, or raise the
  tolerance or minimum delta to cover the observed spread (the 2026-10-26 evidence in Bean 0163 already showed about 20%
  variance between identical runs).
- The flow's merged-head CI gate treats a timing-gate failure with all tests passing as a distinct, retryable outcome
  and does not withdraw consensus on it without one rerun. Never rerun CI from a diagnosis; the flow or maintainer
  decides.
- Record the decision in the CI timing documentation.

## Notes

- Overlap: Bean 0404 is the same defect on the macOS unit job. Bean 0404 owns the fix; this bean adds the
  withdrawn-consensus consequence and is covered by the same flow.
- Related: Bean 0163 (introduced the gate), Bean 0405 (unit suite slowest tests), Bean 0420 (the flow outcome after the
  merge).
- Not confirmed: the cause of the slow runner. The job log has no resource data.

## Progress

- 2026-11-24: covered by the flow of Bean 0404 (`timing-gate-judges-test-time`), launched today; see that bean.

## Audit evidence, 2026-11-24T12:58Z (self-improvement audit, fifth merge)

- Every failed pipeline run in holon-agentic-coder from 09:58Z to 12:55Z failed on a timing gate and on nothing else:
  seven runs, all tests green. `CI Timing Gate (compare with main)` on `unit (macos-latest)`: `03cd2f88`, `6827b0d1`,
  `65d5f906`, `d07ba894` (PR #272, 631 s), `8994dec5` (PR #273, 652 s); on `unit (ubuntu-latest)`: `c341f784` (PR #270,
  368 s); `Timing gate` on `Workspace survival (ubuntu-latest)`: `770fd6fe` (PR #269). Main had no failure in 24 push
  runs.
- Spread of the same job on unchanged code in this window: macOS unit 246 s to 652 s, Ubuntu unit 203 s to 368 s.
- Forecast to check: PR #275 (Bean 0405) brings the unit jobs to about 190 to 210 s. A median-of-5 baseline of about 200
  s with 50 percent tolerance and a 120 s minimum delta puts the bar near 320 s, while the runner spread seen above is
  up to 400 s. Unless the gate changes first, expect more timing-gate failures after #275 merges, not fewer.

- 2026-11-25: PR #278 merged into `main` as `0c933519`. Delivered for the unit gate: the gate now judges summed JUnit
  test time, the first option in the Goal, so a slow runner with green tests no longer fails the gate on wall-clock
  alone. Still open: (1) the flow outcome, where a timing-gate failure with all tests green withdraws consensus with no
  retry (Goal bullet 2); this is the same engine retry that Bean 0404 lists, so it is not moved here; (2) recording the
  decision in the CI timing documentation, not verified in this merge. Bean stays open for those two items.

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

## Resolution

Delivered via [PR #321](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/321) and merged into `main`
(`903aafe4`):

- **Key Architectural Deliverables**: the final-head timing-noise rerun is bounded and covers unchanged-code heads
  (`ci_final_head.py`, `ci_timing_rerun.py`), so a timing-gate-only failure with green tests is retried before consensus
  is withdrawn; `docs/git_flow.md` records the rule. The summed-JUnit gate itself came earlier with PR #278.
- **Verification & Tests**: 11 of 11 checks green on the final head; review consensus (ensemble of 3, two passes).
- **Holon Flow Traversal**: flow `timing-gate-runner-variance` completed Intent -> Plan -> Execute -> Review Loop ->
  Calibration; the maintainer merged the pull request.
