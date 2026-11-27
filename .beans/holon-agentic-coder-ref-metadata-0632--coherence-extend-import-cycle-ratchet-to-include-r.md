---
# holon-agentic-coder-ref-metadata-0632
title: "Coherence: extend import-cycle ratchet to include root-level modules"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - architecture
  - ci
  - hygiene
created_at: 2026-11-27T12:11:44Z
updated_at: 2026-11-27T12:13:43Z
---

## Notes

### Evidence (2026-11-27 fifth-merge Coherence audit, `4a02926b`)

- [PR #76](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/76) (`1bf07f6b`, Bean `0621`) added
  `tests/test_import_cycle_ratchet.py`, locking `commands <-> container` (`4<->3`) and `parsers <-> providers`
  (`3<->4`).
- `tests/test_import_cycle_ratchet.py:69-74` skips every file where
  `len(rel.parts) < 2 or rel.parts[0] not in subpackages`, ignoring all root-level `src/holon_coherence/*.py` modules.
- Live AST inspection of `holon-coherence@4a02926b` confirms **3 additional bidirectional cycles** involving root-level
  modules pass `test_import_cycle_ratchet.py` undetected:
  1. `payload_cleaner (2) <-> providers (4)` (`src/holon_coherence/payload_cleaner.py:12,13` <->
     `providers/{anthropic,base,gemini,openai}.py`).
  2. `payload_cleaner (1) <-> reduction_passes (1)` (`src/holon_coherence/payload_cleaner.py:21` <->
     `src/holon_coherence/reduction_passes.py:10`, `TYPE_CHECKING` back-edge).
  3. `hybrid_cache (1) <-> proxy (1)` (`src/holon_coherence/hybrid_cache.py:35` <->
     `src/holon_coherence/proxy/addon.py:11`), newly surfaced by the `4a02926b` AST scan.

### Proposed Change

1. Extend `tests/test_import_cycle_ratchet.py` to treat root-level `src/holon_coherence/*.py` modules (excluding
   `__init__.py`) as top-level graph nodes alongside subpackages (`commands`, `container`, `parsers`, `providers`,
   `proxy`, etc.).
2. Lock all 5 current cycle pairs at their `4a02926b` edge counts so CI immediately rejects any new or expanded
   root<->subpackage or root<->root cycle while allowing `0527` and follow-up refactors to shrink them downward.

### Expected Gain & Cost

- Closes the blind spot covering root modules (`payload_cleaner`, `hybrid_cache`, `host_local`, `reduction_passes`,
  `settings`, `mitm_addon`, `ringer_orchestrator`) in Coherence CI.
- Cost: ~40 lines in `tests/test_import_cycle_ratchet.py` + synthetic unit test for root-module cycles.

## Acceptance Criteria

- [ ] `tests/test_import_cycle_ratchet.py` includes root-level `src/holon_coherence/*.py` modules alongside subpackages
      and locks all existing cyclic pairs at or below their baseline edge counts.
- [ ] Synthetic AST unit tests verify a newly introduced root<->subpackage or root<->root cycle fails while shrinking a
      recorded cycle edge count passes.
- [ ] `uv run pytest` and `uv run task lint` pass with zero docstrings or comments.

## Resolution
