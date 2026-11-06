---
# holon-agentic-coder-ref-metadata-0235
title: "Stage 4 CI is a post-review gate: launch reviewers immediately without waiting for pending CI"
status: completed
type: bug
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - ci
  - holon-agentic-coder
created_at: 2026-11-06T00:06:30Z
updated_at: 2026-11-06T04:35:00Z
---

## Problem

In `sandbox_executor.flow.run_review_loop()`, step 2 (`probe_ci_checks()` + `_wait_for_pending_ci()`) currently executes
**before** step 3 (`_dispatch_review_ensemble()` / `_ensemble_iteration()`), and `_wait_for_ci_registration()` also
blocks before iteration 1 starts.

Consequently, every Stage 4 review iteration blocks for 5–10 minutes (`Waiting for N pending GitHub CI check(s)...`)
before launching a single reviewer agent:

1. **Violates `pr-review-loop` Doctrine ("CI is a gate, not a waiting room")**: In
   `.agents/skills/pr_review_loop/SKILL.md`, reviews start immediately as soon as a push lands. Waiting on pending CI
   while code findings may exist wastes wall-clock time because the resolver's push will immediately supersede that CI
   run.
2. **Eliminates Natural Parallelism**: Running the reviewer ensemble takes several minutes. Launching reviewers
   immediately allows GitHub Actions CI to run in parallel with the LLM review passes rather than serially before them.
3. **Redundant Double Waiting**: When the host engine dispatches the `review-loop` role container, blocking on CI prior
   to container dispatch delays the container launch completely.

## Decision

Align Stage 4 CI handling in `run_review_loop()` with the `pr-review-loop` skill: **CI is a gate after a clean review,
never a pre-review waiting room.**

1. **Immediate Reviewer Launch**:
   - After the empty-diff guard, PR creation/update, and mergeability check, dispatch the reviewer pass immediately
     without waiting for CI registration or pending CI checks.
2. **Non-Blocking Fast Path When Reviewers Flag Findings (`CHANGES_REQUESTED`)**:
   - If the reviewers report any open Critical, Important, or actionable Nit findings, do **not** wait for pending CI
     checks.
   - Probe current CI state once without blocking: if any CI check has _already_ failed, include
     `FIND-CI-{iteration:03d}` alongside the reviewer findings; if checks are still pending, ignore the pending state
     and hand the reviewer findings straight to the resolver so it can fix and push immediately.
3. **CI Gate When Reviewers Return Clean (`APPROVED`)**:
   - Only when all reviewers return `APPROVED` (zero Critical, zero Important, zero open actionable Nit findings) and
     the branch is mergeable/clean, evaluate the CI gate:
     - If no CI checks have registered yet and local test evidence was not recorded, run `_wait_for_ci_registration()`.
     - If CI checks are still `pending`, run `_wait_for_pending_ci()` until all checks settle or the iteration timer
       expires.
     - If all CI checks pass (`ci_green is True`), `decide_consensus()` returns `APPROVED` and the loop exits cleanly.
     - If any CI check fails, record `FIND-CI-{iteration:03d}` and dispatch the resolver to fix the CI failure.

## Scope

1. **Reorder Review & CI Gate in `apps/sandbox-executor/src/sandbox_executor/flow.py`**:
   - Move `_wait_for_ci_registration()` and `_wait_for_pending_ci()` out of the pre-review path and into the post-review
     gate (executed only when the reviewer ensemble has zero open findings, or when evaluating final consensus after
     reviewers complete).
   - Ensure already-failed CI checks at the time reviewers finish still attach `FIND-CI-{iteration:03d}` for the
     resolver even when reviewers also had findings.
2. **Hermetic Unit Tests (`apps/sandbox-executor/tests/test_flow.py` & `test_review_loop.py`)**:
   - Verify that when reviewers return `CHANGES_REQUESTED` while CI checks are `pending`, `_wait_for_pending_ci` is
     **not** called (zero sleep calls) and the resolver is dispatched immediately with the reviewer findings.
   - Verify that when reviewers return `APPROVED` (0 findings) while CI checks are `pending`, `_wait_for_pending_ci`
     waits for CI to settle before deciding consensus (`APPROVED` if green, or `FIND-CI-NNN` -> resolver if red).

## Notes

- Target repository: `holon-agentic-coder`.
- Must be executed through the 5-stage Holon flow (`holon flow`).
- Pairs naturally with Bean 0234 (event-driven CI check progress reporting when the post-review CI gate does wait).

## Resolution

- Implemented in `holon-agentic-coder` via `holon flow` across Intent `I-1793932288-...`, Plan `P-1793932304-...`, and
  Execution `E-1793936727-...`.
- Restructured `run_review_loop()` in `sandbox_executor.flow` so the reviewer ensemble is launched immediately following
  PR mergeability checks.
- Bypassed pending CI waiting when reviewers object (`CHANGES_REQUESTED`), passing reviewer findings straight to the
  resolver without delay.
- Enforced post-review CI gating only when reviewers return clean `APPROVED` with zero open findings.
- Added comprehensive hermetic unit tests in `test_review_loop.py` and `test_flow.py`.
- Passed Stage 4 ensemble review, completed Stage 5 calibration ($\Delta\text{EV} = +10.93$, predicted `82.41`
  $\rightarrow$ actual `93.34`), and merged into `main` via PR
  [#128](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/128) (`f8220eb`).
