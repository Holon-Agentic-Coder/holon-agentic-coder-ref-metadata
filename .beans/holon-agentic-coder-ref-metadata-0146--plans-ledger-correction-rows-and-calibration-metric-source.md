---
# holon-agentic-coder-ref-metadata-0146
title: "Define plans-ledger correction rows and make calibration pick the right predicted metrics"
status: todo
type: bug
priority: medium
tags:
  - ledger
  - calibration
  - planner
  - provenance
created_at: 2026-10-23T16:10:00Z
updated_at: 2026-10-23T16:10:00Z
---

## Problem

Found in the Stage 4 review of holon-agentic-coder PR #91 (Bean 0135), iteration 1, finding IMP-1:

- `planner.parse_metrics()` let the **last** matching metrics table row win, so the committed `plans.jsonl` row for
  `P-1792765112-claude-agent-claude-opus-5-5` carries Step 5's metrics (p_success 0.9, entropy 0.4, impact 10.0, cost
  2.0, learning_value 1.0, EV 7.38) instead of the plan's `## Overall Plan Metrics` (0.80 / 5.8 / 85.0 / 16.0 / 4.0, EV
  52.26). The parser itself is fixed on the PR #91 branch (commit `ca6cecc`, scoped to the Overall section with two
  regression tests), so future rows are right.
- The wrong row is append-only provenance and cannot be rewritten. `calibration.py:583-601` `parse_predicted_metrics()`
  takes the **first** matching `plans.jsonl` row and has no `ledger_revision` selection for plans rows, so even an
  appended corrected row would be ignored, and `docs/ledger_schema.md` defines no plans-row correction type.
- Related (PR #91 NIT-1): one execution carries two contradictory terminal summary rows (`halted_for_human` then
  `success`), out of chronological order -- the harness `E-` summary `created_at` uses the stage start time while the
  sandboxed agent appends its own `E-` summary.

## Scope

1. Define a plans-ledger superseding/correction row (`ledger_revision >= 2` or `ledger_correction`) in
   `docs/ledger_schema.md`, consistent with the existing execution-row revision mechanism.
2. `calibration.parse_predicted_metrics()` prefers the highest-`ledger_revision` plans row for a plan id, and
   cross-checks against the plan file's Overall table and the execution row's `predicted_metrics`, warning on mismatch.
3. Audit existing `plans.jsonl` rows on `main` for the same last-row-wins defect and, where wrong, append correction
   rows (never rewrite history).
4. Fix the duplicate terminal execution summary: one authoritative `E-` summary per execution, stamped at completion.
5. Tests for each, via `uv run pytest`.

## Notes

- Until this lands, PR #91's Stage 5 calibration report must state that its `plans.jsonl` predicted metrics are
  known-wrong and quote the Overall values from the plan file.
- Evidence: `.subagent/holon-agentic-coder_pr91_coordination.json` (`deferred`, id `IMP-1-residual`).
- Run through the Holon flow on `holon-agentic-coder`.
