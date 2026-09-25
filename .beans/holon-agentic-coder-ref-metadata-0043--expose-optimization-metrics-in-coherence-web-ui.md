---
# holon-agentic-coder-ref-metadata-0043
title: "Expose comprehensive optimization metrics in holon-coherence web interface"
status: todo
type: task
priority: normal
tags:
  - web-ui
  - holon-coherence
  - metrics
  - telemetry
created_at: 2026-09-26T09:25:00Z
updated_at: 2026-09-26T15:20:00Z
---

Enhance the `holon-coherence` web interface to display live, aggregate optimization metrics—including tool calls saved,
tokens reduced, prompt cache hit rate, and latency improvements.

## Context

`holon-coherence` intercepts and optimizes LLM requests by deduplicating historical tool payloads, injecting prompt
cache control breakpoints, and managing local semantic and exact disk caches. While individual turns emit telemetry into
`X-Holon-*` headers and log to `transactions.jsonl`, operators accessing the web dashboard currently lack a unified
overview of cumulative savings and efficiency gains.

## Acceptance Criteria

1. **In-Addon Metrics Aggregator**:
   - Aggregate cumulative statistics across intercepted LLM transactions in `holon_coherence.mitm_addon`:
     - Total tool calls saved / deduplicated (`tool_outputs_omitted`).
     - Total tokens reduced (untransmitted prompt tokens, pruned payload characters, and prompt cache reads).
     - Global prompt cache hit rate (`cache_read_tokens / total_prompt_tokens` and exact local cache hits).
     - Average Time To First Token (TTFT) and decode throughput (Output TPS).
     - Total turns processed, requests cleaned, and total cost/token savings.
2. **Web API Endpoint**:
   - Intercept requests to `/holon/api/metrics` (or `/_holon/metrics`) directly within `mitm_addon.py` to return the
     live JSON metrics payload.
3. **Web Dashboard Visual Interface**:
   - Serve a visual dashboard at `/holon/` (accessible at `http://127.0.0.1:<web_port>/holon/`) featuring real-time
     statistical cards:
     - 🛠️ **Tool Calls Saved**: Count of redundant tool calls and output payloads pruned.
     - 📉 **Tokens Reduced**: Absolute token count and percentage reduction.
     - 🎯 **Cache Hit Rate**: Live provider and local cache hit ratios.
     - ⏱️ **Latency & Speedup**: TTFT reduction and throughput metrics.
   - Include auto-refreshing capability (via periodic poll or Server-Sent Events).
4. **CLI Summary Support**:
   - Expose `holon-coherence metrics` (or include in `holon-coherence status`) to query and print the active metrics
     table in the terminal.
5. **Documentation & Testing**:
   - Update `apps/holon-coherence/README.md` with descriptions and screenshots/examples of the web metrics dashboard.
   - Add unit tests in `apps/holon-coherence/tests/test_mitm_addon.py` and `tests/test_cli.py` verifying accurate
     metrics accumulation and HTTP endpoint delivery.

## Notes

- Target repository: `apps/holon-coherence/`
- Target files:
  - `src/holon_coherence/mitm_addon.py`
  - `src/holon_coherence/cli.py`
  - `tests/test_mitm_addon.py`
  - `README.md`

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: no `/holon/api/metrics` (or `/_holon/metrics`)
endpoint, no dashboard route and no `metrics` CLI command exist in `apps/holon-coherence/src/holon_coherence/`.
