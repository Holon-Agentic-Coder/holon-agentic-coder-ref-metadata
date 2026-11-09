---
# holon-agentic-coder-ref-metadata-0267
title:
  "Stage 3 records a measured `test_pass_rate` (and the review loop can measure tests itself) so the flow does not
  depend on CI alone"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - review-loop
  - testing
  - holon-agentic-coder
created_at: 2026-11-09T11:30:00Z
updated_at: 2026-11-09T11:30:00Z
---

## Problem

`docs/git_flow.md` says Stage 3 "carries the executor container's recorded `test_pass_rate` from its `executions.jsonl`
summary row", and that Stage 4 withholds consensus when tests are unmeasured
(`test results not measured: no recorded Stage 3 test result and no CI checks`). In practice nothing produces that
value:

- `entrypoint/executor.py` never runs the project's tests and never writes a `test_pass_rate`. The only consumers are
  `flow/stages/execute.py`, `flow/stages/review.py`, `flow/review/loop.py` and `calibration.py`.
- In the committed `holon-knowledge/ledger/executions.jsonl`, `"test_pass_rate"` is `null` in **51 of 54** rows that
  carry the field and `1.0` in only **3**.

So every flow so far has been approved on CI evidence alone. When CI does not run, as for the stacked sub-intent PR #152
during the Bean 0262 flow (all three reviewers approved at iteration 5), the flow fails with "test results not
measured", even if the executor and resolver ran the full suite inside their containers. Bean 0266 fixes the specific
trigger (CI skipped on pull requests into non-`main` branches), but the flow should not have a single point of failure
for the question "do the tests pass?".

## Goal

1. **Measure in Stage 3.** After the executor agent's turn and before the execution commit is pushed, the executor
   entrypoint runs the project's test task (`uv run task test`, as the resolver's pre-push verification already does,
   with `uv` now in the image) and records the result in its `executions.jsonl` summary row: `test_pass_rate` in
   `[0, 1]` (passed over passed plus failed plus errored, from the pytest summary), plus `tests_passed`, `tests_failed`,
   `tests_errored` and the exit code. A run that cannot execute the tests (missing tool, timeout) records `null` for the
   rate and an explicit `test_run_error`, never a pass. Redact all captured output.
2. **Never read a missing measurement as a pass.** Keep the existing rule that `null` means "not measured". A measured
   rate below `1.0`, or a non-zero exit code, is a failed test result and Stage 3 and Stage 4 treat it as such.
3. **Let the review loop measure when CI cannot.** When no CI checks register and Stage 3 recorded no rate, the loop's
   `local_tests` fallback runs the test task in the review container and records the result, instead of reporting
   `NOT_MEASURED` immediately. The result is attributed to its source (`stage_3`, `ci` or `review_local`) in the review
   rows and the posted summary.
4. **Calibration uses it.** `calibration.py` already reads `test_pass_rate`; confirm it uses the new measured value and
   add a test.
5. **Tests and docs.** Hermetic tests for: a passing run recording `1.0`; a failing run recording the real fraction and
   a non-zero exit code; a run that cannot execute tests recording `null` plus `test_run_error`; the review-loop
   fallback producing a measurement when no CI registers; and a measured result never being treated as unmeasured.
   Update `docs/git_flow.md`, `docs/ledger_schema.md` and `docs/sandbox/execute_plan.md` to match what is now recorded.
6. **Constraints**: `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies; the
   three-ledger invariant is kept (the fields go on the existing summary row).

## Sequencing

- Independent of Bean 0266 (`.github/workflows/`, `flow/github/`); touches `entrypoint/executor.py`,
  `flow/stages/execute.py`, `flow/stages/review.py`, `flow/review/loop.py` and the docs. Hold behind PR #152's flow:
  Bean 0262 also edits `flow/review/` and `entrypoint/review_loop.py`. Run it after Bean 0262 lands, or when no other
  flow is touching those files.
- Bean 0262 (bind-mounted host worktree) makes the loop-side measurement cheaper, since the review container then works
  in the mounted worktree.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.
