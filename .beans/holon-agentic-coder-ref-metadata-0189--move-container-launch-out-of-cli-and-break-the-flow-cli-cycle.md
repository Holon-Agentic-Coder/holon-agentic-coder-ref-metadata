---
# holon-agentic-coder-ref-metadata-0189
title: "Move container launch and role dispatch out of the CLI into a launcher module; break the flow-cli import cycle"
status: completed
type: task
priority: high
tags:
  - refactor
  - architecture
  - sandbox
  - holon-agentic-coder
blocked_by:
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-23T02:48:56Z
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

## Audit (2026-11-23)

Blockers `0187` (scrapped, replaced by `0254`/PR #147) and `0188` (PR #117) are closed; `0190` merged (PR #219). Still
valid on `main` (`b22258d`): `cli/__init__.py` is 1,732 lines and four lazy `flow` -> `cli` imports remain
(`flow/context.py:199`, `flow/dispatch.py:34`, `flow/pipeline.py:422`, `flow/review/loop.py:197`). Sequence after `0265`
(`cli/__init__.py` split) and open PR #230 (which touches `flow/context.py`, `flow/pipeline.py`, `flow/review/loop.py`).

## Flow run (2026-11-23)

Intent `todo/intent-0189-launcher-breaks-flow-cli-cycle.json`, flow branch
`I-1795388455-launcher-breaks-flow-cli-cycle`. Plan, execute, review (consensus at iteration 5) and calibrate completed;
PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/241 (open, awaiting human merge). Resumed twice from
checkpoint; ledger rows reconciled with origin/main at the merge.

## Resolution

Delivered via [PR #241](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/241) and merged into `main`
(`0f0089d`):

- **Key Architectural Deliverables**: new `launcher/` package (`role_dispatch`, `containers`, `sidecar`, `sidecar_plan`,
  `coherence`, `mounts`, `env_files`, `container_env`, `proxy_paths`, `proxy_attach`, `messages`, `pi_mounts`,
  `antigravity_mounts`) now owns container launch, role dispatch and proxy/sidecar plumbing; `cli/__init__.py` shrinks
  accordingly and `flow/` imports `launcher` instead of `cli`, so the four lazy `flow` -> `cli` imports are gone.
- **Verification & Tests**: AST import-cycle test (`tests/test_import_cycle.py`) fails on any `sandbox_executor.flow` ->
  `sandbox_executor.cli` edge; launch characterisation tests (`tests/test_container_launch_characterisation.py`) and a
  fake Docker harness (`tests/fake_docker.py`) pin the moved behaviour; existing credential redaction and URL fuzz tests
  stay green.
- **Holon Flow Traversal**: all 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed; review
  reached consensus at iteration 5.
- **Post-merge**: `main` fast-forwarded to the merge commit; `install-holon` rebuilt all images and reinstalled `holon`
  and `holon-coherence`; flow worktree and remote flow branches removed.
