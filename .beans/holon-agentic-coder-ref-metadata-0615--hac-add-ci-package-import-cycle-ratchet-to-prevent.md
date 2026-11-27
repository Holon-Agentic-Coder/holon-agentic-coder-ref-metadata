---
# holon-agentic-coder-ref-metadata-0615
title: "HAC: add CI package import-cycle ratchet to prevent layer cycle regressions"
status: completed
type: task
priority: normal
tags:
  - holon-agentic-coder
  - architecture
  - ci
created_at: 2026-11-27T05:26:26Z
updated_at: 2026-11-27T12:29:07Z
---

## Notes

- **Problem**: Over the 42 PRs merged between `f006e79b` and `5c0a557cc`, existing bidirectional package import cycles
  in `holon-agentic-coder` silently worsened: `entrypoint` ↔ `flow` grew from `12↔11` to `12↔15` edges and `knowledge` ↔
  `ledger` grew from `3↔1` to `4↔1` edges (total 6 package cycles: `calibration(2)<->calibration_self_check(1)`,
  `entrypoint(12)<->flow(15)`, `entrypoint(1)<->review_target(1)`, `flow(4)<->flow_guard(1)`,
  `flow(8)<->review_target(4)`, `knowledge(4)<->ledger(1)`).
- **Proposed Change**: Add a fast AST-based package-import graph test in `holon-agentic-coder` CI with a locked baseline
  of allowed cycle edge counts (ratchet-only: new package cycles or increased edge counts fail CI; lowering counts
  updates the baseline downward). Coordinate with Beans `0531` and `0584` which unwind the existing cycles.
- **Reference**: Source: 2026-11-27 ecosystem architecture audit (`docs/ecosystem-audit-report-2026-11.md`); coordinates
  with Beans `0531` and `0584`.

## Acceptance Criteria

- CI fails if any new package import cycle is introduced or if any existing cycle's edge count increases; removing edges
  passes cleanly and allows lowering the ratchet baseline.

## Resolution

Delivered via [PR #415](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/415) and merged into `main`
(`bebb0840d`):

- **Key Architectural Deliverables**: Added `apps/sandbox-executor/tests/test_import_cycle_ratchet.py`, an AST-based
  top-level subpackage import-cycle ratchet locking `BASELINE_CYCLE_EDGE_COUNTS` (`entrypoint <-> flow` 12/15,
  `knowledge <-> ledger` 4/1) so new package cycles or increased edge counts fail CI while reductions pass cleanly.
- **Verification & Tests**: Includes synthetic import-graph unit tests verifying that new cycles and edge regressions
  fail and edge removals pass; self-explaining code gate reported 0 added docstrings and 0 non-`# why:` comments across
  6 changed files.
- **Holon Flow Traversal**: Completed all 5 Holon flow stages (`I-1795768350-hac-import-cycle-ratchet`, plan
  `P-1795768373-ANA-G4N-2`, execution `E-1795768641-ANA-G4N`), calibrated in Stage 5 (EV predicted `53.31` / actual
  `65.54`, $\Delta\text{EV} = +12.23$, Bug EV Drag `0.00`).
