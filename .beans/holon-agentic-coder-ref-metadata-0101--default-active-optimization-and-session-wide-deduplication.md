---
# holon-agentic-coder-ref-metadata-0101
title: "Default proxy to active optimization and implement session-wide tool deduplication"
status: completed
type: feature
priority: high
tags:
  - coherence
  - optimization
  - deduplication
  - token-reduction
  - context-cleaner
created_at: 2026-10-17T00:37:00Z
updated_at: 2026-10-17T01:30:00Z
---

## Summary

Enhance `holon-coherence` context optimization engine to always run in active optimization mode by default and extend
tool output deduplication across the entire agent conversation session:

1. **Active Optimization by Default**:
   - Ensure the proxy always defaults to active optimization (`COHERENCE_TOKEN_REDUCTION=1`,
     `HOLON_PASSIVE_MONITORING=0`) in container start, CLI runners, and proxy interceptor initialization.
   - Passive monitoring must be strictly opt-in via explicit flags (`--passive` or `HOLON_PASSIVE_MONITORING=1`) or
     per-request headers (`X-Holon-Mode: baseline` / `X-Holon-Passive: 1`) used during A/B testing comparisons.

2. **Session-Wide Tool Output Deduplication**:
   - Retire the hardcoded `_RECENT_TURNS_TO_KEEP = 6` limitation in `src/holon_coherence/payload_cleaner.py`.
   - Track tool output content hashes across the **entire multi-turn trajectory**, spanning long agent workflows (15–50+
     turns).
   - When an identical tool output appears in multiple turns (e.g. repeated `git status`, test runs, directory
     listings), prune the repetitive verbose body while strictly preserving the tool protocol envelope (`tool_use_id` /
     `tool_call_id`, tool name, and turn structure) so upstream provider schemas remain completely valid.
   - Replace redundant bodies with structured tombstones (e.g.
     `[Tool output omitted: identical output matches Turn N]`).
   - Maintain KV cache prefix alignment so compaction does not inadvertently break upstream server-side KV caching.

## Target Repository & Files

- Repository: `holon-coherence` (`apps/holon-coherence/`)
- Target Files:
  - `src/holon_coherence/payload_cleaner.py`
  - `src/holon_coherence/mitm_addon.py`
  - `src/holon_coherence/commands/start.py`
  - `tests/test_payload_cleaner.py`
  - `tests/test_mitm_addon.py`
  - `docs/ab_testing_guide.md`

## Acceptance Criteria

- [x] Proxy boots in active optimization mode by default without requiring manual environment variables.
- [x] Tool output deduplication operates across the entire conversation history instead of being bounded by a 6-turn
      window.
- [x] Tool call protocol IDs (`tool_use_id`, `id`) and message sequences are preserved with zero schema validation
      errors across Anthropic, OpenAI, and Gemini formats.
- [x] Real workload A/B benchmarks demonstrate measurable token reduction (>15%) on repetitive multi-turn agent traces.
- [x] All unit and integration tests pass cleanly and linters report 0 errors.

## Notes

- Complements Bean 0098 (A/B testing suite), ensuring Variant B exercises full session-wide deduplication against
  unoptimized Variant A.
- Strictly adheres to Rule 10 (Zero synthetic data for benchmarks).

## Resolution

Implemented via the 5-stage Holon flow:

1. **Flow Branches**:
   - Intent branch: `I-1792158378-active-opt-dedup-and-throughput-terminology/_`
   - Plan branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/_`
   - Execution branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/E-1792158381-antigravity-agent-gemini-3.8-flash-medium/_`
   - Calibrated branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/E-1792158381-antigravity-agent-gemini-3.8-flash-medium/calibrated`
2. **Pull Request**:
   - [Holon-Agentic-Coder/holon-coherence#22](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/22)
3. **Review & Calibration**:
   - Unanimously approved by 3-agent ensemble review (`pr-reviewer` skill).
   - Calibrated via `holon calibrate` with calibration report merged into PR head branch ($\Delta EV$ -72.24).
   - All 630 tests passed; GitHub Actions CI 7/7 passed cleanly.
   - Merged into `origin/main` (commit `ded9f80`) on 2026-10-17.
