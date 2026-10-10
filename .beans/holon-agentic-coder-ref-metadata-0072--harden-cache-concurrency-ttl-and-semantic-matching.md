---
# holon-agentic-coder-ref-metadata-0072
title: "Harden cache concurrency, TTL expiration, and semantic matching performance"
status: todo
type: task
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-07T12:50:00Z
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
