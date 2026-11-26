---
# holon-agentic-coder-ref-metadata-0381
title: "Resuming with a bare holon flow leaves token reduction on: every reviewer fails with cache_control.ttl 400"
status: todo
type: bug
priority: high
tags:
  - flow
  - token-reduction
  - stage-4
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

Resuming a flow by calling `holon flow … --checkpoint …` directly (not through the harness wrapper `run_holon_flow.py`)
enables the token-reduce sidecar, and every Stage 4 reviewer then fails with `API Error: 400 system.2.cache_control.ttl`
from the holon-coherence proxy. Seen twice on 2026-11-23: PR #250 (iteration 6, all three reviewers) and PR #251.
Resuming through the wrapper, which sets `HOLON_TOKEN_REDUCE=0`, worked both times.

Two defects:

1. The proxy rewrites a request into one the API rejects (`system.2.cache_control.ttl`): a holon-coherence bug in how
   cache-control blocks are added or ordered.
2. Whether token reduction is on depends on how the flow was launched. PR #248 (Bean 0157) was meant to make the sidecar
   opt-in only; a bare `holon flow` resume still turned it on.

## Goal

- The proxy never emits a `cache_control` block the API rejects; a regression test replays the failing request shape.
- Token reduction is off unless explicitly opted into, identically for a fresh run, a `--checkpoint` resume and the
  wrapper. The checkpoint records the choice and a resume keeps it.
- When the proxy returns a 4xx for a rewritten request, the role retries once without the proxy and reports the proxy
  fault instead of failing the stage.

## Progress

- 2026-11-24: HAC stale plan `flow-token-reduce-opt-in-resume` deleted after PR #263 merged; restart HAC half from
  current `main` once `0376` clears (coherence half already merged in PR #44).

- 2026-11-23: Launched `holon-coherence` flow (`todo/intent-0381-coherence-cache-control-ttl.json`, slug
  `fix-cache-control-ttl-order`, subagent `85c68b2a-9084-4a33-8421-26df8066a765`) and `holon-agentic-coder` flow
  (`todo/intent-0381-hac-token-reduce-opt-in.json`, slug `token-reduce-opt-in-resume`, subagent
  `be888633-7438-45fc-939d-8780d5cfa53a`) via `antigravity-agent` / `gemini-4-argon`.
- 2026-11-24: The `holon-coherence` half (`fix-cache-control-ttl-order`) was delivered via
  [PR #44](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/44) and merged into `main` (`e793d55`; 3/3
  consensus approved, 7/7 CI green, Stage 5 calibrated EV predicted `8.44` / actual `9.03` / delta `+0.59`),
  `holon-coherence` image & CLI were rebuilt from `main`, superseded PR #43 was closed, and
  `flow-fix-cache-control-ttl-order` worktree/branches were pruned; remaining work is the `holon-agentic-coder` half
  (`token-reduce-opt-in-resume`).

- 2026-11-24 (clean-up): set back to `todo` because the `holon-coherence` half is delivered (PR #44) and the
  `holon-agentic-coder` half has no running flow, no flow worktree and no open pull request; it is queued behind `0376`.
