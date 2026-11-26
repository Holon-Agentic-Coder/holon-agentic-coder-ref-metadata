---
# holon-agentic-coder-ref-metadata-0535
title: "Make RunnerSpec single-source runner registration and add GitForge Protocol + stage registry"
status: todo
type: task
priority: normal
tags:
  - holon-agentic-coder
  - extensibility
  - architecture
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Adding a new coding-agent runner still requires coordinated edits across ~8 files spanning Python, shell, and Docker
configs. Meanwhile, GitHub CLI (`gh`) calls are hardcoded with no forge `Protocol`, `flow/pipeline.py` dispatches stages
via hardcoded `if/elif`, only 2 `Protocol` classes exist across 341 modules, and `subprocess` is imported directly in 50
modules.

## Evidence

- Adding a runner spans `agent_runner.py`, `agent_defaults.py`, `launcher/mounts.py`, `entrypoint/role_dispatcher.sh`,
  `Dockerfile`, `docker-bake.hcl`, `env_registry.py`, and docs despite `runners/spec.py` (`RunnerSpec`).
- `flow/pipeline.py:176-199`: hardcoded `if/elif` stage dispatch.
- Only 2 `Protocol` definitions across 341 source files; no `GitForge` `Protocol` decoupling PR/CI operations from `gh`
  JSON; `subprocess` imported directly in 50 modules.

## Proposed Change

1. Make `RunnerSpec` (`runners/spec.py`) the single source of truth driving `agent_defaults.py`, `launcher/mounts.py`,
   and generated/manifested role-dispatcher runner metadata.
2. Define a `GitForge` `Protocol` implemented by `GitHubAdapter` so stage code depends on the protocol rather than `gh`
   subprocess internals.
3. Replace the `if/elif` stage dispatch in `flow/pipeline.py:176-199` with a declarative stage registry mapping stage
   enum/keys to handlers.

## Acceptance Criteria

- Runner mounts, defaults, and model-discovery hooks read from `RunnerSpec` without duplicating per-runner tables in
  `agent_defaults.py`.
- Pipeline stage dispatch uses a registry table and PR/CI consumers type against `GitForge`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Related: Bean `0270` (dynamic model discovery).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
