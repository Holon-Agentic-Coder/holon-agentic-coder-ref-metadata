---
# holon-agentic-coder-ref-metadata-0232
title: "Bump default per-turn timeout to 1 hour (3600 seconds)"
status: completed
type: task
priority: normal
tags:
  - budgets
  - executor
  - turn-supervisor
  - holon-agentic-coder
created_at: 2026-11-05T09:38:00Z
updated_at: 2026-11-06T00:09:00Z
---

## Problem

The default turn timeout (`DEFAULT_TURN_SECONDS` in `sandbox_executor.budgets`, governed by
`HOLON_TURN_TIMEOUT_SECONDS`) is currently set to 300 seconds (5 minutes).

Deep-reasoning and extended-thinking models (such as `gemini-4-argon`, Claude Opus with extended thinking, or
high-effort reasoning agents) frequently spend several minutes in silent prefill/deliberation before emitting their
first file modification or spawning a tool process. During this silent deliberation period, no watched artefact
(`plans/P-*.md`, `executions/E-*.md`), repository file, or tool CPU usage changes. Consequently, the turn supervisor
assumes the agent has stalled and terminates the process right after 300 seconds
(`Stopping agent turn: execute turn budget of 300 s exceeded after 300.9 s`), failing execution stages prematurely.

## Scope

1. **Update Default Constant**:
   - Change `DEFAULT_TURN_SECONDS` from `300.0` to `3600.0` (1 hour) in
     `apps/sandbox-executor/src/sandbox_executor/budgets.py`.
2. **Update Tests**:
   - Update assertions in `apps/sandbox-executor/tests/test_budgets.py` and `apps/sandbox-executor/tests/test_cli.py`
     (e.g., `budgets turn=3600s stall=90s`).
   - Ensure all affected test suites in `apps/sandbox-executor` pass via `uv run pytest`.
3. **Update Documentation**:
   - Update `docs/budgets.md`, `docs/ledger_schema.md`, and CLI help text / documentation where the 300 s turn budget is
     cited.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be delivered through the Holon flow (`holon flow`).

## Completed (2026-11-06)

Delivered end-to-end via `holon flow` on `antigravity-agent` / `gemini-4-argon`: intent
`I-1793921896-bump-default-turn-timeout-to-1-hour`, plan `P-1793921914-antigravity-agent-gemini-4-argon`, execution
`E-1793922181-antigravity-agent-gemini-4-argon`, PR #126, merged as `0f80271`. Updated `DEFAULT_TURN_SECONDS = 3600.0`
in `sandbox_executor.budgets`, updated unit/CLI tests in `test_budgets.py` and `test_cli.py`, and updated
`docs/budgets.md` and `docs/ledger_schema.md`. Passed unanimous 3/3 Stage 4 review at iteration 1 and completed Stage 5
calibration (`plans/P-1793921914-antigravity-agent-gemini-4-argon_calibration.md`, predicted EV 70.67 vs actual EV
75.31, $\Delta\text{EV} = +4.64$).
