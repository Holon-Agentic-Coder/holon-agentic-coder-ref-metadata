---
# holon-agentic-coder-ref-metadata-0635
title: "HAC: extend test_import_cycle_ratchet.py to cover root-level sandbox_executor modules"
status: completed
type: task
priority: normal
tags:
  - holon-agentic-coder
  - architecture
  - ci
created_at: 2026-11-27T15:53:29Z
updated_at: 2026-11-27T23:48:13Z
---

## Notes

### Evidence (2026-11-27 fifth-merge audit, `holon-agentic-coder@1f3331637`)

- [PR #415](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/415) (`bebb0840d`, Bean `0615`) added
  `apps/sandbox-executor/tests/test_import_cycle_ratchet.py`, locking `entrypoint <-> flow` (`12<->15`) and
  `knowledge <-> ledger` (`4<->1`).
- `discover_top_level_subpackages()` (`apps/sandbox-executor/tests/test_import_cycle_ratchet.py:19-28`) only scans
  subdirectories (`if child.is_dir()`), ignoring all root-level `src/sandbox_executor/*.py` modules.
- Live AST inspection of `apps/holon-agentic-coder/main` (`1f3331637`) confirms **4 additional bidirectional cycles**
  involving root-level modules bypass `test_import_cycle_ratchet.py` undetected:
  1. `calibration (2) <-> calibration_self_check (1)` (`calibration/__init__.py:30`, `calibration/run.py:19` <->
     `calibration_self_check.py:16`).
  2. `entrypoint (1) <-> review_target (1)` (`entrypoint/review_loop.py:58` <-> `review_target.py:12`).
  3. `flow (8) <-> review_target (4)` (`flow/git_refs.py:33`, `flow/review/*.py` <->
     `review_target.py:127,159,186,223`).
  4. `flow (4) <-> flow_guard (1)` (`flow/pipeline.py:43`, `flow/stages/*.py` <-> `flow_guard.py:9`).

### Proposed Change

1. Extend `apps/sandbox-executor/tests/test_import_cycle_ratchet.py` to treat root-level `src/sandbox_executor/*.py`
   modules (excluding `__init__.py`) as top-level graph nodes alongside subpackages.
2. Lock all 6 current cycle pairs at their `1f3331637` edge counts so CI rejects any new or expanded root<->subpackage
   or root<->root cycle while allowing Beans `0531` and `0584` to shrink them downward.

### Expected Gain & Cost

- Closes the root-module import-cycle blind spot in HAC CI (mirroring Coherence Bean `0632`).
- Cost: ~40 lines in `apps/sandbox-executor/tests/test_import_cycle_ratchet.py` + synthetic root-module cycle unit test.

## Acceptance Criteria

- [ ] `apps/sandbox-executor/tests/test_import_cycle_ratchet.py` includes root-level `src/sandbox_executor/*.py` modules
      alongside subpackages and locks all 6 existing cyclic pairs at or below their baseline edge counts.
- [ ] Synthetic AST unit tests verify a newly introduced root<->subpackage or root<->root cycle fails while shrinking a
      recorded cycle edge count passes.
- [ ] `uv run pytest` and `uv run task lint` pass with zero docstrings or non-`# why:` comments.

## Flow

- **Progress (`2026-11-27`):** `hac-root-import-cycle-ratchet` completed all 5 stages on `antigravity-agent` /
  `gemini-4-neon` and opened [PR #432](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/432) (`OPEN`,
  `MERGEABLE` / `CLEAN`, `16/16` CI checks `SUCCESS`, Consensus `APPROVED`,
  `Predicted EV 58.05 / Actual EV 65.75 / ΔEV +7.70`). Waiting for human maintainer merge.

## Resolution

Delivered via [PR #432](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/432) and merged into `main`
(`65c7741f73`):

- **Key Architectural Deliverables**: Extended `apps/sandbox-executor/tests/test_import_cycle_ratchet.py` to cover
  root-level `src/sandbox_executor/*.py` modules alongside subpackages and ratchet all 6 bidirectional import-cycle
  pairs.
- **Verification & Tests**: Synthetic root-module AST cycle tests in
  `apps/sandbox-executor/tests/test_import_cycle_ratchet.py`; `16/16` CI checks `SUCCESS`.
- **Holon Flow Traversal & Readiness (`pr_readiness.py --record`)**: Head `a2591bdc`, Consensus `APPROVED` (`5a754a55`),
  Stage 5 calibration `calibrate=success`
  (`plans/I-1795796830-hac-root-import-cycle-ratchet/P-1795796867-ANA-G4N_calibration.md`),
  `gates: consensus=ok, calibration=ok, pipeline=ok`.
