---
# holon-agentic-coder-ref-metadata-0405
title: "Clean up unnecessary unit tests: the suite has outgrown the pipeline"
status: in-progress
type: task
priority: high
tags:
  - tests
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T09:55:00Z
updated_at: 2026-11-27T17:58:33Z
---

## Why

Maintainer, 2026-11-24: "the tests are getting quiet long now. ubuntu unit test take 4m, workspace survival takes 7m,
and macos unit test takes more than 8m. make a bean to clean up all unncessary unit tests".

## Problem

The unit suite of `apps/sandbox-executor` has grown faster than anything prunes it, and every flow waits for it at least
twice.

| Measure (2026-11-24)                 | Value                                                        |
| :----------------------------------- | :----------------------------------------------------------- |
| Test files                           | 243                                                          |
| Lines of test code                   | about 71,800                                                 |
| Test functions                       | 3,486 (6,470 collected cases with parametrisation)           |
| `unit (ubuntu-latest)`               | 204 to 302 s today; about 120 s when the timing gate was set |
| `unit (macos-latest)`                | 234 to 744 s today; 235 to 370 s when the gate was set       |
| `Workspace survival (ubuntu-latest)` | 6.5 to 7 minutes                                             |
| Largest files                        | `test_review_loop.py` 2,579 lines, `test_cli.py` 1,859,      |
|                                      | `test_calibration.py` 1,780, `test_local_llm.py` 1,327       |

The suite roughly doubled in run time since the gate's thresholds were written into `test-unit.yml`. The macOS job now
sits at the 600 s ceiling and fails approved pull requests on runner variance (Bean 0404); two flows were stopped by it
within an hour on 2026-11-24. Every flow adds tests (review findings and surviving mutants each add more) and nothing
removes any.

## Goal

1. **Measure first.** From the JUnit reports of recent runs on `main`: time per test, per file and per fixture, on both
   runners; list the slowest 50 tests and the files that carry most of the time. No test is removed on a guess.
2. **Remove what is unnecessary**, each removal with its reason:
   - duplicates: tests that assert the same behaviour through the same path (often one per review finding);
   - tests that only restate the implementation (mock in, same mock out) and cannot fail for a real defect;
   - parametrised cases that add no new branch;
   - tests for code that has been deleted or is unreachable;
   - tests superseded by a broader test that covers the same lines and mutants.
3. **Make the necessary ones cheap**: real sleeps, real subprocesses, real git repositories and real timeouts in unit
   tests replaced by fakes or injected clocks (Bean 0167 is one instance); expensive fixtures shared at module or
   session scope where it is safe; anything that needs Docker, the network or a real repository moved to the integration
   or stress suite.
4. **Keep the safety net**: line and branch coverage do not fall, and the mutation score of the touched modules does not
   fall. A removed test that was the only killer of a mutant is kept or replaced.
5. **Workspace survival**: say why it takes 7 minutes and whether it must run on every push or only when the paths it
   protects change.
6. **Stop the regrowth**: a per-test time limit in the unit suite and a note in the review rules that a finding is
   answered by strengthening an existing test where one exists, not always by adding one.

## Targets (to confirm after the measurement)

- `unit (ubuntu-latest)` back to about 2 minutes, `unit (macos-latest)` under 5 minutes on a slow runner.
- The suite's size reported in the pull request so growth is visible.

## Notes

- Large: plan it as a split flow, one package or test area per sub-intent (review loop, CLI, calibration, local LLM,
  flow stages), each with its own before and after timings. Touch sets are test files, so they rarely overlap feature
  work but do overlap each other; run the sub-intents in sequence.
- Module budgets apply to test code as they do to source; do not change the budget file.
- Related: Bean 0404 (timing ceiling fails on runner variance; this bean removes the cause, 0404 the symptom), Bean 0400
  (shorten the pipeline), Bean 0168 (unit suite slower on macOS), Bean 0167 (real 50 ms reader join in a test), Bean
  0386 (tests that fail together in one serial run), Bean 0403 (no full CI for bookkeeping-only commits).

