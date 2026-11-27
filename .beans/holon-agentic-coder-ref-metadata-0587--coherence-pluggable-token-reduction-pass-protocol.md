---
# holon-agentic-coder-ref-metadata-0587
title: "Introduce a pluggable ReductionPass Protocol and registry for holon-coherence token reduction"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - extensibility
  - architecture
  - token-reduction
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-27T00:33:33Z
---

## Problem

Token-reduction payload transformations (system prompt caching normalization, whitespace/message cleanup, redundant
metadata stripping) are implemented imperatively across `proxy/steps/clean_payload.py`, `payload_cleaner.py`, and
`providers/anthropic.py` with no composable `ReductionPass` `Protocol` or registry. Adding, reordering, toggling, or
A/B-benchmarking individual reduction strategies requires editing core step/cleaner code directly.

## Evidence

- `src/holon_coherence/proxy/steps/clean_payload.py`, `src/holon_coherence/payload_cleaner.py`, and
  `src/holon_coherence/providers/anthropic.py` hardcode reduction logic per provider branch rather than iterating an
  ordered registry of composable passes.
- `src/holon_coherence/ab_testing/evaluation.py` has no pluggable pass abstraction to isolate or compare individual
  reduction passes.

## Proposed Change

1. Define a structural `ReductionPass` `Protocol` (`name`, `applies(provider, payload)`,
   `apply(payload, context) -> ReductionResult`) and a deterministic ordered pass registry.
2. Refactor existing token-reduction transforms into small registered passes invoked by `clean_payload.py` cleanly
   without redundant deep copies (coordinating with Bean `0528`).
3. Allow A/B evaluation and configuration toggles to enable, disable, or measure individual passes by name.

## Acceptance Criteria

- Adding a new token-reduction strategy requires implementing and registering a `ReductionPass` without modifying
  `clean_payload.py` control flow or provider string branches.
- Unit tests verify deterministic ordering, toggle/isolation, and A/B pass comparison.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Coordinate with Bean `0527` (`ProviderFormat` seam) and Bean `0528` (single-copy hot path).
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
