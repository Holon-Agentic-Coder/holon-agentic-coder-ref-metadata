---
# holon-agentic-coder-ref-metadata-0586
title: "Move 7 functions out of holon_coherence/providers/__init__.py and enforce no-logic __init__.py"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - architecture
  - hygiene
  - refactor
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-27T07:47:29Z
---

## Problem

`src/holon_coherence/providers/__init__.py` defines 7 functions implementing provider registration, default loading, and
URL/payload detection. Under the ecosystem "no logic in `__init__.py`" standard (tracked for `holon-agentic-coder` in
Bean `0379`), package `__init__.py` files should only re-export public symbols cleanly without behavioural logic or
import-time side effects.

## Evidence

- `src/holon_coherence/providers/__init__.py` defines 7 functions: `register_provider`, `_load_default_providers`,
  `get_provider`, `_detect_by_url`, `_detect_by_payload`, `detect_provider_name`, and `resolve_provider`.
- Bean `0379` enforces the no-logic `__init__.py` invariant only in `holon-agentic-coder`, leaving `holon-coherence`
  without an AST guard.

## Proposed Change

1. Extract the 7 registry and provider-detection functions into `src/holon_coherence/providers/registry.py`
   (coordinating with Bean `0527`'s unified `ProviderFormat.matches()` seam).
2. Keep `src/holon_coherence/providers/__init__.py` restricted to clean public re-exports.
3. Add a pytest AST hygiene check in `holon-coherence/tests/` asserting zero `FunctionDef` / `AsyncFunctionDef` /
   `ClassDef` definitions in any `src/holon_coherence/**/__init__.py`.

## Acceptance Criteria

- `src/holon_coherence/providers/__init__.py` (and all other `src/holon_coherence/**/__init__.py`) contains zero
  function or class definitions.
- Automated AST test enforces no logic in `holon_coherence` package `__init__.py` files.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Coordinate with Bean `0527` (`providers/__init__.py` detection unification) and mirror Bean `0379` from
  `holon-agentic-coder`.
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
