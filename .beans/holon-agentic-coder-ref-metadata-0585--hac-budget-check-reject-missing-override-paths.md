---
# holon-agentic-coder-ref-metadata-0585
title: "Reject deleted or missing file paths in check_module_budgets.py and prune dead calibration.py cap"
status: todo
type: bug
priority: normal
tags:
  - holon-agentic-coder
  - hygiene
  - ci
  - module-budgets
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-27T00:33:33Z
---

## Problem

When a refactored monolith is deleted, its legacy override entry in `holon-config/hygiene/module_budgets.json` remains
orphaned without `scripts/check_module_budgets.py` failing or warning. Currently `calibration.py` (deleted in PR `#347`)
still carries a 1,608-line override, and `flow/__init__.py` sits at 38 lines under a 522-line cap.

## Evidence

- `holon-config/hygiene/module_budgets.json` lists `"apps/sandbox-executor/src/sandbox_executor/calibration.py": 1608`,
  even though that file was deleted in PR `#347` (`8b208632`).
- `holon-config/hygiene/module_budgets.json` lists `"apps/sandbox-executor/src/sandbox_executor/flow/__init__.py": 522`,
  while the file is 38 lines (well below the 400-line default cap).
- `scripts/check_module_budgets.py` does not reject override keys whose target path does not exist on disk.

## Proposed Change

1. Update `scripts/check_module_budgets.py` (and its unit tests) to fail when any entry in `module_budgets.json`
   `overrides` references a missing file path.
2. Add a check/warning or automatic ratchet failure for override entries whose actual line count is already at or below
   `default_max_lines`.
3. Under maintainer budget-change authorisation (coordinate with Beans `0489` and `0570`), prune the orphaned
   `calibration.py` override and stale `flow/__init__.py` override.

## Acceptance Criteria

- `scripts/check_module_budgets.py` fails immediately if `module_budgets.json` names a non-existent path.
- No deleted-file entries remain in `holon-config/hygiene/module_budgets.json`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f006e79b`).
- Coordinate `module_budgets.json` edits with Beans `0489` and `0570` (`module-budget-change` maintainer authorisation
  rule).
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
