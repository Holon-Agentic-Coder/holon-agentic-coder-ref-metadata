---
# holon-agentic-coder-ref-metadata-0075
title: "Decouple orphaned modules and fix documentation path drift in holon-coherence"
status: todo
type: task
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-07T12:50:00Z
---

## Summary

In `holon-coherence`, an architectural audit revealed that:

1. `OpenBrainMemory`, `RAGCodebaseIndexer`, and `RingerOrchestrator` are documented as Phase 4 components and exported
   in `__init__.py`, but have no operational hookups to `cli.py` or `mitm_addon.py`. They exist as orphaned modules
   without execution path wiring.
2. Several documents under `docs/methods/` contain outdated references to obsolete script paths (`scripts/run_mitm.sh`)
   and historical repository layouts.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Decide architectural path for Phase 4 components: either integrate `RingerOrchestrator` and `RAGCodebaseIndexer` into
  CLI entrypoints and test harnesses, or cleanly decouple them into optional plugin modules with explicit status
  markers.
- Update outdated script paths across `docs/methods/` to match modern `uv run coherence` CLI invocations.
- Decompose monolithic `mitm_addon.py` and `cli.py` by extracting provider parsers into `src/holon_coherence/parsers/`
  and command dispatchers into `src/holon_coherence/commands/`.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Findings ARCH-01,
  ARCH-02, ARCH-03).
