---
# holon-agentic-coder-ref-metadata-0526
title: "Fix SSE chunk fragmentation bugs and add real mitmproxy tflow wire-level tests"
status: in-progress
type: bug
priority: high
tags:
  - holon-coherence
  - sse
  - proxy
  - testing
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T07:35:24Z
---

## Problem

Streaming SSE handlers split raw TCP byte chunks without carrying incomplete lines or multi-byte UTF-8 sequences across
chunk boundaries, silently corrupting or dropping fragmented events. Because the test suite contains zero tests built on
real `mitmproxy.http.HTTPFlow` (`tflow`) or a local HTTP server, these wire-level bugs went undetected, while
integration tests still hit external hosts and mix legacy `unittest.TestCase`.

## Evidence

- `src/holon_coherence/providers/translation.py:426-442`: splits TCP chunks on `\n` with no incomplete-line carry
  buffer, silently dropping JSON events split across chunks.
- `src/holon_coherence/proxy/steps/sse_tap.py:41-47`: decodes raw byte chunks without an incremental UTF-8 decoder and
  contains a dead self-assignment at line 47.
- Zero tests in `tests/` construct real `mitmproxy.http.HTTPFlow` (`mitmproxy.test.tflow`) or exercise a local
  `HTTPServer` despite `mitmproxy==12.2.3` in dev dependencies.
- `tests/test_docker_integration.py:31`: makes live HTTP calls to `http://example.com`.
- `tests/test_coherence.py` and `tests/test_docker_integration.py`: use legacy `unittest.TestCase`.
- `src/holon_coherence/rag_indexer.py:23`: references `rag_indexer`, bypassed `tests/test_repo_hygiene.py:41`
  (`\.beans/` regex).

## Proposed Change

1. Add an incomplete-line carry buffer in `providers/translation.py` and use `codecs.getincrementaldecoder("utf-8")` in
   `proxy/steps/sse_tap.py` (removing the dead self-assignment at line 47).
2. Add real `mitmproxy.test.tflow` and local `HTTPServer` wire tests covering fragmented SSE JSON lines, split
   multi-byte UTF-8 characters, Host-header routing, and dashboard isolation.
3. Replace the live `http://example.com` call in `tests/test_docker_integration.py` with a local test server and migrate
   remaining `unittest.TestCase` classes to pure pytest.
4. Remove legacy references from `rag_indexer.py:23` and tighten `tests/test_repo_hygiene.py`.

## Acceptance Criteria

- Fragmented SSE JSON lines and split multi-byte UTF-8 code points across arbitrary chunk boundaries translate and tap
  with zero dropped events or decode errors.
- Wire tests using mitmproxy.test.tflow and local HTTPServer pass offline with uv run pytest.
- Zero unittest.TestCase subclasses and zero harness references remain in holon-coherence.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
