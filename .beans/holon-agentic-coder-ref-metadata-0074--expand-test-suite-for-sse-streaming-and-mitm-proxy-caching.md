---
# holon-agentic-coder-ref-metadata-0074
title: "Expand test suite for SSE streaming, network chunking, and proxy cache integration"
status: todo
type: task
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-07T12:50:00Z
---

## Summary

In `holon-coherence`, `mitm_addon.py` comprises over 1,400 lines handling complex Server-Sent Events (SSE) streaming for
Anthropic, OpenAI, and Gemini APIs, partial chunk reassembly, and live telemetry. The current unit test suite
extensively tests `cli.py` and `host_local.py`, but has limited coverage for `mitm_addon.py` response streaming,
fragmented buffer parsing, and proxy cache eviction edge cases.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Add comprehensive unit tests for `mitm_addon.py` mocking mitmproxy `HTTPFlow` events across all supported provider
  streaming formats (OpenAI delta chunks, Anthropic SSE content blocks, Gemini chunks).
- Test fragmented and chunked SSE buffers arriving across multiple TCP packet boundaries to verify zero token count
  truncation.
- Add tests for error conditions, upstream connection resets, and proxy fallback behavior.
- Ensure test coverage for `mitm_addon.py` exceeds 85%.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Findings QA-01, QA-02,
  BUG-02).
