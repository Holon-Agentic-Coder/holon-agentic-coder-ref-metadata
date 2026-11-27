---
# holon-agentic-coder-ref-metadata-0527
title: "Unify provider detection, make ProviderFormat extensible, and break import cycles"
status: in-progress
type: task
priority: high
tags:
  - holon-coherence
  - architecture
  - extensibility
  - refactor
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T17:35:46Z
---

## Problem

Provider detection logic is duplicated and already diverges between the proxy addon and the provider registry. Extending
`holon-coherence` with a new LLM provider requires editing closed `Literal` types and hardcoded provider branches across
multiple modules, while circular imports connect `parsers/` ↔ `providers/` and `commands/docker_ops.py` ↔
`commands/endpoints.py`.

## Evidence

- `src/holon_coherence/proxy/addon.py:82-126` (`detect_provider`) vs `src/holon_coherence/providers/__init__.py:69-115`:
  disagree on `"claude"` model and `"system"`-vs-`"messages"` detection precedence.
- `src/holon_coherence/providers/base.py:10`: closed `ProviderName = Literal["anthropic", "openai", "gemini"]`;
  `ProviderFormat` lacks a `matches(url, payload)` seam; concrete providers nominally inherit from `Protocol`.
- `src/holon_coherence/parsers/sse.py:44-57`: hardcoded `KNOWN_PROVIDERS` omits `ollama`/`vllm`.
- `src/holon_coherence/proxy/routing.py:78-86`, `src/holon_coherence/proxy/steps/clean_payload.py:54-58`: branch on
  provider name strings; `src/holon_coherence/hybrid_cache.py:173-175` ignores its `provider` parameter.
- Import cycles: `parsers/tokens.py:84` and `parsers/sse.py:58,64` deferred-import `providers.get_provider`;
  `commands/docker_ops.py:24-25,122` ↔ `commands/endpoints.py:6-10`; sibling imports from `providers/anthropic.py` in
  `providers/openai.py:11` and `providers/gemini.py:11`.
- Newly surfaced AST cycle (`c26a0c1` audit): `payload_cleaner(2) <-> providers(4)` bidirectional package cycle
  (`src/holon_coherence/payload_cleaner.py` ↔ `src/holon_coherence/providers/`).
- Duplicate `in_container` helper in `src/holon_coherence/host_local.py:218-219` and
  `src/holon_coherence/container/lifecycle.py:153-154`.

## Proposed Change

1. Move shared message/turn helpers (`merge_consecutive_roles`, etc.) into a leaf `providers/_common.py` module and use
   structural `Protocol` typing instead of inheriting from `ProviderFormat`.
2. Add a `matches(url, payload)` (and capability/header hooks) seam to `ProviderFormat` so `detect_provider` delegates
   to a single registry-ordered lookup and `KNOWN_PROVIDERS` is derived dynamically from the registry (covering
   `ollama`/`vllm`).
3. Break all import cycles (`parsers/` ↔ `providers/`, `payload_cleaner` ↔ `providers/`, and `commands/docker_ops.py` ↔
   `commands/endpoints.py`) and add an acyclic-import boundary test.
4. Consolidate `in_container` into a single shared helper.

## Acceptance Criteria

- Exactly one provider-detection code path exists across `proxy/addon.py` and `providers/`.
- Zero circular imports remain between `parsers/`, `payload_cleaner`, `providers/`, and `commands/` (verified by an
  automated import test).
- Registering a new provider via `register_provider()` requires no core `Literal` or string `if/elif` edits.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- Audit refresh (`2026-11-27`, `ce39bf34d`): PR `#63` (`0524` slice 1) added a new bidirectional cycle
  `commands <-> container` (`4 <-> 3`: `container/lifecycle.py:443,468,494` imports `commands.web_token`), and PR `#61`
  added a `TYPE_CHECKING` back-edge `reduction_passes -> payload_cleaner` (`1 <-> 1`). Move `web_token` helpers into
  `container/` or a shared leaf and include both edges in the acyclic-import boundary test (coordinated with Bean
  `0621`).
- Audit refresh (`2026-11-27`, `4a02926b`): Live root+subpackage AST scan also surfaced a fifth bidirectional cycle
  `hybrid_cache (1) <-> proxy (1)` (`src/holon_coherence/hybrid_cache.py:35` imports `holon_coherence.proxy.scrubbing`
  <-> `src/holon_coherence/proxy/addon.py:11` imports `holon_coherence.hybrid_cache`). Note
  `tests/test_import_cycle_ratchet.py` (`#76`) currently inspects subpackages only (extending to root modules tracked in
  Bean `0632`). `0527` slice 1 (`coherence-provider-format-seam`) hit `CF-0061` on pre-`#77` branch `334357d` and was
  re-cut onto `4a02926b`.

## Flow

- **Progress (`2026-11-27`):** [PR #84](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/84)
  (`coherence-provider-format-seam`, merge commit `71d46b44`, `Predicted EV 2.63 / Actual EV 5.70 / ΔEV +3.07`) merged
  into `main`, extracting `src/holon_coherence/providers/_common.py`, adding structural `ProviderFormat.matches()` in
  `providers/base.py`, unifying detection/lookup across `providers/registry.py`, `proxy/addon.py`, and
  `proxy/routing.py`, deriving `KNOWN_PROVIDERS` dynamically in `parsers/sse.py`, breaking the `parsers/` ↔ `providers/`
  import cycle, and adding tests in `tests/providers/test_provider_format_seam.py`. Bean remains `in-progress` because
  remaining import cycles (`commands/docker_ops.py` ↔ `commands/endpoints.py`, `payload_cleaner` ↔ `providers/`,
  `commands` ↔ `container`, `hybrid_cache` ↔ `proxy`) and `in_container` consolidation remain open.
- **Progress (`2026-11-27`):** Slice 2 (`coherence-commands-cycle`,
  [PR #87](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/87)) completed all 5 stages (`APPROVED`, `10/10`
  CI passed, `ΔEV +0.30`; awaiting maintainer merge).
- **Progress (`2026-11-27`):** Slice 3 (`coherence-docker-endpoints`,
  [PR #92](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/92), branch
  `I-1795799828-coherence-docker-endpoints/P-1795799850-ANA-G4N/E-1795800022-ANA-G4N/_`) completed all 5 stages on
  `antigravity-agent`/`gemini-4-neon` (`APPROVED` 3/3 on iteration 1, `10/10` CI passed, `MERGEABLE`/`CLEAN`,
  `Predicted EV -0.77 / Actual EV 0.28 / ΔEV +1.05`; calibration report
  `plans/I-1795799828-coherence-docker-endpoints/P-1795799850-ANA-G4N_calibration.md` in PR diff; checkpoint
  `apps/holon-coherence/flow-coherence-docker-endpoints/.holon/flow/checkpoint-coherence-docker-endpoints.json`;
  awaiting maintainer merge).
