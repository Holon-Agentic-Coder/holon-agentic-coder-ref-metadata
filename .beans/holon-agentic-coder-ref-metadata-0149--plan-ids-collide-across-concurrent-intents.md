---
# holon-agentic-coder-ref-metadata-0149
title: "Plan (and execution) IDs collide across intents planned concurrently"
status: completed
type: bug
priority: high
tags:
  - provenance
  - planner
  - ledger
created_at: 2026-10-24T02:20:00Z
updated_at: 2026-11-09T13:19:00Z
---

## Problem

Plan IDs are `P-<epoch-seconds>-<agent>-<model>`, so two intents planned in the same second by the same runner and model
get the same ID. That happened on 2026-10-23. holon-agentic-coder PR #91 (Bean 0135, now merged) and PR #92 (Bean 0136)
both carry `P-1792765112-claude-agent-claude-opus-5-5`:

- **Plan file:** both write `plans/P-1792765112-claude-agent-claude-opus-5-5.md`. Merging `main` into PR #92 gives an
  add/add conflict between two unrelated plans.
- **Ledger:** `plans.jsonl` would hold two rows with the same `plan_id`. `calibration.parse_predicted_metrics()` takes
  the first matching row, so PR #92 would be calibrated against PR #91's predictions.
- **Calibration report:** `plans/<plan_id>_calibration.md` would collide with PR #91's report, which is already on
  `main`.

Execution IDs (`E-<epoch>-<agent>-<model>`) have the same weakness.

## Scope

- Make plan and execution IDs globally unique. For example, add the parent intent slug or a short random or
  intent-derived suffix, while keeping them sortable and readable. Keep backward compatibility for parsing existing IDs.
- Key plan files, calibration reports and `plans.jsonl` lookups on the full branch (intent + plan) or the unique ID,
  never on the timestamp alone.
- Add a CI or ledger check that fails on duplicate `plan_id` or `execution_id` rows.
- PR #92 was closed and re-run as PR #96 under a fresh plan ID, so no correction row is needed for it (see Bean 0146 for
  the general correction-row mechanism).

## Notes

- Found by the PR #92 Stage 4 dry run, iteration 8 (finding D8-I1).
- Run through the Holon flow on holon-agentic-coder.

## Resolution

- Implemented in `holon-agentic-coder` via the 5-stage Holon flow across Intent
  `I-1794182541-unique-plan-and-execution-ids/_`, Plan `P-1794182557-antigravity-agent-gemini-3.8-flash-medium/_`, and
  Execution `E-1794182857-antigravity-agent-gemini-3.8-flash-medium/_`.
- Added `build_stage_disambiguator()`, `build_plan_id()`, `build_execution_id()`, `validate_ledger_unique_ids()`,
  `validate_ledger_file_unique_ids()`, and `validate_stage_ledger_uniqueness()` in `sandbox_executor.ledger`, wiring
  stage ID generation across `entrypoint/planner.py`, `entrypoint/executor.py`, and `flow.py`
  (`P-{seq}-{disambiguator}-{agent}-{model}` and `E-{seq}-{disambiguator}-{agent}-{model}`).
- Added comprehensive unit test suite in `apps/sandbox-executor/tests/test_unique_stage_ids.py` (211 lines) covering ID
  construction, branch discovery suffix matching, partial-branch regex compatibility, and duplicate ID detection across
  distinct intents and plans.
- Passed Stage 4 3-reviewer ensemble consensus approval at iteration 5 (11/11 CI checks green), completed Stage 5
  calibration (`plans/P-1794182557-antigravity-agent-gemini-3.8-flash-medium_calibration.md`), and merged to `main` via
  [PR #146](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/146) (`4682449`).
