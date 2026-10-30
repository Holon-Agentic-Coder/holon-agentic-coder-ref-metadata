---
# holon-agentic-coder-ref-metadata-0208
title: "holon-coherence: a ProxyLifecycle class owns start-up, readiness and teardown of the proxy"
status: todo
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0203
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. Measured on `68fdf67`: `commands/start.handle_start` **202 lines, CC 33**, `ensure_proxy_running`
171 lines, CC 30; `commands/agents.extract_runner_flags` CC 24 and `build_agent_env` CC 23. `start.py` was touched by 3
of the coherence PRs #24-#31 (#26 readiness polling, #27 mitmweb inspector, #29).

## Scope

1. `ProxyLifecycle` (docker or host-local mode chosen once) with `ensure_ca`, `start`, `wait_until_ready` (monotonic
   deadline), `stop`; `handle_start` becomes argument parsing plus one call.
2. Runner flag and env construction as a small `AgentLaunch` object in `commands/agents.py`.
3. All functions within the 0186 limits; readiness and inspector behaviour unchanged.

## Touch set

`commands/start.py`, `commands/agents.py`, `host_local.py` (call sites only), mirrored tests.

## Dependencies

Blocked by 0203. Parallel-safe with 0207.

## Notes

- Run through the Holon flow on holon-coherence.
