---
# holon-agentic-coder-ref-metadata-0257
title:
  "Stage 5 calibration matches REV-... summary rows on plan_branch and treats status='halted_for_human' as
  p_success=0.0, producing false negative Actual EV"
status: todo
type: bug
priority: high
tags:
  - calibration
  - stage-5
  - ledger
  - metrics
  - holon-agentic-coder
created_at: 2026-11-09T13:16:30Z
updated_at: 2026-11-09T13:16:30Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/calibration.py` (`compute_actual_metrics`, around lines 744–789):

```python
if (execution_id and rec_exec_id == execution_id) or (
    plan_branch and rec_plan_branch.rstrip("/_") == plan_branch.rstrip("/_")
):
    rev = int(record.get("ledger_revision", 1))
    if best_record is None or rev >= best_rev:
        best_record = record
        best_rev = rev
...
if best_record is not None:
    exec_meta = best_record
    status = best_record.get("status", "success")
    actual.exit_code = 0 if status == "success" else int(best_record.get("exit_code", 1))
    actual.p_success = 1.0 if status == "success" and actual.exit_code == 0 else 0.0
```

In `holon-knowledge/ledger/executions.jsonl`, **both** Stage 3 execution summary rows (`execution_id: "E-..."`) and
Stage 4 review loop summary rows (`execution_id: "REV-..."`) have `"entry_type": "summary"` and carry the exact same
`"plan_branch"` value:

1. Because the Stage 4 review loop runs _after_ Stage 3 execution and appends its `"entry_type": "summary"` record
   (`REV-...`) at the end of `executions.jsonl` with the same `plan_branch` and default `ledger_revision = 1`, the loop
   condition `or (plan_branch and rec_plan_branch.rstrip("/_") == plan_branch.rstrip("/_"))` with `rev >= best_rev`
   **overwrites** the `E-...` execution summary row with the later `REV-...` review summary row!
2. When Stage 4 reaches consensus approval and stops at the mandatory human-merge safety boundary, the `REV-...` summary
   row records:
   ```json
   {
     "execution_id": "REV-1794190123-antigravity-agent",
     "status": "halted_for_human",
     "summary": "Review Loop reached consensus approval after 5 iteration(s) (human-only merge safety halt)"
   }
   ```
   Or if an earlier review pass halted and was resumed, an intermediate `REV-...` row has `"status": "failed"`.
3. `compute_actual_metrics()` checks `status == "success"` (`"halted_for_human" != "success"`), sets
   `actual.p_success = 0.0` and `actual.impact = 0.0` (`predicted.impact if actual.p_success > 0.5 else 0.0`), and
   computes a **false negative Actual EV** (e.g. `Actual EV = -8.48`, `ΔEV = -83.36` on PR #146 despite 100% test pass,
   3/3 unanimous review approval, and successful execution)!

## Decision

1. **Filter Execution Summary Lookup to Stage 3 `E-...` Records When `execution_id` Starts with `E-`**:
   - In `compute_actual_metrics()`, when `execution_id` is provided, prefer exact `rec_exec_id == execution_id` matches
     over `plan_branch`-only matches, and ignore `REV-...` review loop summary records when resolving the Stage 3
     execution summary (or inspect `REV-...` records separately only to confirm review consensus).
2. **Recognise `"halted_for_human"` Consensus Approval as Successful Outcome**:
   - If a review summary or execution record carries `status == "halted_for_human"` (the canonical Stage 4 consensus
     approval safety halt), treat it as a successful outcome (`exit_code = 0`, `p_success = 1.0`) rather than a failure.

## Scope

1. `apps/sandbox-executor/src/sandbox_executor/calibration.py`:
   - Update `compute_actual_metrics()` so `REV-...` summary rows on the same `plan_branch` do not clobber the matched
     `E-...` execution summary row, and treat `"halted_for_human"` as a non-failing status.
2. `apps/sandbox-executor/tests/test_calibration.py` (or a dedicated calibration test module):
   - Add a regression test with `executions.jsonl` containing an `E-...` summary row (`status: "success"`) followed by
     `REV-...` summary rows (`status: "failed"` from an earlier iteration and `status: "halted_for_human"` on consensus
     approval) sharing the same `plan_branch`, verifying `actual.p_success == 1.0`, `actual.impact == predicted.impact`,
     and positive `actual.ev`.