## Measurement (2026-11-24, main at bb71d60c)

- Command: `uv run pytest -n auto --dist worksteal -m "not integration_test and not stress" --durations=120`, run
  locally on an 18-core macOS machine in a throwaway worktree (since removed).
- Result: 6,635 passed, 3 skipped, 78 s wall, 1,193 s summed test time.
- System time 557 s against 394 s user time, so most of the cost is real subprocesses (git repositories, process
  spawns).
- Concentration:
  - 25 cases of 5 s or more carry 21 percent of the time;
  - 130 of 2 s or more carry 45 percent;
  - 330 of 1 s or more carry 68 percent;
  - 565 of 0.5 s or more (8.5 percent of cases) carry 82 percent.

Slowest files:

| File                                                  | Summed seconds | Cases |
| :---------------------------------------------------- | -------------: | ----: |
| `tests/flow/stages/test_decomposition.py`             |           94.7 |    79 |
| `tests/test_calibrate_rerun.py`                       |           77.6 |    42 |
| `tests/test_approval_fingerprint.py`                  |           68.2 |    13 |
| `tests/flow/test_dispatch.py`                         |           64.8 |    43 |
| `tests/test_url_credential_redaction.py`              |           57.2 |    77 |
| `tests/flow/github/test_merge.py`                     |           38.5 |    58 |
| `tests/flow/stages/test_plan_decision.py`             |           32.8 |    19 |
| `tests/flow/stages/test_plan_resume_adopts_branch.py` |           29.4 |    16 |
| `tests/flow/stages/test_children.py`                  |           29.1 |    26 |
| `tests/test_resume_tip.py`                            |           23.9 |    13 |
| `tests/test_executor_run_salvage.py`                  |           21.3 |    13 |
| `tests/flow/review/test_conflict_gate.py`             |           21.2 |    29 |
| `tests/flow/test_git_refs.py`                         |           20.3 |    10 |
| `tests/test_turn_supervisor.py`                       |           19.9 |    47 |
| `tests/test_calibration_diff_property.py`             |           19.8 |    12 |
| `tests/flow/stages/test_integration.py`               |           19.6 |     5 |

Slowest single cases:

- Two property tests in `test_approval_fingerprint.py` take 32.8 s and 28.8 s.
- `test_calibration_diff_property.py::test_counted_files_are_exactly_the_pr_files` takes 15.2 s.
- The `doctor-*` parametrised cases of `test_url_credential_redaction.py` take 6 to 10.5 s each.

Finding: the pipeline runs the unit selection four times per run: unit on ubuntu, unit on macOS, and twice more inside
the "Workspace survival" job (`test-stress.yml`: once from the executor's workspace path, once more by the hermetic
canary guard under a simulated container HOME). That job runs pytest without `-n auto`, which is why it takes 7 minutes.
A later sub-flow should make that job parallel or run it only when the paths it protects change; it must wait for Bean
0403's flow because both edit `test-stress.yml`.

## Progress

- 2026-11-24: first flow `unit-suite-slowest-tests-speedup` launched (`claude-agent` / `claude-fable-5-2`), intent
  `todo/intent-0405-unit-suite-slowest-tests-speedup.json`.
- Scope: the 13 slowest test files not touched by an open pull request, plus three conftest files.
- Target: at least 60 percent less summed time for those files, with no production code change and no loss of coverage.
- Left out for now because open pull requests or running flows touch them: `test_git_refs.py`, `test_conflict_gate.py`,
  `test_calibration_diff_property.py`.

