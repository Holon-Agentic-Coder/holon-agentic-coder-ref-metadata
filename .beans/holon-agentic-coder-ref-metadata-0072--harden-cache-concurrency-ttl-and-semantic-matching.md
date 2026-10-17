---
# holon-agentic-coder-ref-metadata-0072
title: "Harden cache concurrency, TTL expiration, and semantic matching performance"
status: completed
type: task
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-12T19:00:00Z
---

## Summary

In `holon-coherence`, `HybridCache` operates an in-memory dictionary synchronized with an SQLite store. Under
multi-client concurrency or proxy load:

1. `_lookup_semantic` sequentially deserializes and tokenizes up to 100 historical payloads on every cache miss, causing
   CPU spikes.
2. TTL expiration pruning occurs in-line during writes without lock isolation or background sweeping, leading to write
   amplification.
3. Concurrent writes to SQLite lack explicit busy timeouts and WAL mode journal handling.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Enable SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`) for robust concurrent access.
- Precompute and store minhash / token shingles in SQLite columns to eliminate full-payload deserialization and
  tokenization on semantic cache misses.
- Implement background or batch TTL eviction rather than per-write prune scans.
- Add stress and concurrency tests for `HybridCache` under simulated parallel agent workloads.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Findings PERF-01,
  BUG-03, BUG-04).

## Progress (2026-10-11)

`holon-coherence` branch `feat/0072-0074-cache-concurrency-and-sse-tests`, commit `dcd9739` (pushed, PR not yet
created). Worktree `apps/holon-coherence/feat-0072-0074-cache-concurrency-and-sse-tests`.

**Done — PERF-01.** A semantic miss no longer deserialises and re-tokenises up to `candidate_limit` stored payloads.
`prompt_cache` carries `user_tokens` and `system_hash`, written on `put`; the scan compares the digest and splits stored
tokens. Pre-shingle rows are migrated on open and backfilled on first read, so the slow path runs once per row instead
of once per miss. New `tests/test_hybrid_cache.py` (8 tests, the module previously had none), including a regression
test that counts extractor calls and permits exactly one. Full suite 294 passed; the one failure
(`test_cli.py::…::test_ca_cert_missing_diagnostic_warning`) reproduces identically on pristine `origin/main`, so it is
pre-existing and not attributable here.

**Done — part of BUG-03.** Connections were opened with `with sqlite3.connect(...)`, which commits but never closes,
leaking a handle that pins a WAL read snapshot on every cache call. One context manager now sets `busy_timeout` and
`synchronous=NORMAL` and closes in `finally`.

**Corrected premise — the TTL task.** This bean states that "TTL expiration pruning occurs in-line during writes without
lock isolation". There is **no TTL, expiry or prune code anywhere in `src/holon_coherence`** (grep for
`ttl|expire|prune` returns only unrelated `ca_generator.py` certificate expiry). So nothing is being pruned in-line, and
nothing is expiring: cache entries live forever. The task is therefore _add_ batched TTL eviction, not relocate an
existing prune. That also makes the audit's write-amplification framing moot — the real defect is unbounded growth.

**Done — BUG-04 (TTL eviction & expiry, commit `960b34e`).** Implemented batched, time-gated TTL eviction and
expiry-aware reads:

- Reads filter by age: both exact and semantic lookup exclude expired entries before sweeping.
- Writes trigger time-gated sweep (default every 300s, not per-write) to prevent write amplification.
- Deletion is batched (default 5000 rows per DELETE).
- `ttl_seconds=604800` (7 days default), configurable per instance (`ttl_seconds=0` disables expiry).
- 13 unit tests passed in `tests/test_hybrid_cache.py`.

**Holon Flow Execution:** Batch execution with Bean 0074 traversed Stages 1–3 on `holon-coherence` building directly off
`feat/0072-0074-cache-concurrency-and-sse-tests`:

- Stage 1 (Intent): `I-1791726197-cache-concurrency-and-sse-test-suite/_` (commit `0a992e8`)
- Stage 2 (Plan): `P-1791726209-antigravity-agent-gemini-3.8-flash-medium` (commit `58e091f`)
- Stage 3 (Execute): `E-1791726594-antigravity-agent-gemini-3.8-flash-medium` (commit `bbee02a`)
- Verified cache WAL mode, TTL eviction, and concurrency stress testing in `tests/test_hybrid_cache.py`.
- Pull Request: [#14](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/14) targeting `main`.
- Review Loop: 3-agent ensemble consensus approved (PR #14).
- Calibration probe: Evaluated commit `bbee02aa525c5d238bfbae0c1f6457048b7d1063`, actual EV 46.71 (predicted 35.0,
  $\Delta EV$ +11.71), test pass rate 1.0 (exit code 0).
- Merged: PR #14 merged into `origin/main` on 2026-10-12 (merge commit `77c29abb60b86ca329869216237a66736990fa5c`).
