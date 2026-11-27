---
# holon-agentic-coder-ref-metadata-0596
title: "Stage 4/5 gate: the PR diff must stay inside the intent scope"
status: todo
type: task
priority: high
tags:
  - review-loop
  - scope
  - invariants
  - holon-agentic-coder
created_at: 2026-11-27T00:57:56Z
updated_at: 2026-11-27T01:07:06Z
---

## Evidence

- PR #360 (bean 0549) merged with 16 files outside the intent scope, changed by the review-loop resolver (for example
  `outcome.py`, `model_tiers.py`, `review/loop.py`, `conftest.py`, `test_uv_lock.py`).
- The Stage 3 touch-set check exists (it refused flow 0572 with `touch_set_violation`), but nothing checks resolver
  commits.
- PR #357 (bean 0546) also added 3 out-of-scope helper modules.
- Related: beans 0546 (intent-check misses real scope escapes), 0562 (every invariant has an explicit check), 0573
  (invariant registry). Ledger: CF-0031, CF-0032 (renumbered from CF-0020/0021).

- PR #380 (bean 0549 Stage 5 remainder) merged with 3 files outside its intent scope: `failure_classification.py`,
  `flow/github/stage5_test_failure.py`, `flow/lazy_exports.py` (the scope listed only `test_failure_record.py`,
  `ci_reverify.py`, `wisdom.py` and two test files).

## Goal

No flow PR reaches calibration or merge with files outside its intent scope that were not explained by a recorded
re-plan.

## Design

- The resolver's changes are checked against the plan touch set exactly as Stage 3 does; a violating commit is refused.
- Widening the touch set requires a recorded re-plan (appended to the plans ledger) before the resolver may edit the
  extra file.
- Stage 5 refuses calibration when the PR diff has unexplained out-of-scope files.
- Readiness checks list every out-of-scope file in the PR diff.
- The scope rule is registered in the invariant registry (0573) with an explicit check (0562).

## Acceptance

- [ ] Resolver commits touching a file outside the plan touch set are refused with `touch_set_violation`.
- [ ] A recorded re-plan that widens the touch set lets the same file through.
- [ ] Stage 5 refuses calibration when the PR diff has an out-of-scope file without a re-plan.
- [ ] The readiness check lists out-of-scope files.
- [ ] Tests use PR #360's file list (outcome.py, model_tiers.py, review/loop.py, conftest.py, test_uv_lock.py and the
      other 11 files) against bean 0549's scope and fail before the change, pass after.
- [ ] Code has no docstrings and no comments except `# why:`; run with `uv run pytest`.
