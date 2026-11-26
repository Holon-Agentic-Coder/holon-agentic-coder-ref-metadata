---
# holon-agentic-coder-ref-metadata-0528
title: "Eliminate request hot-path deepcopies, duplicate parsers, metric drift, and ab_test leaks"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - performance
  - clean-code
  - refactor
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

The proxy request/response hot path executes redundant `copy.deepcopy` calls, duplicate token parsing, and triple
payload normalization per cache write, while duplicated SSE/text/metrics helpers cause subtle drift (including
inconsistent streaming vs. non-streaming `finish_reason` mapping) and `ab_test.py` leaks temporary directories and
passes host paths into containers.

## Evidence

- Up to 4× `copy.deepcopy` per request across `src/holon_coherence/proxy/steps/clean_payload.py:17`,
  `src/holon_coherence/payload_cleaner.py:52`, and `src/holon_coherence/providers/anthropic.py:44,68,96,106`; 2× token
  parsing per response; 3× `normalize_payload` per `HybridCacheStore.put()`.
- `src/holon_coherence/hybrid_cache.py:76-79,248-255`: unused SQLite index `idx_prompt_cache_provider_system_created`.
- 3× copy-pasted `_iter_sse_chunks` (`providers/anthropic.py:408`, `providers/openai.py:26`, `providers/gemini.py:25`)
  and 2× `_extract_item_text` (`anthropic.py:485`, `openai.py:228`).
- Divergent `CumulativeMetrics` (`src/holon_coherence/proxy/metrics.py`) vs `OfflineMetricsAccumulator`
  (`src/holon_coherence/metrics/aggregation.py`) and duplicate `if ttft is not None and ttft > 0:` condition at
  `proxy/metrics.py:87-91`.
- `src/holon_coherence/commands/ab_test.py:89-118`: leaks `mkdtemp` directory and passes host path into container
  execution.
- `src/holon_coherence/providers/translation.py:380-382` vs `252-255`: streaming and non-streaming paths produce
  inconsistent `finish_reason` values.
- `pyproject.toml:25`: unused `cryptography==48.0.1` runtime dependency.

## Proposed Change

1. Copy the request payload at most once at the step boundary, parse response tokens once, and normalize payloads once
   on cache `put()`.
2. Drop the unused `idx_prompt_cache_provider_system_created` SQLite index in `hybrid_cache.py`.
3. Extract shared `_iter_sse_chunks`, `_extract_item_text`, and live/offline metrics accumulation helpers; remove the
   duplicate `ttft` branch in `proxy/metrics.py`; align streaming vs. non-streaming `finish_reason`.
4. Fix `commands/ab_test.py` temp-dir lifecycle (`tempfile.TemporaryDirectory`) and container mount paths, and remove
   unused `cryptography==48.0.1` from `pyproject.toml`.

## Acceptance Criteria

- Hot-path proxy pipeline performs at most one defensive copy per mutated request and one token parse per response.
- Streaming and non-streaming translation yield matching `finish_reason` values for equivalent stop states.
- Live and offline metrics accumulators share core aggregation logic and `commands/ab_test.py` leaves no leaked
  `mkdtemp` directories.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
