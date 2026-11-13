---
# holon-agentic-coder-ref-metadata-0293
title: "Tests that patch time.sleep patch only the module under test, so unrelated subprocesses cannot trip them"
status: completed
type: bug
priority: high
tags:
  - tests
  - flakiness
  - holon-agentic-coder
created_at: 2026-11-13T11:00:00Z
updated_at: 2026-11-13T11:00:00Z
---

## Problem

Several tests patch `time.sleep` for the whole process (for example
`patch("sandbox_executor.flow.github.ci.time.sleep", sleep)` replaces the `time` module's own `sleep`) and assert it is
never called. Any real subprocess started during such a test makes `subprocess` poll its child with `time.sleep` (delays
0.001, 0.002 ... 0.05 s) whenever the child outlives the first poll, which happens in the review-loop container but
rarely on a host. The assertion then fails with a thousand "calls". Seen three times in two days, each with a different
real subprocess:

- PR #184: `calibrate_sync.record_starting_branch` ran a real `git symbolic-ref` inside `run_review_stage`.
- PR #187: `_ReviewLocalTests._head` ran a real `git rev-parse HEAD` inside `run_review_loop`.

Each halted the resolver's pre-push verification, cost several review iterations and needed a hand edit.

## Goal

1. Replace every process-wide `time.sleep` patch in the tests with a patch of the module under test's own reference, for
   example
   `patch("sandbox_executor.flow.github.ci.time", <proxy whose sleep is the mock and everything else wraps the real module>)`,
   so `subprocess`, `threading` and the ledger lock keep the real clock.
2. Add a shared test helper for it, and a lint-level check (a test) that fails when a test patches `time.sleep` through
   `...time.sleep` on a real module.
3. Keep the assertions' meaning: "this code path never sleeps".
4. Tests pass in the review-loop container image (`uv run task test` there), not only on a host; `uv run pytest`,
   `uv run task lint` and `uv run task lint-docs` pass.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths.
- Touches test files only (`tests/flow/github/test_ci.py` and the other files that patch sleep).
- Related: Bean 0267 and Bean 0253, where the hand edits were made.

## Resolution (completed, 2026-11-13)

Delivered by flow `sleepfix` as holon-agentic-coder PR #188, merged 2026-11-13T11:39:39Z (merge commit `54bfd55`, review
`PRR_kwDORMmd1c8AAAABXxGQPQ`). Calibration report
`plans/P-1794567531-a466a71e-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
+15.74 (actual 50.44). Tests that patch `time.sleep` now patch only the module under test, with a shared helper and a
test that enforces it.
