---
# holon-agentic-coder-ref-metadata-0623
title: "Coherence: allow shrinking files in test_module_budgets and test_complexity_baseline under frozen config"
status: completed
type: bug
priority: high
tags:
  - holon-coherence
  - hygiene
  - tests
created_at: 2026-11-27T08:29:46Z
updated_at: 2026-11-27T11:50:10Z
---

## Problem

Coherence flows (`0527` slice 1 `coherence-provider-format-seam` and PR `#67` / `0530` `coherence-dashboard-html-asset`)
halted at Stage 3/4 in a ratchet-test deadlock:

- `holon-config/hygiene/module_budgets.json` is frozen by `flow_gates.py` (flows cannot edit it without explicit
  maintainer budget-change authorization), yet `tests/test_module_budgets.py:183`
  (`test_live_repository_passes_module_budgets`) asserts `captured.out == ""` on `scripts/check_module_budgets.py`,
  which prints informational `Ratchet notice: <path> shrunk to <actual> lines (< <limit>); ...` lines whenever an
  overridden file shrinks.
- `tests/test_complexity_baseline.py:82` (`test_complexity_baseline_ratchet_ceiling`) enforces exact equality
  `total_count == BASELINE_CEILING` (`11`), so any PR removing an inline `# noqa: PLR0911` suppression fails unless it
  edits `tests/test_complexity_baseline.py` out of scope.

## Acceptance Criteria

- `tests/test_module_budgets.py::test_live_repository_passes_module_budgets` asserts `main(...) == 0` and
  `captured.err == ""` without failing on informational `Ratchet notice:` stdout lines, while still failing if any
  module exceeds its budget or `main(...)` returns non-zero.
- `tests/test_complexity_baseline.py::test_complexity_baseline_ratchet_ceiling` enforces
  `total_count <= BASELINE_CEILING` without failing when inline `# noqa` suppressions strictly decrease below
  `BASELINE_CEILING`.
- Unit tests prove both behaviors (shrinking an overridden module passes while emitting a ratchet notice; reducing
  `# noqa` count below ceiling passes while exceeding ceiling fails), `uv run pytest` and `uv run task lint` pass with
  zero docstrings/comments, and `holon-config/hygiene/module_budgets.json` is untouched.

## Resolution

Delivered via [PR #77](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/77) and merged into `main`
(`bfdb1fd7`):

- **Key Architectural Deliverables**: Updated `test_live_repository_passes_module_budgets` in
  `tests/test_module_budgets.py` to assert `main(...) == 0` and `captured.err == ""` without failing on informational
  `Ratchet notice:` stdout lines, and updated `test_complexity_baseline_ratchet_ceiling` in
  `tests/test_complexity_baseline.py` to enforce `total_count <= BASELINE_CEILING` while leaving
  `holon-config/hygiene/module_budgets.json` untouched.
- **Verification & Tests**: Added unit tests in `tests/test_module_budgets.py` and `tests/test_complexity_baseline.py`
  proving shrinking overridden modules and reducing inline `# noqa` suppressions below ceiling pass while regressions
  fail.
- **Holon Flow Traversal**: Completed all 5 stages (`I-1795768590-coherence-ratchet-test-deadlock`,
  `P-1795768613-ANA-G4N`, `E-1795776793-ANA-G4N`, Stage 4 consensus review, Stage 5 calibration).
