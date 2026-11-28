---
# holon-agentic-coder-ref-metadata-0621
title: "Coherence: add CI package import-cycle ratchet to prevent new layer cycles"
status: completed
type: task
priority: normal
tags:
  - holon-coherence
  - architecture
  - ci
created_at: 2026-11-27T08:03:26Z
updated_at: 2026-11-27T11:50:10Z
---

## Notes

- **Problem**: `holon-coherence` has no CI package import-cycle ratchet (unlike HAC Bean `0615`). Between `c26a0c1` and
  `ce39bf34d`, PR `#63` (`2a1a856`, `0524` slice 1) silently introduced a new bidirectional package cycle
  `commands <-> container` (`4 <-> 3`, via `src/holon_coherence/container/lifecycle.py:443,468,494` importing
  `holon_coherence.commands.web_token`), and PR `#61` added a `TYPE_CHECKING` back-edge
  `reduction_passes -> payload_cleaner` (`1 <-> 1`), alongside existing `parsers <-> providers` (`3 <-> 4`) and
  `payload_cleaner <-> providers` (`2 <-> 4`).
- **Proposed Change**: Add a fast AST-based package-import graph test in `holon-coherence` CI locking baseline cycle
  edge counts (ratchet-only: new package cycles or increased edge counts fail CI; lowering counts updates the baseline
  downward). Coordinate with Bean `0527` which breaks the existing cycles.
- **Expected Gain & Cost**: Prevents security/feature PRs from silently adding cross-layer dependency cycles; small
  self-contained AST test.
- **Reference**: Source: 2026-11-27 architecture & code-quality refresh (`docs/ecosystem-audit-report-2026-11.md`);
  coordinates with Bean `0527` and mirrors HAC Bean `0615`.

## Acceptance

- CI fails if any new package import cycle is introduced or if any existing cycle's edge count increases; breaking
  cycles passes cleanly and lowers the ratchet baseline.

## Resolution

Delivered via [PR #76](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/76) and merged into `main`
(`1bf07f6b`):

- **Key Architectural Deliverables**: Added an AST-based package import-cycle ratchet test in
  `tests/test_import_cycle_ratchet.py` scanning `src/holon_coherence/` top-level subpackages and locking baseline cycle
  pair edge counts so regressions fail CI while cycle reductions pass cleanly.
- **Verification & Tests**: Added synthetic AST unit tests in `tests/test_import_cycle_ratchet.py` verifying cycle
  regressions fail and improvements pass.
- **Holon Flow Traversal**: Completed all 5 stages (`I-1795768569-coherence-import-cycle-ratchet`,
  `P-1795768592-ANA-G4N`, `E-1795776797-ANA-G4N`, Stage 4 consensus review, Stage 5 calibration).
