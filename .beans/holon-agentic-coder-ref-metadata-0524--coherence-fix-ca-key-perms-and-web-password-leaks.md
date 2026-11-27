---
# holon-agentic-coder-ref-metadata-0524
title: "Fix world-writable Root CA key permissions, web password leaks, and unscrubbed cache"
status: in-progress
type: bug
priority: critical
tags:
  - holon-coherence
  - security
  - ca
  - secrets
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T07:52:54Z
---

## Problem

`holon-coherence` generates its X.509 Root CA cleanly with `0o700`/`0o600` permissions in `ca_generator.py`, but
container startup immediately negates that hardening by enabling world-writable mount permissions (`0o777` directories
and `0o666` private key files), passing `HOLON_COHERENCE_WEB_PASSWORD` on container command lines and query strings, and
persisting unscrubbed LLM payloads inside the world-writable cache directory.

## Evidence

- `src/holon_coherence/commands/start.py:263`: passes `world_accessible_mounts=True`.
- `src/holon_coherence/container/lifecycle.py:39-40,309-320,423-424`: `chmod 0o777` on `~/.holon/proxy-ca`, `cache`, and
  `logs`, and `chmod 0o666` on `holon-root-ca.key` and `mitmproxy-ca.pem`, overriding
  `src/holon_coherence/ca_generator.py:12-26,67-89,162-189`.
- `src/holon_coherence/container/lifecycle.py:341-342,498-499`: exposes `HOLON_COHERENCE_WEB_PASSWORD` in
  `docker run -e` and `--set web_password=...` process argv.
- `src/holon_coherence/commands/endpoints.py:34`: leaks auth token in `?token=` query string.
- `src/holon_coherence/hybrid_cache.py:299-325`: `HybridCacheStore` writes unscrubbed LLM payloads into the `0o777`
  cache directory.

## Proposed Change

1. Remove `0o777`/`0o666` world-writable mount permissions (`world_accessible_mounts=True`); use proper container
   UID/GID mapping or read-only cert-only mounts while keeping Root CA private keys strictly `0o600` inside `0o700`
   directories.
2. Pass `web_password` via a `0o600` mounted file or temp env-file instead of `docker run -e` / CLI argv, and replace
   `?token=` URL query output with non-URL token delivery or header auth.
3. Scrub sensitive tokens/headers before persisting to `HybridCacheStore` and enforce `0o700`/`0o600` permissions on
   cache and log directories.

## Acceptance Criteria

- Starting the proxy container never sets `0o777` on `~/.holon/*` directories or `0o666` on `holon-root-ca.key` or
  `mitmproxy-ca.pem`.
- `HOLON_COHERENCE_WEB_PASSWORD` never appears in `docker run` arguments, mitmproxy `--set` argv, or endpoint URLs.
- Regression tests assert restrictive directory/key permissions (`0o700`/`0o600`) and scrubbed cache storage.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- parked 2026-11-27T07:33:03Z (flow `coherence-cache-scrub-endpoints`): blocked by PR #63
  (`I-1795760711-coherence-ca-key-perms/P-1795760732-ANA-G4N/E-1795760946-ANA-G4N/_`) on `tests/commands/test_start.py`,
  `tests/commands/test_web_token.py`; resume from checkpoint
  `apps/holon-coherence/flow-coherence-cache-scrub-endpoints/.holon/flow/checkpoint-coherence-cache-scrub-endpoints.json`
  when PR #63 merges.

## Progress (`2026-11-27`, Coherence PR `#63`)

- Slice 1 (`coherence-ca-key-perms`): merged via
  [holon-coherence#63](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/63) (`2a1a8562`). Worktree and flow
  branches pruned.
- Bean stays `in-progress` for slice 2 (`coherence-cache-scrub-endpoints`, now unblocked and ready to resume from
  checkpoint).
