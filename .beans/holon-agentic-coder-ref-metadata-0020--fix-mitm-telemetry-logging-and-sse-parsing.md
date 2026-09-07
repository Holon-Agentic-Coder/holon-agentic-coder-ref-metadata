---
id: holon-agentic-coder-ref-metadata-0020
title: Fix MITM Telemetry Log Formatting and SSE Stream Token Extraction
status: done
type: task
created_at: 2026-08-31T21:38:00+10:00
updated_at: 2026-08-31T21:41:00+10:00
---

# Fix MITM Telemetry Log Formatting and SSE Stream Token Extraction

## Context

Fixed duplicate log formatting output and token count extraction for nested SSE stream payloads in `mitm_addon.py`.

## Resolution Summary

1. **Holon Flow Lifecycle**:
   - Created intent `./holon intent intents/fix-mitm-telemetry-logging-and-sse-parsing.json` ->
     `I-1788176325-fix-mitm-telemetry-logging-and-sse-parsing/_`.
   - Generated plan
     `./holon plan I-1788176325-fix-mitm-telemetry-logging-and-sse-parsing/_ --agent antigravity-agent --model gemini-3.5-flash`
     -> `P-1788176334-antigravity-agent-gemini-3.5-flash/_`.
   - Executed `./holon execute` for end-to-end sandbox execution.

2. **Telemetry Log Deduplication**:
   - Updated `log_telemetry()` in `mitm_addon.py` to route exclusively through `mitmproxy.ctx.log.info` when running
     inside `mitmdump`, eliminating duplicate log lines.

3. **Nested SSE Payload Token Extraction**:
   - Added `find_nested_key()` recursive search helper to unwrap nested response objects (`"response"`, `"result"`,
     `"data"`) found in Cloud Code PA / Antigravity streaming payloads (`v1internal:streamGenerateContent`).
   - Standardized Cache status logging on both Cache Hits and Cache Misses (`Cache: MISS (Hit Rate: 0.0%)` /
     `Cache: HIT (Hit Rate: 50.0%)`).
