---
# holon-agentic-coder-ref-metadata-0237
title: "Increase default review_iteration stage budget from 15 minutes to 120 minutes (2 hours)"
status: completed
type: task
priority: high
tags:
  - budgets
  - review-loop
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-06T00:12:30Z
updated_at: 2026-11-06T02:25:00Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/budgets.py`, `StageBudgets.review_iteration` is currently set to `900.0`
seconds (15 minutes), compared to `2700.0` seconds (45 minutes) for `execute`:

```python
@dataclass(frozen=True)
class StageBudgets:
    """Per-stage wall-clock ceilings in seconds."""

    intent: float = 600.0
    plan: float = 2100.0
    execute: float = 2700.0
    review_iteration: float = 900.0
    calibration: float = 600.0
```

A 15-minute ceiling for a review iteration is far too small now that Stage 4 executes:

1. **Three independent blind reviewer agent turns** (`ensemble_size=3`) in the `review-loop` container, each analysing
   the full diff with deep-thinking models (such as `gemini-4-argon` or `claude-fable-5` / `claude-opus-5-5`).
2. **A native resolver pass** (Bean 0229) when findings are reported — which clones the repo, applies code fixes, runs
   `uv run task lint` and `uv run pytest` across ~3,000 tests, commits, and pushes.
3. **GitHub CI gate checks** ( ~5–10 minutes on GitHub Actions runners).

Consequently, a single review+resolve iteration routinely takes longer than Stage 3 execution itself, and a 15-minute
`review_iteration` budget causes premature stage budget breaches mid-review or mid-resolution.

## Decision

Increase the default `review_iteration` stage budget in `StageBudgets` from `900.0` seconds (15 minutes) to `7200.0`
seconds (120 minutes / 2 hours) — larger than `execute` (`2700.0`s / 45 min) and sufficient for a full 3-reviewer
ensemble pass, native resolver pass (with full test suite execution), and CI gate within a single iteration.

## Scope

1. **Update Default Constant (`apps/sandbox-executor/src/sandbox_executor/budgets.py`)**:
   - Change `StageBudgets.review_iteration` from `900.0` to `7200.0` (120 minutes / 2 hours) and update module docstring
     references.
2. **Update Unit & CLI Tests**:
   - Update assertions in `apps/sandbox-executor/tests/test_budgets.py`, `apps/sandbox-executor/tests/test_cli.py`, and
     any flow/review tests asserting the default `900`s / `15m` review iteration budget to `7200`s / `120m`.
3. **Update Documentation**:
   - Update `docs/budgets.md` and any CLI help/docs citing the 15-minute `HOLON_STAGE_BUDGET_REVIEW_ITERATION_MINUTES`
     default to 120 minutes.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be delivered through the 5-stage Holon flow (`holon flow`).

## Completed (2026-11-06)

Delivered end-to-end via `holon flow` on `antigravity-agent` / `gemini-4-argon`: intent
`I-1793925076-increase-default-review-iteration-stage-budget-to-2-hours`, plan
`P-1793925096-antigravity-agent-gemini-4-argon`, execution `E-1793925366-antigravity-agent-gemini-4-argon`, PR #127,
merged as `6b9264c`. Updated `StageBudgets.review_iteration = 7200.0` (120 minutes) in `sandbox_executor.budgets` and
updated unit/flow tests in `test_budgets.py` and `test_flow.py`. Passed Stage 4 review and completed Stage 5 calibration
(`plans/P-1793925096-antigravity-agent-gemini-4-argon_calibration.md`, predicted EV 68.89 vs actual EV 72.69,
$\Delta\text{EV} = +3.80$).
