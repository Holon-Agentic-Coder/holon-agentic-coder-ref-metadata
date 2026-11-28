---
# holon-agentic-coder-ref-metadata-0530
title: "Add static type checker to CI, prune redundant self-doc tests, legacy shims, and root clutter"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - typing
  - clean-code
  - hygiene
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T23:50:58Z
---

## Problem

Despite 98.3% return type annotations, CI runs no static type checker (`mypy`/`pyright`). Meanwhile, 9 redundant
per-module `*_self_doc.py` test files duplicate `test_repo_self_doc.py`, legacy compatibility barrels and per-request
`sys.modules` probes add maintenance overhead, unused experimental modules with unclosed SQLite connections sit at the
package root, and misleading names mask metric/parity semantics.

## Evidence

- No `mypy` or `pyright` step in `.github/workflows/`.
- 9 redundant hardcoded `*_self_doc.py` files (922 LOC) duplicating `tests/test_repo_self_doc.py`.
- `src/holon_coherence/proxy/steps/_compat.py:25-67` probes `sys.modules["holon_coherence.mitm_addon"]` on every
  request; oversized re-export barrels in `cli.py:7-162`, `commands/__init__.py`, `mitm_addon.py`, `proxy/__init__.py`,
  and 10 legacy Anthropic wrappers in `payload_cleaner.py:10-17,77-137`.
- Unused experimental modules at package root: `openbrain_memory.py` (unclosed SQLite connections at lines `21,48,81`),
  `rag_indexer.py`, `ringer_orchestrator.py`.
- `src/holon_coherence/proxy/dashboard.py:6-383`: 378-line inline HTML/CSS/JS string literal.
- Overstated parity names `_check_semantic_parity` / `"100% Structural Equivalence"`
  (`ab_testing/evaluation.py:185,307-326`) that only inspect non-empty messages and final role; triple rate aliases
  (`*_tps`, `*_throughput_tps`, `*_speed_tps`) in `proxy/metrics.py:135-142`; dual CLI arg parsing (`cli.py:187-222` vs
  `commands/agents.py:390-454`).

## Proposed Change

1. Add `mypy` or `pyright` to CI and resolve any surfaced type errors.
2. Delete the 9 redundant `*_self_doc.py` test files while keeping `tests/test_repo_self_doc.py` authoritative.
3. Migrate callers off legacy re-export shims/`_compat.py` and retire `proxy/steps/_compat.py` and `payload_cleaner.py`
   legacy wrappers.
4. Move experimental modules (`openbrain_memory.py`, `rag_indexer.py`, `ringer_orchestrator.py`) into
   `holon_coherence/experimental/` (or delete if obsolete) and wrap SQLite usage in context managers.
5. Extract `proxy/dashboard.py`'s inline HTML/CSS/JS to a static asset file, rename `_check_semantic_parity` /
   `"100% Structural Equivalence"` to reflect structural validation accurately, consolidate duplicate TPS field aliases,
   and unify CLI argument parsing.

## Acceptance Criteria

- CI runs `mypy` or `pyright` with zero errors on `src/` and `tests/`.
- Zero redundant `*_self_doc.py` files remain; `_compat.py` per-request probing is removed.
- Package root contains only active core modules and `dashboard.py` loads its HTML asset cleanly.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- Audit refresh (`2026-11-27`, `ce39bf34d`): redundant `*_self_doc.py` files grew from `9` (`922` LOC) to `10` (`1,202`
  LOC) across `#58`–`#65`; `unittest.TestCase` migration finished in PR `#64` (`0` subclasses remain, only
  `unittest.mock` left).
- Progress (`2026-11-27`): [PR #71](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/71)
  (`coherence-parity-and-hygiene`, merge commit `f958f9a0`) merged into `main`, addressing `ab_testing/evaluation.py`,
  `openbrain_memory.py`, `rag_indexer.py`, and repo hygiene tests. Bean remains `in-progress` for remaining slices
  (e.g., `dashboard-html-asset` and CI type-checking).
- Progress (`2026-11-27`): [PR #67](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/67)
  (`coherence-dashboard-html-asset`, merge commit `63a6bf3f`) merged into `main`, extracting `proxy/dashboard.py`'s
  inline HTML/CSS/JS template into static package resource `src/holon_coherence/proxy/dashboard.html` loaded via
  `importlib.resources` (`render_dashboard_html()`) with `tests/proxy/test_dashboard.py` verification. Bean remains
  `in-progress` for CI `mypy`/`pyright`, redundant `*_self_doc.py` prune, and `_compat.py` retirement.
- Progress (`2026-11-27`): [PR #86](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/86)
  (`coherence-prune-self-doc`, merge commit `6976c7b783`, head `b92afe33`, review `APPROVED` on `eb8e443b`, Stage 5
  calibration `plans/I-1795794388-coherence-prune-self-doc/P-1795794410-ANA-G4N_calibration.md`, `10/10` CI `SUCCESS`)
  merged into `main`, deleting the 9 redundant per-module `*_self_doc.py` test files while keeping
  `tests/test_repo_self_doc.py` and updating `tests/test_scripts_self_doc.py`. Bean remains `in-progress` for CI
  `mypy`/`pyright`, `_compat.py` / legacy shim retirement, `ringer_orchestrator.py` cleanup, and CLI arg parsing.
