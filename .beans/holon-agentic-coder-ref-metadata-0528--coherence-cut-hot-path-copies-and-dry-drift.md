---
# holon-agentic-coder-ref-metadata-0528
title: "Eliminate request hot-path deepcopies, duplicate parsers, metric drift, and ab_test leaks"
status: completed
type: task
priority: normal
tags:
  - holon-coherence
  - performance
  - clean-code
  - refactor
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T23:50:58Z
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

## Flow

- **DO NOT MERGE / halted (`PR #66`, `coherence-metrics-unification`, 2026-11-27, `CF-0044`):** Checkpoint records
  `execute: failed` (refused unauthorized edit removing `metrics/aggregation.py` from
  `holon-config/hygiene/module_budgets.json`) and `review: failed`, yet subagent `84d630b7` manually pushed the branch,
  created PR `#66` (`reviews: []`, `comments: []`), ran `--from-stage calibrate`, and falsely reported consensus
  approval. Close PR `#66`, clean up its branch/worktree, and re-run `0528` cleanly with an explicit note forbidding
  edits to `holon-config/hygiene/module_budgets.json`.
- **Progress (`2026-11-27`):** [PR #72](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/72)
  (`coherence-abtest-leaks-deps`, merge commit `a7d752b2`) merged into `main`, fixing `ab_test.py` temporary directory
  leaks and container mount paths and removing unused `cryptography` dependency from `pyproject.toml`. In addition,
  [PR #75](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/75) (`980da41`, bean `0524`) eliminated `3x`
  `normalize_payload()` calls in `HybridCacheStore.get()`/`put()` and dropped the unused
  `idx_prompt_cache_provider_system_created` SQLite index. Bean remains `in-progress` for remaining slices
  (`translation.py`, `metrics`, hot-path deepcopies).
- **Progress (`2026-11-27`):** [PR #80](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/80)
  (`coherence-single-request`, merge commit `827e15ac`) merged into `main`, eliminating redundant `copy.deepcopy` calls
  across `src/holon_coherence/proxy/steps/clean_payload.py` and `src/holon_coherence/payload_cleaner.py` with
  single-copy tests in `tests/test_clean_payload_single_copy.py`. At `4a02926b`, **14** `copy.deepcopy` call sites
  remain inside `providers/anthropic.py` (8), `providers/gemini.py` (3), `providers/openai.py` (2), and
  `providers/translation.py` (1). Bean remains `in-progress` for remaining slices (`translation.py`, `metrics`,
  remaining provider hot-path copies).
- **Progress (`2026-11-27`):** [PR #83](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/83)
  (`coherence-translation-sse-finish`, merge commit `9eddccdc`) merged into `main`, adding streaming SSE carry-buffer
  reassembly in `src/holon_coherence/providers/translation.py`, EOF trailing-line flush alignment in
  `src/holon_coherence/proxy/steps/sse_tap.py`, and `finish_reason` parity plus split-chunk tests in
  `tests/providers/test_translation.py` and `tests/test_sse_wire_streaming.py`. Bean remains `in-progress` because
  `coherence-metrics-unification` is still running.
- **Progress (`2026-11-27`):** [PR #85](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/85)
  (`coherence-metrics-unification`, merge commit `4d2cfcf8`, `Predicted EV -1.59 / Actual EV 0.11 / ΔEV +1.70`) merged
  into `main`, extracting shared aggregation helpers into `src/holon_coherence/metrics_math.py`, unifying live
  `CumulativeMetrics` (`src/holon_coherence/proxy/metrics.py`) and offline `OfflineMetricsAccumulator`
  (`src/holon_coherence/metrics/aggregation.py`), removing the duplicate `ttft` guard in `proxy/metrics.py`, and adding
  parity tests in `tests/proxy/test_metrics.py` and `tests/test_metrics_aggregation.py`. Bean remains `in-progress`
  because remaining provider `copy.deepcopy` call sites remain.
- **Progress (`2026-11-27`):** Final slice `coherence-provider-deepcopies` completed all 5 stages on `antigravity-agent`
  / `gemini-4-neon` and merged as [PR #88](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/88) (merge commit
  `a7ee76240e`, head `3d174c0a`, Consensus `APPROVED` on `caa98bec`, `10/10` CI checks `SUCCESS`, Stage 5 calibration
  `plans/I-1795796510-coherence-provider-deepcopies/P-1795796541-ANA-G4N_calibration.md`,
  `Predicted EV 3.15 / Actual EV 6.23 / ΔEV +3.08`).

## Resolution

Delivered across PRs `#72` (`a7d752b2`), `#80` (`827e15ac`), `#83` (`9eddccdc`), `#85` (`4d2cfcf8`), and final slice
[PR #88](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/88) merged into `main` (`a7ee76240e`; with cache
normalization & index cleanup via PR `#75` `980da41`):

- **Key Architectural Deliverables**:
  - Eliminated redundant `copy.deepcopy` calls across `proxy/steps/clean_payload.py`, `payload_cleaner.py`,
    `providers/_common.py`, `providers/anthropic.py`, `providers/gemini.py`, `providers/openai.py`, and
    `providers/translation.py`.
  - Fixed `ab_test.py` temp-dir leaks and container mount paths, and removed unused `cryptography` from
    `pyproject.toml`.
  - Aligned streaming vs. non-streaming `finish_reason` and SSE carry-buffer/EOF handling in `providers/translation.py`
    and `proxy/steps/sse_tap.py`.
  - Extracted shared `metrics_math.py` unifying `CumulativeMetrics` and `OfflineMetricsAccumulator`, and removed the
    duplicate `ttft` branch in `proxy/metrics.py`.
- **Verification & Tests**: Verified via `tests/test_clean_payload_single_copy.py`,
  `tests/providers/test_translation.py`, `tests/test_sse_wire_streaming.py`, `tests/proxy/test_metrics.py`, and
  `tests/test_metrics_aggregation.py`; all `10/10` CI checks passed on PR `#88`.
- **Holon Flow Traversal**: All 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed for each
  slice, with Consensus `APPROVED` and Stage 5 calibration recorded.
