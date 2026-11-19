---
# holon-agentic-coder-ref-metadata-0316
title: "macOS unit CI timing gate trips on runner noise and blocks Stage 5"
status: completed
type: bug
priority: high
tags:
  - ci
  - timing-gate
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-17T10:00:00Z
updated_at: 2026-11-19T10:28:01Z
---

## Problem

The `unit (macos-latest)` job's CI Timing Gate (`scripts/check_ci_runtime_budget.py`, budget 300 s) fails on runner
speed alone. The same code swings by more than 100 s between runs, so a head whose only new commits are calibration
bookkeeping goes red, the consensus approval is withdrawn ("approval no longer stands") and Stage 5 refuses the final
head.

Seen on 2026-11-17:

- PR #204: head `f4a2a4d` (calibration commits only) failed at 332.0 s; the same code passed at 235 s three hours
  earlier, and a rerun of the failed job passed (4m49s job).
- PR #203: head `1028afe` (calibration commits only) failed at 312.7 s, then 370.2 s and again on a third attempt (5m28s
  job); the code head below it passed with a 280 s test step. All 4,287 tests passed each time. The one test file the PR
  adds runs in 11.6 s serially.
- `main` itself last ran the job in 306 s; the touchset PR tripped the gate at 317 s and 339 s.

## Goal

1. The macOS unit job stops failing on runner variance: either the suite gets real headroom under the budget on macOS
   (the ubuntu job runs the same suite in about 2 minutes) or the gate measures something that does not swing with the
   runner (test-step time against a per-OS budget, or a comparison with the base branch's time on the same runner
   class).
2. A timing-gate failure on a head that adds only ledger, plan and knowledge-base files does not withdraw a consensus
   approval or fail Stage 5's final-head CI check without one automatic rerun of the failed job.
3. The gate stays fail-closed for a real regression: a change that slows the suite is still refused.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths.
- Touch set: `.github/workflows/test-unit.yml`, `scripts/check_ci_runtime_budget.py`, the Stage 5 final-head CI check
  (Bean 0292) and the approval-invalidation path. Overlaps Bean 0297 (PR #203); run after it.
- Related: Bean 0168 (CI test time), Bean 0166 (pipeline duration dashboard), Bean 0292 (final-head CI check).

## Resolution

Delivered via [PR #205](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/205) and merged into `main`
(`3d10c28`), flow slug `macgate`:

- **Key Architectural Deliverables**: the macOS timing gate now compares the PR's test-step time with the base branch's
  time on the same runner class, under a 600 s ceiling, instead of a fixed 300 s budget
  (`.github/workflows/test-unit.yml`). A timing failure on a head that adds only bookkeeping files (ledger, plan,
  knowledge base) gets one automatic rerun of the failed job before the final-head CI check or the consensus approval is
  withdrawn (`ci_final_head.py`, `ci_reverify.py`, `approval_invalidation.py`). The Stage 5 verdict and the invalidation
  comment report the rerun.
- **Scope note**: the PR also changed `apps/sandbox-executor/flow_module_budgets.json`, which is outside this bean's
  stated touch set. `scripts/check_ci_runtime_budget.py` was not changed.
- **Verification & Tests**: hermetic tests added for the relative gate thresholds, the rerun semantics and the timing
  rerun (`test_ci_timing_gate.py`, `test_final_head_timing_rerun.py`, `test_ci_reverify.py`,
  `test_approval_invalidation.py`). Full suite, lint and docs-lint passed at execute step 6.
- **Holon Flow Traversal**: all 5 stages completed. Review approved 3/3 at iteration 3 (three nits at iteration 2, all
  applied). Calibration report `plans/P-1794976517-cac841ef-claude-agent-claude-fable-5_calibration.md`: predicted EV
  34.25, actual 60.61 (delta +26.36).
