---
# holon-agentic-coder-ref-metadata-0200
title: "Remove holon-agentic-coder's diverged token_reduction copy; holon-coherence is the single owner"
status: todo
type: task
priority: normal
tags:
  - refactor
  - duplication
  - token-reduction
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0189
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:45:00Z
---

## Problem

Spawned by Bean 0177; this is Bean 0152 scope item 4. `sandbox_executor/token_reduction/` (`993b686`, 2,819 lines) is a
diverged copy of holon-coherence (`68fdf67`): `mitm_addon` 1,358 vs 2,348 lines (2,358 differing lines), `hybrid_cache`
308 vs 446, `payload_cleaner` 552 vs 598, `ca_generator` 251 vs 278. Both contain the same 192-line
`extract_sse_token_counts` (CC 85). Production code imports only `generate_root_ca` from it (`cli.py`); the rest is
reached only by tests (`test_token_reduction.py` 3,734 lines, `test_context_cleaner.py` and fuzz tests). The proxy that
actually runs is the holon-coherence image.

## Scope

1. **Decision first (recorded in this bean before Stage 1):** holon-coherence owns token reduction. Confirm in the plan
   that no image, Dockerfile, bake target or runtime path loads `sandbox_executor.token_reduction` other than CA
   generation.
2. Keep CA generation (move it next to the sidecar launcher from 0189, or call holon-coherence's `init-ca`).
3. Delete the remaining modules and their tests; move any test that guards holon-agentic-coder behaviour (redaction on
   URLs, sidecar env) to the module it tests.
4. No reduction in coverage of code that remains.

## Touch set

`sandbox_executor/token_reduction/`, `launcher/sidecar.py` (CA call), `tests/test_token_reduction.py`,
`tests/test_context_cleaner.py`, the fuzz tests' imports, `docs/` references.

## Dependencies

Blocked by 0189. **Maintainer decision (2026-10-29): token reduction is owned by holon-coherence.** holon-agentic-coder
keeps only what it needs to use holon-coherence (for example the root CA generation, sourced from holon-coherence) and
deletes its own copy. Related to 0157 (sidecar auto-enable).

## Notes

- Run through the Holon flow on holon-agentic-coder.
- A tracked `todo/ab_measure_all_methods.py` imports this package; it is a harness-path leak handled by Bean 0147.
