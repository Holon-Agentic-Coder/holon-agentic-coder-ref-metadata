---
# holon-agentic-coder-ref-metadata-0074
title: "Expand test suite for SSE streaming, network chunking, and proxy cache integration"
status: completed
type: task
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-12T19:00:00Z
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

## Progress (2026-10-11)

New test module `tests/test_mitm_addon_sse.py` holds 90 tests. Same branch as Bean 0072:
`feat/0072-0074-cache-concurrency-and-sse-tests` in `holon-coherence` (worktree
`apps/holon-coherence/feat-0072-0074-cache-concurrency-and-sse-tests`). New file `tests/test_mitm_addon_sse.py`, 79
tests, in three tranches:

| Tranche | Commit    | Subject                                                          |
| :------ | :-------- | :--------------------------------------------------------------- |
| 1       | `9fffef8` | `extract_sse_content` reassembly: 3 providers, tools, truncation |
| 2       | `bdbd7be` | `extract_sse_token_counts`, cache-read, detailed mapping         |
| 3       | `026a9bc` | `scrub_string` / `scrub_headers` credential redaction            |
| 4       | `cad8cb3` | non-streaming token accounting and estimation fallback           |

**Measured coverage of `mitm_addon.py`: 21% → 58%** (`pytest --cov=holon_coherence.mitm_addon`, full suite,
`uv run --with pytest-cov`). The bean's target is **>85%**, so this is roughly halfway by statement count and the target
is **not** met. `tests/test_mitm_addon_sse.py` now holds 90 tests. The remaining ~370 statements are dominated by the
mitmproxy addon surface: `MitmproxyAddon.server_connect/request/responseheaders/response/_dump_flow_transaction`,
`MITMProxyInterceptor.intercept_request_with_stats`, and wire-log writing.

**Found while raising coverage (fixed on this branch, commit `b679387`)**: `build_agent_env` copies `os.environ` and
only overwrites the CA variables when the bundle resolves, so when it does not resolve the child inherits a CA path the
command has just reported missing. The existing test asserted the correct contract and passed only because CI runs with
a clean environment.

**Behaviour pinned, worth knowing even outside the tests**: Anthropic `input_tokens` is reported as the sum of fresh +
cache-read + cache-creation tokens; usage frames arrive last and a parser that stops early reports zero; thinking deltas
count toward the output estimate _and_ again as reasoning tokens.

**Holon Flow Execution:** Batch execution with Bean 0072 traversed Stages 1–3 on `holon-coherence` building directly off
`feat/0072-0074-cache-concurrency-and-sse-tests`:

- Stage 1 (Intent): `I-1791726197-cache-concurrency-and-sse-test-suite/_` (commit `0a992e8`)
- Stage 2 (Plan): `P-1791726209-antigravity-agent-gemini-3.8-flash-medium` (commit `58e091f`)
- Stage 3 (Execute): `E-1791726594-antigravity-agent-gemini-3.8-flash-medium` (commit `bbee02a`)
- Added comprehensive mitmproxy addon lifecycle hook and HTTPFlow unit tests in `tests/test_mitm_addon_sse.py` (+794
  lines), testing flow transaction dumping, streaming reassembly, and interception stats.
- Pull Request: [#14](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/14) targeting `main`.
- Review Loop: 3-agent ensemble consensus approved (PR #14).
- Calibration probe: Evaluated commit `bbee02aa525c5d238bfbae0c1f6457048b7d1063`, actual EV 46.71 (predicted 35.0,
  $\Delta EV$ +11.71), test pass rate 1.0 (exit code 0).
- Merged: PR #14 merged into `origin/main` on 2026-10-12 (merge commit `77c29abb60b86ca329869216237a66736990fa5c`).
