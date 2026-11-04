---
# holon-agentic-coder-ref-metadata-0227
title:
  "Sidecar readiness probe false positive: docker-proxy accepts TCP before mitmproxy binds, role container gets
  connection refused"
status: in-progress
type: bug
priority: high
tags:
  - token-reduce
  - proxy
  - flow
  - holon-agentic-coder
created_at: 2026-11-04T08:10:00Z
updated_at: 2026-11-04T09:30:00Z
---

## Problem

Observed 2026-11-04 during the maintainer's manual end-to-end flow run: Stage 1 dispatched the role container
immediately after starting the mitmproxy sidecar, and the container's `git clone` failed with
`Failed to connect to holon-proxy-<suffix> port 8080 after 0 ms`. `setup_token_reduction_proxy` does gate on
`_wait_for_proxy`, but that probe is a bare TCP connect to the PUBLISHED HOST PORT — and Docker's userland proxy
(docker-proxy) accepts TCP on the host port the moment the container starts, before mitmproxy inside has bound its
listener. The probe therefore passes instantly (false positive) while the role container, dialling the sidecar directly
on the per-run docker network, is refused until mitmdump finishes booting.

Secondary surprise (documented, not changed here): `detect_holon_coherence` auto-enables token-reduce via its tiered
probes (a live 127.0.0.1:8080 listener, the holon-coherence image, or the CLI on PATH), so the sidecar engages even
without `--token-reduce` unless `HOLON_TOKEN_REDUCE=0` is set.

## Fix

Make `_wait_for_proxy` an HTTP-level probe: connect, send a minimal proxy-style request, and require actual `HTTP/`
response bytes before declaring ready (mitmproxy answers even for an unresolvable upstream, e.g. 502). A connection that
is accepted but closed or reset without an HTTP response (docker-proxy with no backend yet) is not-ready and is retried
until the existing `PROXY_READY_TIMEOUT_SECONDS` deadline. Unit tests fake both server behaviours with local socket
listeners.

## Notes

- Hand-authored fix in a local worktree under the explicit maintainer instruction of 2026-11-04 ("if there's any issues
  I want you to fix it directly without using the holon and with local worktree") — the named exception to the flow-only
  rule; it is recorded in the commit message.

## Resolution (2026-11-04)

Fixed hand-authored on branch `fix/0227-proxy-readiness-http-probe` (commit `36c9765`), pushed to origin.
`_wait_for_proxy` now sends a proxy-style request for `holon-proxy-readiness.invalid` and declares readiness only on
`HTTP/` response bytes; accept-then-silent-close (docker-proxy with no backend yet) retries until the existing 15 s
deadline. Three real-socket unit tests cover silent-close, immediate-502 and boot-then-answer. Full sandbox-executor
suite green (2900 passed, 1 skipped). Awaiting maintainer decision on PR creation/merge.
