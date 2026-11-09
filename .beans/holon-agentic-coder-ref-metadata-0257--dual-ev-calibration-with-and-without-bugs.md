---
# holon-agentic-coder-ref-metadata-0257
title:
  "Dual Actual EV in Stage 5 calibration: report both Intrinsic EV (without pre-existing/pipeline bugs) and Observed EV
  (with bugs included)"
status: todo
type: feature
priority: high
tags:
  - calibration
  - stage-5
  - ledger
  - metrics
  - ev
  - holon-agentic-coder
created_at: 2026-11-09T13:16:30Z
updated_at: 2026-11-09T14:30:00Z
---

## Problem

When a flow execution encounters a pre-existing engine/harness bug from a previous PR or an intermediate pipeline halt
before converging to a clean, approved PR (as happened on PR #146, where an intermediate Stage 4 run recorded a failed
`REV-...` summary row before the final converged iteration passed 11/11 CI checks and 3/3 review approval), Stage 5
calibration currently reports only a single `Actual EV` (`-8.48`).

A single `Actual EV` conflates two distinct realities:

1. **If only the raw/bug-affected EV (`-8.48`) is shown**: It makes a healthy, approved PR look like it delivered
   negative value (`P(success) = 0.00`), masking the true intrinsic value of the change (`+81.89`).
2. **If only the clean/intrinsic EV (`+81.89`) is shown**: It hides the real operational drag caused by hitting a bug
   from a previous PR during the run.

## Decision

Update Stage 5 calibration (`sandbox_executor/calibration.py`) to compute and report **two Actual EV metrics** side by
side:

1. **`Actual EV (Clean / Without Bugs)` (`ev_clean`)**:
   - Evaluates the intrinsic quality and outcome of the delivered change itself using the final converged Stage 3
     execution (`E-...`) and final converged Stage 4 review outcome (treating `status == "halted_for_human"` consensus
     approval and `status == "success"` as `p_success = 1.0`), excluding intermediate pipeline/harness bug failures.
2. **`Actual EV (Observed / With Bugs Included)` (`ev_with_bugs` / `ev_observed`)**:
   - Evaluates the raw end-to-end execution trail including any intermediate `failed` summary rows, bug-induced retries,
     or pre-existing pipeline/harness failures encountered during the run.
3. **Alignment & Divergence Signal (`bug_ev_drag`)**:
   - On a clean run where no bugs or intermediate failures occur, **both EV scores align (`ev_clean == ev_with_bugs`)**.
   - Whenever a flow hits or uncovers a bug from a previous PR, the two EV scores diverge (`ev_clean != ev_with_bugs`),
     and the difference (`bug_ev_drag = round(ev_clean - ev_with_bugs, 2)`) explicitly quantifies how much Expected
     Value was lost to the bug.

## Scope

1. **`ActualMetrics` & `CalibrationDeltas` in `apps/sandbox-executor/src/sandbox_executor/calibration.py`**:
   - Extend `ActualMetrics` (and `CalibrationDeltas` / `report_data`) to carry both:
     - `ev` / `ev_clean` (the intrinsic EV without pre-existing/pipeline bugs, plus `p_success_clean`, `impact_clean`,
       `delta_ev_clean`)
     - `ev_with_bugs` (the raw EV with intermediate/pipeline bugs included, plus `p_success_with_bugs`,
       `delta_ev_with_bugs`, and `bug_ev_drag`)
   - Ensure `compute_actual_metrics()` separates Stage 3 `E-...` execution summary records and final `REV-...` consensus
     records (`ev_clean`) from intermediate failed `REV-...` / `E-...` records (`ev_with_bugs`).
   - Treat `status == "halted_for_human"` (the mandatory Stage 4 human-merge safety gate after consensus approval) as a
     successful convergence state for `ev_clean` (and for `ev_with_bugs` when no prior failure rows exist).
2. **Calibration Markdown Report & Console Summary (`format_markdown_report`)**:
   - In the Executive Calibration Summary table and Mathematical Derivations section of `plans/P-*_calibration.md`,
     render both:
     - **Expected Value — Clean ($EV\_{\text{clean}}$, without bugs)**
     - **Expected Value — Observed ($EV\_{\text{with\_bugs}}$, with bugs included)**
   - When the two values match, note that no bug drag was observed; when they differ, highlight the divergence and
     report the exact EV drag ($\Delta EV_{\text{bug}}$) attributable to bugs encountered during the run.
3. **Unit Tests (`apps/sandbox-executor/tests/`)**:
   - Verify that when a run has no intermediate failures, `ev_clean == ev_with_bugs` and `bug_ev_drag == 0.0`.
   - Verify that when a run hits an intermediate failed summary row (or bug) before succeeding on retry/resumption,
     `ev_clean` reflects the positive converged EV while `ev_with_bugs` reflects the bug-penalised EV, and both are
     rendered in `plans/P-*_calibration.md`.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be executed through the 5-stage Holon flow (`holon flow`).
- Keep net line delta of `calibration.py` (currently >1,000 lines) $\le 0$ by extracting helper logic into a focused
  submodule (e.g. `sandbox_executor/calibration_ev.py`) and placing new tests in a dedicated test file.
