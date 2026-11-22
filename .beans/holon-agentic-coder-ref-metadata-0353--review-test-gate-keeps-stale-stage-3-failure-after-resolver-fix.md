---
# holon-agentic-coder-ref-metadata-0353
title: "_ReviewTestGate keeps stale Stage 3 tests_failed after Stage 4 resolver fixes and green CI"
status: scrapped
type: bug
priority: high
tags:
  - holon-agentic-coder
  - review-loop
  - ci
  - tests
created_at: 2026-11-21T05:09:38Z
updated_at: 2026-11-22T22:55:00Z
---

## Problem

When Stage 3 (`execute`) completes with failing tests (`test_exit_code != 0` or `test_pass_rate < 1.0`) and Stage 4's
resolver subsequently fixes those test failures on a newer commit where all GitHub Actions CI checks pass (`11/11`),
Stage 4 never exits with consensus `APPROVED`. Instead, it gets trapped in an infinite loop generating synthetic
`FIND-CI-NNN` (`CI checks failed in iteration N: local_tests.`) findings until `max_review_iterations` is exhausted.

Observed directly on **Bean 0322** (PR `#222`) across 9 consecutive review iterations (iterations 7–15):

- Iteration 4 resolver fixed the 2 failing test assertions (`4944 passed, 1 skipped` locally) and pushed.
- Iterations 7–15 each had all 3 reviewers (`claude-agent / claude-opus-5-5`) unanimously return
  `APPROVED (critical 0, important 0, nit 0)` AND `CI Checks: 11 total, 11 passed, 0 failed, 0 pending (github_cli)`.
- Yet Stage 4 kept emitting `FIND-CI-007` through `FIND-CI-015`
  (`summary: "CI checks failed in iteration N: local_tests."`), forcing another full ensemble review each iteration
  after the resolver rejected `FIND-CI-NNN` as `inaccurate`.
- **Bean 0190** (PR `#219`) hit the exact same trap at Iteration 6 (`APPROVED` + `11/11` CI green, yet continued into
  Iteration 7 because its Stage 3 payload recorded `test_exit_code: 1`, `tests_failed: 6`).

### Root Cause

1. In `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py` (`line 206`),
   `_ReviewTestGate(context, repo_dir)` caches
   `self.stage_3_evidence = (rate, exit_code != 0 or (rate is not None and rate < 1.0))` once from
   `context.stage_results.get("execute")`.
2. In `apps/sandbox-executor/src/sandbox_executor/flow/review/local_tests.py`:
   - `_applies(ci_status, stage_3_rate, stage_3_failed)` returns `True` **only** when
     `ci_status.get("source") == "local_tests" and stage_3_rate is None and not stage_3_failed`.
   - Whenever Stage 3 failed (`stage_3_failed == True`) OR GitHub CLI CI checks are present (`source == "github_cli"`),
     `evidence()` never updates or clears `tests_failed` — it returns the frozen Stage 3 `(rate, True)` tuple forever.
3. In `apps/sandbox-executor/src/sandbox_executor/flow/review/ci_outcome.py` (`gate_ci_flags`) and
   `apps/sandbox-executor/src/sandbox_executor/flow/github/ci.py` (`_ci_green`), `tests_failed == True` overrides
   `ci_status.get("all_passed") is True`, setting `ci_green = False` and `ci_finding = True`
   (`FIND-CI-{iteration:03d}`).

## Action

Through the 5-stage Holon flow on `holon-agentic-coder`:

1. Update `_ReviewTestGate` in `apps/sandbox-executor/src/sandbox_executor/flow/review/local_tests.py` (and any call
   sites in `loop.py` if needed):
   - When `ci_status.get("source") == "github_cli"`, authoritative CI on the current PR HEAD has already run: stale
     Stage 3 `tests_failed` MUST NOT fail `_ci_green` / `gate_ci_flags` (use the `github_cli` outcome rather than a
     frozen earlier-HEAD failure).
   - When `ci_status.get("source") == "local_tests"` and the current `HEAD` differs from the Stage 3 execution commit
     (e.g. a Stage 4 resolver committed fixes, or `test_gate` has not yet measured `HEAD`), re-measure tests on the
     current `HEAD` via `_ReviewLocalTests` instead of reusing stale Stage 3 failure evidence.
2. Preserve existing behavior when `github_cli` is absent AND `HEAD` has not advanced since Stage 3 (so Stage 3 local
   test results still gate Stage 4 without redundant test runs on the same commit, and unmeasured runs stay unmeasured).
3. Add hermetic unit tests in `apps/sandbox-executor/tests/flow/` covering:
   - Stage 3 failed (`test_exit_code = 1`, `tests_failed > 0`), resolver pushes a fix, `github_cli` reports
     `all_passed = True` -> `evidence()` / `gate_ci_flags()` / review loop approves without synthesizing `FIND-CI-NNN`
     for `local_tests`.
   - Stage 3 failed, `ci_status["source"] == "local_tests"`, and `HEAD` advanced past Stage 3 -> `_ReviewTestGate`
     re-measures on the new `HEAD` and clears `tests_failed` if tests pass.
   - Stage 3 failed, `ci_status["source"] == "local_tests"`, and `HEAD` is unchanged -> `tests_failed` still fails the
     gate without re-running.

## Acceptance Criteria

- Stage 4 consensus `APPROVED` + `11/11` passing `github_cli` checks completes immediately in the same iteration even
  when Stage 3's initial `execute` checkpoint recorded `test_exit_code != 0`.
- When running without `github_cli` (`local_tests`), advancing `HEAD` in Stage 4 invalidates stale Stage 3
  `tests_failed` evidence by measuring on the new `HEAD`.
- All existing and new tests pass via `uv run pytest`, and `uv run task lint` and `uv run task lint-docs` pass.
- `holon-config/hygiene/module_budgets.json` is unchanged.

## Notes

- Target repository: `Holon-Agentic-Coder/holon-agentic-coder`
- Related beans: `0235`, `0238`, `0267`, `0322`, `0190`.

## Resolution

Superseded as a duplicate of **Bean 0354**, which tracks the exact same `_ReviewTestGate` stale Stage 3 failure bug in
`flow/review/local_tests.py` and is currently in progress in `holon-agentic-coder`
[PR #230](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/230) (`flow-review-approved-and-fresh-tests`,
implementing `flow/review/head_test_evidence.py` and updated `flow/review/local_tests.py` covering green `github_cli` CI
on the PR head, local re-measurement on moved heads, unchanged Stage 3 head reuse, and hermetic tests).
