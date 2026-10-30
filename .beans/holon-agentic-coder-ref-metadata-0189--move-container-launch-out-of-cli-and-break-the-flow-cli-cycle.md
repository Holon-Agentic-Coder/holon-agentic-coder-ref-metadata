---
# holon-agentic-coder-ref-metadata-0189
title: "Move container launch and role dispatch out of the CLI into a launcher module; break the flow-cli import cycle"
status: todo
type: task
priority: high
tags:
  - refactor
  - architecture
  - sandbox
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0187
  - holon-agentic-coder-ref-metadata-0188
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `cli` imports `flow` at top level while `flow` lazily imports `cli` four times
(`detect_holon_coherence`, `dispatch_role_agent`, `get_host_proxy_envs`, `teardown_token_reduction_proxy`): an import
cycle hidden by function-local imports. The engine depends on the presentation layer, and container plumbing lives in
the CLI: `run_docker_container` (227 lines, CC 49) and `setup_token_reduction_proxy` (186 lines, CC 25).

## Scope

1. New `launcher/` package: `role_dispatch.py` (`dispatch_role_agent`), `containers.py` (`run_docker_container` as a
   `ContainerLaunch` with named steps: env file, mounts, credentials, argv), `sidecar.py` (proxy setup/teardown, host
   proxy envs, coherence detection).
2. `flow` and `cli` both import `launcher`; `flow` no longer imports `cli` anywhere. Add a pytest that walks `ast`
   imports and fails on any `sandbox_executor.flow` -> `sandbox_executor.cli` edge.
3. Decompose the moved functions to the 0185 limits; credential redaction on argv and env stays byte-for-byte identical
   (existing redaction and URL fuzz tests green).

## Touch set

`cli/` (the moved functions), `flow/` (four import sites), new `launcher/`, tests for the moved code.

## Dependencies

Blocked by 0187 and 0188. Should precede 0183 (this module is what 0183 turns into the thin host launcher) and 0200.
Sequence with 0155 and 0157, which change the same functions.

## Notes

- Run through the Holon flow on holon-agentic-coder.
