---
# holon-agentic-coder-ref-metadata-0204
title: "holon-coherence: split mitm_addon.py into a proxy package by concern (move only, AST-verified)"
status: completed
type: task
priority: high
tags:
  - refactor
  - architecture
  - proxy
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0186
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T21:05:00Z
---

## Problem

Spawned by Bean 0177. `src/holon_coherence/mitm_addon.py` (`68fdf67`) is 2,348 lines (radon MI grade C) holding secret
scrubbing, wire logging, flow timing, cumulative metrics, local-target routing, Anthropic normalisation, Gemini/OpenAI
translation, the dashboard and the `MitmproxyAddon` hooks. 12 commits touched it; its tests are split over
`test_mitm_addon.py` (919) and `test_mitm_addon_sse.py` (1,341).

## Scope

1. Move without changing function bodies into `proxy/`: `scrubbing.py`, `wire_log.py`, `timing.py`, `metrics.py`
   (`CumulativeMetrics`), `routing.py` (`is_local_target`), `translation/gemini_openai.py`, `normalise/anthropic.py`,
   `dashboard.py` (with the HTML as a package asset file), `addon.py` (`MitmproxyAddon`, `MITMProxyInterceptor`).
2. `mitm_addon.py` stays as the mitmproxy script entry point re-exporting the addon, so the image and `-s` path are
   unchanged.
3. An AST comparison proves the move; tests mirror the new modules.

## Touch set

`src/holon_coherence/mitm_addon.py`, new `src/holon_coherence/proxy/`, `tests/test_mitm_addon*.py` (split), the
`Dockerfile` only if a package asset needs including.

## Dependencies

Blocked by 0186. Blocks 0205 and 0206. Parallel-safe with 0203.

## Resolution

Completed through the Holon flow on `holon-coherence`:

- Pull Request: [#37](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/37)
- Review: 3/3 unanimous approval with zero findings.
- Calibration: Stage 5 completed and merged into PR head.
- Merged into `main` at commit `9b001c3d4c8d8345a9095ef59adce5a738da9760`.

## Notes

- Run through the Holon flow on holon-coherence, alone on `mitm_addon.py`.
