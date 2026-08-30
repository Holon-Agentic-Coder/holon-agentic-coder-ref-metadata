---
id: holon-agentic-coder-ref-metadata-0017
title: Implement MITM Proxy Telemetry & Streaming TPS Metrics
status: done
type: task
created_at: 2026-08-30T21:16:00+10:00
updated_at: 2026-08-30T21:17:00+10:00
---

# Implement MITM Proxy Telemetry & Streaming TPS Metrics

## Context

Implemented `docs/optimisation/mitm_telemetry_metrics_plan.md` in the reference repository inside dedicated Git worktree
`holon-agentic-coder-ref/feat-0017-mitm-telemetry-metrics` on branch `feat/0017-mitm-telemetry-metrics`.

## Resolution Summary

1. **Created Worktree**:
   - Created Git worktree `holon-agentic-coder-ref/feat-0017-mitm-telemetry-metrics` off `origin/develop`.

2. **Implemented Telemetry Calculation & Flow Hooks (`mitm_addon.py`)**:
   - Built `compute_telemetry_metrics()` to calculate high-resolution streaming latency, throughput, and caching
     metrics:
     - `ttft_ms` (Time-To-First-Token in ms)
     - `decode_time_sec` (Generation duration in sec)
     - `total_time_ms` (Total end-to-end request duration in ms)
     - `prefill_tps` (Prompt processing throughput in tokens/sec)
     - `tail_prefill_tps` (Effective throughput on uncached prompt tokens in tokens/sec)
     - `output_tps` (Generation throughput in tokens/sec)
     - `cache_hit_rate_pct` (Prompt cache hit rate %)
   - Extended `MitmproxyAddon` lifecycle callbacks:
     - `request(flow)`: Captures $T_{\text{start}}$ timestamp.
     - `responseheaders(flow)`: Captures $T_{\text{first}}$ timestamp upon first byte receipt.
     - `response(flow)`: Captures $T_{\text{end}}$ timestamp and injects response headers (`X-Holon-TTFT-Ms`,
       `X-Holon-Decode-Time-Sec`, `X-Holon-Total-Time-Ms`, `X-Holon-Prefill-TPS`, `X-Holon-Tail-Prefill-TPS`,
       `X-Holon-Output-TPS`, `X-Holon-Cache-Hit-Rate`).

3. **Testing & Verification**:
   - Added unit test suite in `apps/sandbox-executor/tests/test_token_reduction.py`:
     - `test_compute_telemetry_metrics`
     - `test_mitm_addon_flow_telemetry_headers`
   - Verified 56 unit tests pass 100% clean (`uv run pytest apps/sandbox-executor/tests/test_token_reduction.py`).

4. **Formatting**:
   - Formatted all markdown files with `npx prettier --write "**/*.md"`.
