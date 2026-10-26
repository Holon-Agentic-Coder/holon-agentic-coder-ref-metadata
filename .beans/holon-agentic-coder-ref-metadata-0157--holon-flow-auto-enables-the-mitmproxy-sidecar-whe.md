---
# holon-agentic-coder-ref-metadata-0157
title: "holon flow auto-enables the mitmproxy sidecar when the image exists, and role containers cannot reach it"
status: todo
type: bug
priority: high
tags:
  - holon-flow
  - token-reduce
  - proxy
  - holon-agentic-coder
created_at: 2026-10-26T04:23:42Z
updated_at: 2026-10-26T04:23:42Z
---

## Problem

Found on 2026-10-26 while running Bean 0151 through `holon flow --agent claude-agent` (log `todo/logs/0151-flow.log`).
No `--token-reduce`, `--mitm-web` or `HOLON_TOKEN_REDUCE` was set.

- `FlowContext` defaults `token_reduce` to `detect_holon_coherence()` (`sandbox_executor/flow.py` around line 310). That
  returns true when `mitmproxy/mitmproxy:12.2.3` or a holon-coherence image is merely present locally (tier 4 image
  probe). So every flow silently starts the TLS-intercepting sidecar. This contradicts
  `get_token_reduction_mounts_and_envs()` in `cli.py`, which says opt-in is strictly explicit.
- The sidecar (`holon-proxy-<pid>-<hex>`) then was not reachable from the intent-creator container:
  `git clone ... Failed to connect to holon-proxy-82284-86288f31 port 8080 after 0 ms`, exit 128. Stage 1 failed in 3
  seconds, even though the host-side readiness probe had passed.

Workaround: `HOLON_TOKEN_REDUCE=0`.

## Scope

- `holon flow` must use the same explicit opt-in rule as the per-stage commands. Auto-detection may only attach to an
  already running user-owned proxy, never spawn a sidecar.
- Find out why a role container on the sidecar network cannot connect after the host probe succeeds (network attach
  order, published-port versus network-alias probe; related to Bean 0130).
- Tests: image present without opt-in does not spawn a sidecar; opt-out wins; container-side reachability.

## Notes

- Run through the Holon flow on holon-agentic-coder.
