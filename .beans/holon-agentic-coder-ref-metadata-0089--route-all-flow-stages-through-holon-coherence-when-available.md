---
# holon-agentic-coder-ref-metadata-0089
title: "Route all Holon flow stages through holon-coherence token optimization proxy when available"
status: completed
type: feature
priority: normal
tags:
  - holon-flow
  - holon-coherence
  - token-reduction
  - proxy
  - pipeline
created_at: 2026-10-13T18:32:00Z
updated_at: 2026-10-15T09:10:00Z
---

## Summary

Ensure every stage of the Holon flow (`intent`, `plan`, `execute`, `pr-review-loop`, `calibrate`) automatically routes
sandbox and agent network egress through `holon-coherence` (the token reduction proxy) whenever the proxy or its Docker
image is available, rather than requiring manual opt-in flags (`--token-reduce`) on every command.

## Context

`holon-coherence` provides substantial token reduction, prompt cache optimization, and request deduplication via its
`mitmproxy` sidecar. Currently:

1. `holon intent`, `holon plan`, and `holon execute` require manual `--token-reduce` or the `HOLON_TOKEN_REDUCE=1`
   environment variable to activate the proxy.
2. The automated pipeline runner (`sandbox_executor/flow.py`) accepts `token_reduce: bool = False`, leaving token
   reduction disabled by default unless explicitly configured.
3. Subagent review ensembles in the `pr-review-loop` run on the host or inside spawned subagent contexts without
   automated proxy attachment unless an external proxy is manually running on port 8080.
4. If `holon-coherence` (or its Docker image `holon-coherence:latest` /
   `ghcr.io/holon-agentic-coder/holon-coherence:latest`) is present or can be started, the harness should
   opportunistically auto-attach or spawn the proxy sidecar for all stages, while safely falling back to direct egress
   only if the proxy fails readiness probes or is completely unavailable.

## Acceptance Criteria

1. **Auto-Detection & Opportunistic Proxy Wiring**:
   - In `apps/sandbox-executor/src/sandbox_executor/cli.py` and `flow.py`, add auto-discovery for `holon-coherence`:
     - If `HOLON_TOKEN_REDUCE` is explicitly set to `0`/`false`, respect the opt-out.
     - Otherwise, check if a coherence proxy is already listening on `127.0.0.1:8080` (or `HOLON_PROXY_PORT`), or if the
       `holon-coherence:latest` / `ghcr.io/...` Docker image / `holon-coherence` binary is available.
     - If available, automatically enable `token_reduce=True` across all flow stages: Intent, Plan, Execute, Review, and
       Calibration.
2. **Review Loop Egress Coverage**:
   - Ensure the subagents and review runners spawned during `pr-review-loop` (including Reviewer 1, 2, 3 and the
     resolver) inherit the proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`,
     `SSL_CERT_FILE`) and trust store whenever the coherence proxy is active.
3. **Graceful Fallback & Diagnostics**:
   - If the proxy cannot be contacted or fails the TCP readiness probe within the timeout window, emit a clear
     diagnostic log and fall back to direct egress without crashing the flow.
4. **Testing & Verification**:
   - Add unit tests verifying auto-detection behavior, explicit opt-out precedence, fallback on port unreachability, and
     proper environment propagation to sub-processes.
   - Run Prettier and test suites cleanly.

## Target Repositories

- `holon-agentic-coder`: `apps/sandbox-executor/src/sandbox_executor/cli.py`, `flow.py`, `executor.py`
- Harness: `.agents/skills/pr_review_loop/`, `.agents/skills/pr_reviewer/`

## Resolution

- Implemented 5-tier proxy auto-detection hierarchy in `detect_holon_coherence()`, honoring explicit opt-out precedence
  (`HOLON_TOKEN_REDUCE=0/false`).
- Implemented `get_host_proxy_envs()` supplying host loopback URLs and host-valid Root CA paths for host-side stages
  (`execute`, `review`).
- Configured opportunistic external proxy attachment in `_attach_external_proxy()` with host-reachable probes on
  `127.0.0.1`.
- Added deterministic sidecar and network teardown in `run_flow_pipeline()` `try...finally` block.
- Added contract tests in `test_flow.py` and hermetic test suite updates in `test_token_reduction.py` and `test_cli.py`.
- Successfully validated in Holon flow lifecycle stages 1-5; PR #76 achieved 3/3 unanimous ensemble consensus approval
  and 10/10 green CI checks; pre-merge calibrated on `/calibrated` branch ($\Delta EV$ +4.38); merged to `main` at
  commit `eec806e4edb160dfb45b0f02cd90b795a074f446`.