- 2026-11-25 (post-merge of PR #275, merged as `acbf790e`): first slice delivered. Scope: the 13 slowest files plus
  three conftest files; no production code change. Six tests removed as duplicates of a test that proves the same, the
  rest made cheap (shared repository fixtures, fakes for real subprocesses and sleeps). Measured with the same command
  on the same machine, median of four alternating runs: summed time of the 13 in-scope files 323.3 s to 117.6 s, a fall
  of 63.6 percent (62.0 percent counting the three test files the plan added). Target of 60 percent met. The 55.5
  percent figure in an earlier audit is the first measurement of Step 8 (235.0 s to 104.5 s), which missed the threshold
  and is superseded. Coverage 93.863 to 93.873 percent; mutants killed before are killed after.
- Still open on this bean (not closed):
  - Workspace survival job (`test-stress.yml`) still runs the unit selection twice without `-n auto` (about 7 minutes).
    Make it parallel or run it only when the paths it protects change. Waits for Bean 0403, which also edits that file.
  - Regrowth rules (goal 6): no per-test time limit in the unit suite and no review-rule note yet.
  - Test areas left out: `tests/flow/test_git_refs.py` (20.3 s), `tests/flow/review/test_conflict_gate.py` (21.2 s) and
    `tests/test_calibration_diff_property.py` (19.8 s), deferred because open pull requests or running flows touch them.
    About 870 s of the 1,193 s summed time sits outside the 13 files.
  - Targets for the pipeline (ubuntu unit about 2 minutes, macOS unit under 5 minutes) not yet re-measured on `main`.
- 2026-11-24: second slice launched, flow `workspace-survival-job-parallel` (`claude-agent` / `claude-opus-5-5`, since
  `claude-fable-5-2` is over its monthly spend limit): cut the Workspace survival job's time (two stress tests that each
  re-run the unit suite, run one after the other) without weakening either guarantee. Bean 0403 has landed (#272), so
  the shared `test-stress.yml` is free.
- 2026-11-26 (post-merge of PR #308, merged as `a8cfaf80`): second slice delivered. The two stress tests of the
  Workspace survival job now run concurrently (`-n auto --dist worksteal` in `test-stress.yml`), each with its own HOME,
  workspace, TMPDIR and basetemp (`tests/stress_support.py`; `tests/test_stress_support.py` proves they share none of
  them). The canary child runs only the modules picked by the rule in `tests/stress_selection.py`, and each child uses
  every usable CPU. Negative controls show both guards still trip. Local measurement in the CI shape: serial 276 s,
  concurrent median about 160 s (about 42 percent less). The CI job itself is not yet re-measured on `main` (run
  45725903403 in progress at merge time). The timing gate and the 'Assert the stress suite really ran' step are
  unchanged.
- Still open on this bean (stays in-progress):
  - Regrowth rules (goal 6): no per-test time limit in the unit suite and no review-rule note yet.
  - Re-measure the pipeline targets on `main` (ubuntu unit about 2 minutes, macOS unit under 5 minutes) once the
    post-merge runs finish.
  - Test areas still left out: `tests/flow/test_git_refs.py` (20.3 s), `tests/flow/review/test_conflict_gate.py` (21.2
    s) and `tests/test_calibration_diff_property.py` (19.8 s), deferred while open pull requests touched them (PR #310
    and its neighbours). About 870 s of the 1,193 s summed time sits outside the 13 files of the first slice.

## Test suite audit 2026-11-26

Measured on main `412bed21` (report: `todo/test-suite-audit-2026-11-26.md`, raw data in
`todo/test-suite-audit-2026-11-26/`; no code changed, no flow launched).

- Suite: 8,311 unit cases (+25 percent since 2026-11-24), 19 integration, 2 stress. CI on the last three main pushes:
  unit ubuntu 159 to 255 s (2 workers), unit macOS 478 to 530 s (3 workers), Workspace survival 207 to 321 s. Workers
  end within 4 s of each other: wall is summed test time / workers, no single test sets it.
- Two causes carry the time. (1) git processes: 45,157 per unit run, about 25 ms each on macOS and 5 ms on ubuntu;
  git-using files are 1,195 of 1,424 s summed on macOS. (2) A quadratic per-test fixture cost: the autouse fixtures'
  `tmp_path_factory.mktemp` lists the whole worker base temp each call; 4,200 empty tests take 56.4 s, 5.7 s with a
  constant-time numbered dir; median unit test 26 ms to 3 ms in an A/B at `-n 3`.
- Coverage per test: 866 identical-coverage groups, mostly cheap data cases; only about 25 s macOS summed is worth
  folding, and no clean deletions beyond folds were found.
- Plan, eight test-only batches with draft intents `todo/intent-0405-tests-*.json`: constant-time temp dirs (about 40 /
  38 / 35 s off ubuntu / macOS / Workspace survival), stage-pipeline git cut (11 / 45 / 11), worktree/executor (7.5 / 30
  / 7.5), calibration (7 / 25 / 7, after the calibration split), CPU-bound matrices (10 / 14 / 10), review and
  decomposition (4 / 18 / 4, after `no-unneeded-full-review`), self-doc consolidation in two parts (about 1 s, -2,400
  lines). Projected: ubuntu 250 to 170 s, macOS 512 to 339 s, Workspace survival 247 to 172 s. Running the git-heavy
  pipeline tests only on ubuntu would take macOS to about 100 to 150 s (maintainer decision, Bean 0400).
- Bug found: running a subset of files loses the `flow_repos` fixture (Bean 0491).

- Batch 1 flow started 2026-11-26 (intent `todo/intent-0405-tests-constant-time-tmp-dirs.json`, worktree
  `flow-tests-constant-time-tmp-dirs`, claude-agent / claude-opus-5-5, log
  `todo/flow-tests-constant-time-tmp-dirs.log`).
- Batch 3 flow started 2026-11-26 (intent `todo/intent-0405-tests-fewer-git-worktree-exec.json`, worktree
  `flow-tests-fewer-git-worktree-exec`, claude-agent / claude-opus-5-5, `--no-wait-on-overlap`, log
  `todo/flow-tests-fewer-git-worktree-exec.log`).
  - Result 2026-11-26: flow completed; PR #323 (`I-1795677070-tests-fewer-git-worktree-exec`) APPROVED 3/3 on 907a29c2
    (iteration 1), calibrated
    (`plans/I-1795677070-tests-fewer-git-worktree-exec/P-1795677093-CLA-CO5.5_calibration.md`), MERGEABLE/CLEAN at head
    c8fb0b0b. Execution notes measure the in-scope files at git processes 8,819 to 5,669 (-35.7%) and summed time 91.04
    s to 58.17 s (-36.1%): the 40 percent acceptance target is missed, recorded there per the plan's discard rule, not
    closed by cutting tests. CI on the head: unit macOS 553 s pytest (job 593 s, against 543 s on 907a29c2 and a 506 s
    main median); ubuntu unit and Workspace survival skipped by the bookkeeping gate (carried over the 907a29c2 real
    success: 263 s and 210 s); no CI saving shown yet. Bug logged: bean 0496 (flow log empty until exit).
- 2026-11-26 (post-merge of PR #323, merged as `b7b3bef`): batch 3 delivered. Test-only change; no production code
  changed. Git processes in the 15 in-scope files 8,819 to 5,669 (-35.7 percent); summed test time 91 s to 58 s (-36
  percent). The 40 percent target is missed, recorded as such. CI saving not yet visible: the first post-merge runs on
  `main` are not measured yet. Install step skipped (test-only change).
- Still open on this bean (stays in-progress): the remaining batches of the audit plan (batch 5
  `tests-cpu-bound-redaction-ledger` is running); regrowth rules (goal 6); re-measure the pipeline targets on `main`
  once the batches have merged.
- Batch 5 flow started 2026-11-26 (intent `todo/intent-0405-tests-cpu-bound-redaction-ledger.json`, worktree
  `flow-tests-cpu-bound-redaction-ledger`, claude-agent / claude-opus-5-5, `--no-wait-on-overlap`, log
  `todo/flow-tests-cpu-bound-redaction-ledger.log`).
  - Result 2026-11-26: PR #327 (`I-1795679415-tests-cpu-bound-redaction-ledger`) APPROVED 3/3 on 64a2ed9 (iteration 2),
    calibrated on dface60f (calibrate rerun after main merged in), CI green, MERGEABLE/CLEAN; maintainer merged it
    2026-11-26 09:38:33Z. Measured saving 27.8 percent (summed scope time 68.16 s to 49.24 s, 370 to 373 cases, git
    processes 1,319 to 1,193): NOT the 35 percent the intent requires. The whole unit selection still shows 9 failures
    in `test_stress_support.py` (out of scope per the notes). Bugs logged: bean 0503 (review approved unmet acceptance
    criteria); bean 0501 (log empty, second occurrence).
  - 2026-11-26 (post-merge of PR #327, merged as `58c66198`): test-only change; install step skipped. Batch 5 CI figures
    are not yet measured on `main`: re-measure with the next pushes. Bean stays in-progress.
- Batch 1 outcome (2026-11-26 09:19): flow completed all 5 stages, PR #325
  (`I-1795676983-tests-constant-time-tmp-dirs/...`), MERGEABLE/CLEAN at the wrapper exit, 3/3 ensemble consensus
  APPROVED (one review iteration with two findings, fixed), calibration
  `plans/I-1795676983-tests-constant-time-tmp-dirs/P-1795677012-CLA-CO5.5_calibration.md` in the PR diff. Left for the
  maintainer to merge.
- Saving, measured by the flow on a shared Linux container: empty-test run 2.5x faster (5x required), median unit test
  1.5x at `-n 2` and 1.14x at `-n 3` (3x required). The acceptance thresholds are NOT met; the flow did not claim them.
  Full-suite figures are noisy (load average 7 to 33).
- CI on the execution head 68fc39e4: `unit (ubuntu-latest)` 169 s and `unit (macos-latest)` 506 s for the
  `Run unit tests` step, against 185 to 220 s and 537 to 621 s on two main runs (45786178112, 45785970686). Two baseline
  runs only, so the saving is indicative, not measured to the 40 s / 38 s claimed.
- The final PR head 205da7f6 (calibration commit only) skipped the unit steps (bookkeeping-only push, bean 0403), so the
  green unit check there is the 68fc39e4 run. The PR body is the auto-generated summary and lacks the before/after CI
  comparison the intent asks for.
- Bug from this batch: bean 0501 (wrapper log stays empty until exit).
- 2026-11-26 (post-merge of PR #325, merged as `0fc9efa4`): batch 1 delivered (constant-time per-test temp dirs;
  test-only change, no production code). Local empty-test run 2.5x faster (5x target), median unit test 1.14 to 1.5x (3x
  target) on a noisy host: thresholds still NOT met. Single CI run on `main` shows unit ubuntu 169 s (185 to 220 s
  before) and unit macOS 506 s (537 to 621 s before). Two baseline runs only, so indicative. Install step skipped
  (test-only change). Re-measure on `main` over the next pushes before counting batch 1 as met. Bean stays in-progress.

## Batch 2 flow

- 2026-11-26: batch 2 flow started for intent `tests-fewer-git-stage-pipeline` (flow-tests-fewer-git-stage-pipeline off
  origin/main, claude-agent / claude-opus-5-5, log todo/flow-tests-fewer-git-stage-pipeline.log).
- 2026-11-26: batch 2 flow finished at the merge boundary: PR #332 (MERGEABLE/CLEAN, 3/3 APPROVED at iteration 2,
  calibration in diff, final-head CI green). Measured saving missed the 40 percent floor: in-scope git processes 12,177
  to 8,832 (-27.5 percent), summed time 125.8 s to 113.7 s (-9.6 percent, noisy; about -17 percent on quieter runs).
  Shortfall reported on the PR; not closed by cutting tests. Bug bean 0511 logged (out-of-order pytest fixture).
- 2026-11-26 (post-merge of PR #332, merged as `29fa09b3`): batch 2 delivered (test-only change; no production code).
  In-scope git processes 12,177 to 8,832 (-27.5 percent); summed time 125.8 s to 113.7 s (-9.6 percent under load, about
  -17 percent estimated on quieter runs). The 40 percent target is missed; the maintainer merged it as a partial result.
  Per-job CI saving not measured yet. Install step skipped (test-only change). Bean stays in-progress.

## Batch 7 (self-doc consolidation)

- 2026-11-26 (post-merge of PR #336, merged as `6d68e5dc`): batch 7 delivered by bean 0453 / PR #336 (26 standalone
  `test_*_self_doc.py` files consolidated into one data-driven test; test-only change). Install step skipped. Bean stays
  in-progress.

## Acceptance

- [ ] Measurement from JUnit or pytest durations lists the slowest tests and files before any removal (delivered;
      measurement of 2026-11-24 and audit of 2026-11-26).
- [ ] The 13 slowest files are made cheap with at least 60 percent less summed time and no coverage loss (delivered by
      PR #275).
- [ ] The Workspace survival job runs its stress tests concurrently (delivered by PR #308).
- [ ] Batch 1, constant-time per-test temp dirs, merged (delivered by PR #325); its CI saving is re-measured on `main`.
- [ ] Batch 2, fewer git processes in the stage pipeline tests, merged (delivered by PR #332).
- [ ] Batch 3, fewer git processes in worktree and executor tests, merged (delivered by PR #323).
- [ ] Batch 5, CPU-bound redaction and ledger tests, merged (delivered by PR #327).
- [ ] Batch 7, self-doc test consolidation, merged (delivered by PR #336).
- [ ] The remaining audit batches (calibration tests after the calibration split; review and decomposition tests after
      `no-unneeded-full-review`; self-doc consolidation part two) are delivered, each test-only with before and after
      timings.
- [ ] Test areas deferred earlier (`test_git_refs.py`, `test_conflict_gate.py`, `test_calibration_diff_property.py`) are
      cleaned up.
- [ ] Line and branch coverage do not fall, and the mutation score of touched modules does not fall.
- [ ] Regrowth rules: a per-test time limit in the unit suite, and a review-rules note that a finding is answered by
      strengthening an existing test where one exists.
- [ ] Pipeline targets re-measured on `main`: `unit (ubuntu-latest)` about 2 minutes, `unit (macos-latest)` under 5
      minutes.
- [ ] The suite size is reported in each pull request so growth is visible.
- [ ] The module budget file is not changed.

## Assumptions

- Targets stay as written until confirmed by the measurement. Validated by re-measuring on `main` after the batches
  merge.
- Batches that missed their percentage floor (3, 5, 2, 1) count as delivered because the maintainer merged them as
  partial results. Validated by the progress notes.

## Deferred areas batch (`2026-11-27`)

- Launched `tests-deferred-three-speedup` (`todo/intent-0405-tests-deferred-three-speedup.json`,
  `todo/intent-coverage-0405.json`) targeting the three deferred files `tests/flow/test_git_refs.py`,
  `tests/flow/review/test_conflict_gate.py`, and `tests/test_calibration_diff_property.py` (test-only).
- Launched `tests-fewer-git-calibrate` (`todo/intent-0405-tests-fewer-git-calibrate.json`,
  `todo/intent-coverage-0405.json`) targeting the 10 disjoint calibration test files (plus optional helper
  `apps/sandbox-executor/tests/calibrate_scenarios.py`, test-only, excluding `test_calibration_diff_property.py`).
- Launched `tests-fewer-git-review-decomp` (`todo/intent-0405-tests-fewer-git-review-decomp.json`,
  `todo/intent-coverage-0405.json`) targeting the 5 disjoint review/decomposition/fingerprint test files (test-only,
  excluding `test_conflict_gate.py`).
