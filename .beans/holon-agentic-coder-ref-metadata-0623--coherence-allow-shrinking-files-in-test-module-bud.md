---
# holon-agentic-coder-ref-metadata-0623
title: "Coherence: allow shrinking files in test_module_budgets and test_complexity_baseline under frozen config"
status: in-progress
type: bug
priority: high
tags:
  - holon-coherence
  - hygiene
  - tests
created_at: 2026-11-27T08:29:46Z
updated_at: 2026-11-27T08:30:40Z
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
