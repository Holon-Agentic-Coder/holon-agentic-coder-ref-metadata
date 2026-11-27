---
# holon-agentic-coder-ref-metadata-0527
title: "Unify provider detection, make ProviderFormat extensible, and break import cycles"
status: todo
type: task
priority: high
tags:
  - holon-coherence
  - architecture
  - extensibility
  - refactor
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T05:26:34Z
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
