---
# holon-agentic-coder-ref-metadata-0269
title: "Deferred nits from the holon-agentic-coder PR 158 review loop"
status: todo
type: task
priority: low
tags:
  - review-loop
  - calibration
  - holon-agentic-coder
created_at: 2026-11-10T00:00:00Z
updated_at: 2026-11-20T14:20:00Z
---

## Deferred findings

Collected by the PR 158 review loop (principle 12 deferral bean). Each was a Nit on code the increment did not change.

- `parse_actual_metrics` gives exit code 1 and `_record_exit_code` gives 0 for a non-integrated `decomposed` row;
  p_success is 0 in both, so no score differs. Fold both onto `_record_exit_code` to remove the duplicate logic
  (iteration 4 dry run, out of increment).
- The removed-definitions consistency test cannot prove the removed key ever existed in the original `flow.py`
  (iteration 5 ensemble, out of increment).
- `docs/git_flow.md:295` says an exception 'keeps the recorded progress', which no longer holds when the checkpoint save
  itself fails (iteration 6, out of increment).

## Audit (2026-11-21)

Re-checked. Item 1 still valid (`calibration.py` around line 772 keeps its own exit-code logic while
`calibration_outcome.record_exit_code` exists; fold them together). Item 2 is obsolete: `flow.py` is gone and no
removed-definitions consistency test exists. Item 3 still valid: `docs/git_flow.md` around line 384 still says Stage 3
keeps the recorded progress. The `flow.py` references above are stale.
