---
# holon-agentic-coder-ref-metadata-0584
title: "Consolidate 12 flat calibration_*.py siblings into calibration/ and break calibration_self_check cycle"
status: todo
type: task
priority: normal
tags:
  - holon-agentic-coder
  - architecture
  - modularity
  - refactor
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-27T00:33:33Z
---

## Problem

After PR `#347` (Bean `0197`) split `calibration.py` into `apps/sandbox-executor/src/sandbox_executor/calibration/` (12
modules, 29–273 lines each), 12 flat `calibration_*.py` sibling modules remain at the top level of `sandbox_executor/`.
This creates a confusing split layout (including a naming collision between `calibration_predicted.py` and
`calibration/predicted.py`) and introduces a new top-level import cycle `calibration` ↔ `calibration_self_check`,
alongside `flow` ↔ `flow_guard` and `flow`/`entrypoint` ↔ `review_target`.

## Evidence

- `apps/sandbox-executor/src/sandbox_executor/calibration/` holds 12 modules (`__init__.py`, `actual.py`,
  `actual_evidence.py`, `branches.py`, `checkout.py`, `deltas.py`, `generate.py`, `physics.py`, `predicted.py`,
  `refs.py`, `report.py`, `run.py`).
- 12 flat sibling modules sit at package root: `calibration_diff.py`, `calibration_ev.py`,
  `calibration_evaluated_sha.py`, `calibration_execution_owner.py`, `calibration_format.py`, `calibration_outcome.py`,
  `calibration_predicted.py`, `calibration_record.py`, `calibration_review_churn.py`, `calibration_rows.py`,
  `calibration_self_check.py`, `calibration_touch_set.py`.
- Import cycle: `calibration/run.py:21` imports `calibration_self_check`, while `calibration_self_check` (and sibling
  `calibration_*` helpers) import back into `calibration` (`calibration` 2 ↔ `calibration_self_check` 1).
- Additional flat-helper cycle: `flow_guard.py:9` imports `FlowContext` from `sandbox_executor.flow` while `flow`
  imports `flow_guard` (`flow` 4 ↔ `flow_guard` 1).

## Proposed Change

1. Move all 12 flat `calibration_*.py` siblings under `sandbox_executor/calibration/`, reconciling
   `calibration_predicted.py` and `calibration/predicted.py` cleanly.
2. Invert the `calibration` ↔ `calibration_self_check` dependency (via shared types/protocols or cohesive placement) so
   `calibration` has zero circular imports.
3. Break `flow` ↔ `flow_guard` by passing explicit data contracts rather than importing `FlowContext` back into
   `flow_guard.py`.
4. Update internal/test imports and remove any redundant flat re-exports.

## Acceptance Criteria

- All calibration helpers live cleanly inside `sandbox_executor/calibration/` with no colliding
  `calibration_predicted.py` vs `calibration/predicted.py` split.
- Zero circular import edges exist between `calibration` sub-modules or between `flow` and `flow_guard`.
- `uv run pytest` passes across calibration and flow suites.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f006e79b`).
- Related beans: Bean `0197` (completed `calibration.py` package split), Bean `0531` (`flow` ↔ `entrypoint` and `ledger`
  ↔ `knowledge` cycles).
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
