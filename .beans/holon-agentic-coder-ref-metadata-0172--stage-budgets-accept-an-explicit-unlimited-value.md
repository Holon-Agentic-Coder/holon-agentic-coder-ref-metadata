---
# holon-agentic-coder-ref-metadata-0172
title: "Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)"
status: completed
type: feature
priority: normal
tags:
  - budgets
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-27T14:04:58Z
updated_at: 2026-11-21T08:55:00Z
---

## Problem

The stage budgets cannot be removed explicitly. While running Bean 0168 (2026-10-27), the maintainer wanted Stage 3 to
run without a ceiling rather than risk another budget breach (Bean 0171).

In `sandbox_executor/budgets.py`, `_read_positive` (around lines 115-150) treats every `HOLON_STAGE_BUDGET_*` value as
follows:

- **unset or blank:** the default (for example 45 minutes for execute);
- **`inf`, `nan`, negative or zero:** rejected with a warning, then the default;
- **above `MAX_BUDGET_SECONDS` (7 days):** rejected with a warning, then the default;
- **anything else:** used as given.

So "no limit" cannot be expressed. An unset variable has to keep meaning "use the default", and so it cannot also mean
unlimited. The workaround is `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080`, the 7-day maximum. It works, but it is a magic
number, and its log and summary line ("execute: … / 10080 min") misreport the intent.

The turn budgets are inconsistent with this: `HOLON_TURN_STALL_SECONDS=0` already disables stall detection
(`allow_zero=True`), but `HOLON_TURN_TIMEOUT_SECONDS` and the stage variables have no equivalent.

## Scope

1. **An explicit sentinel.** Accept one documented, case-insensitive value, for example `unlimited` (decide whether
   `none`, `off` or `0` are aliases, and keep it consistent with the stall variable's `0`), for:
   - every per-stage variable (`HOLON_STAGE_BUDGET_{INTENT,PLAN,EXECUTE,REVIEW_ITERATION,CALIBRATION}_MINUTES`);
   - `HOLON_STAGE_BUDGET_SECONDS`;
   - `HOLON_TURN_TIMEOUT_SECONDS`.

   Unset still means the default. The literal float `inf` stays rejected, so no infinite value reaches the arithmetic.

2. **Representation.** Use `None` (or a dedicated type) internally for "no ceiling", never `float("inf")`, so
   remaining-time maths, `format_minutes` and the container env stay finite. The env handed to a role container
   (`stage_budget_env`, around line 288) must carry "unlimited" without turning it into a number. The container side
   must honour it too.
3. **Safety.** With no stage ceiling, stall detection and the per-turn timeout are the only protection against a hung
   agent. Log a clear warning when a stage is unlimited. Refuse, or loudly warn, when the stage ceiling, the turn
   timeout and stall detection are all disabled together. Record the unlimited budget on the stage's ledger row, so that
   calibration and the metrics see that it was unbounded.
4. **Reporting.** `holon doctor` and the flow summary show "unlimited" (for example
   `execute: ok (73.2 min / unlimited)`) instead of a number.
5. **Tests**, with an injected clock and no real waiting:
   - sentinel parsing for each variable, including case and whitespace;
   - unset still gives the default;
   - `inf` and `nan` still rejected;
   - an unlimited stage never breaches, while stall and turn limits still fire;
   - the container env round-trips the sentinel;
   - the doctor and summary output.
6. **Docs.** Update `docs/budgets.md`, the CLI help and the environment-variable reference.

## Notes

- Run through the Holon flow on holon-agentic-coder. It touches `budgets.py`, `turns.py`/`flow.py` budget plumbing and
  the doctor output, so check for overlap with open flows.
- Related: Bean 0171 (salvage on a budget breach drops the code changes), Bean 0139 (the original budgets work).

## Audit (2026-11-21)

Still valid. `budgets.py` `_read_positive` (around lines 106-152) still rejects `inf`, zero and values above
`MAX_BUDGET_SECONDS` (7 days) with the default; no `unlimited` sentinel exists.

## Progress

- 2026-11-21: started via `holon flow` (claude-agent, claude-opus-5-5) in worktree `flow-unlimited-stage-budgets`.
- 2026-11-21: flow complete; PR #225 approved 3/3 at review iteration 2, calibrated (EV 41.0 predicted, 59.32 actual),
  CI green, CLEAN/MERGEABLE; awaiting human merge.

## Resolution

- **Delivered via PR #225:** Merged into `main` (`4811599793a0604d175e5b1561178f55e5e29537`) on 2026-11-21T08:54:15Z.
- **Key Deliverables:**
  - Explicit `unlimited` sentinel support across stage (`HOLON_STAGE_BUDGET_*`) and turn timeout
    (`HOLON_TURN_TIMEOUT_SECONDS`) variables.
  - Internal `None` representation with clean container environment propagation and round-tripping.
  - `holon doctor` and flow summary reporting showing `unlimited` instead of magic numbers.
  - Full test suite additions (`test_pipeline_unlimited.py`, `test_cli_unlimited_budgets.py`, etc.) and updated
    documentation (`docs/budgets.md`).
- **Flow & Quality Metrics:**
  - Traversed all 5 Holon flow stages
    (`I-1795184210-unlimited-stage-budgets/P-1795184233-CLA-CO5.5/E-1795246867-CLA-CO5.5/_`).
  - Achieved 3/3 reviewer consensus approval at iteration 2.
  - All 11/11 CI checks passing.
  - Calibration report (`plans/I-1795184210-unlimited-stage-budgets/P-1795184233-CLA-CO5.5_calibration.md`): EV 41.0
    predicted vs. 59.32 actual.
