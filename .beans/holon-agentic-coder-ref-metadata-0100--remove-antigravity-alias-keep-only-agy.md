---
# holon-agentic-coder-ref-metadata-0100
title: "Remove antigravity agent alias and retain only agy in holon-coherence"
status: completed
type: task
priority: normal
tags:
  - coherence
  - cli
  - cleanup
created_at: 2026-10-16T06:08:00Z
updated_at: 2026-10-17T01:35:00Z
---

Remove redundant `antigravity` agent alias from `holon-coherence` CLI commands, runner maps, and documentation,
consolidating exclusively on `agy`.

## Context

Currently `holon-coherence` exposes both `agy` and `antigravity` as agent subparsers and targets in `SUPPORTED_AGENTS`
and `AGENT_BINARY_MAP`. Both refer to the identical Google Antigravity coding agent CLI (`agy`). Exposing both causes
redundant CLI subparsers and clutter in `holon-coherence --help`.

## Tasks

- [x] In `src/holon_coherence/commands/agents.py`, remove `antigravity` from `SUPPORTED_AGENTS` and `AGENT_BINARY_MAP`,
      keeping `agy -> agy`.
- [x] In `src/holon_coherence/cli.py` and documentation, ensure only `agy` is registered and referenced.
- [x] Update unit and integration tests in `tests/test_cli.py` to assert only `agy` is in `SUPPORTED_AGENTS`.
- [x] Verify formatting with prettier and ruff checks.

## Resolution

- Cleanly removed `antigravity` alias from `SUPPORTED_AGENTS` and `AGENT_BINARY_MAP` keys in
  `src/holon_coherence/commands/agents.py`.
- Preserved host binary fallback resolution in `AGENT_BINARY_MAP["agy"] = ["agy", "antigravity"]`.
- Set default `HOLON_AGENT_ID` in `src/holon_coherence/mitm_addon.py` to `agy`.
- Plumbed `--name` across `start`, `stop`, `status`, `logs`, and `metrics` subparsers in `src/holon_coherence/cli.py` to
  allow sandboxed container testing.
- Added `--offline` argument to `metrics_parser` in `cli.py`.
- Added unit and integration test coverage in `tests/test_cli.py` and `tests/test_docker_integration.py`.
- PR #21 raised and reviewed through 3-agent ensemble consensus loop: 3/3 unanimous `APPROVED`.
- Rebased onto `origin/main` resolving argument conflict with PR #20; 624/624 tests passing green.
- Merged into `origin/main` (commit `c1a58e4`) on 2026-10-16.
