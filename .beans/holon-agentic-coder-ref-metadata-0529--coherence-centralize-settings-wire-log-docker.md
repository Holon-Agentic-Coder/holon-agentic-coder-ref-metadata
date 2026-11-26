---
# holon-agentic-coder-ref-metadata-0529
title: "Centralize typed CoherenceSettings, bound wire-log queues, and align Docker/wheel packaging"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - config
  - resilience
  - packaging
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Environment configuration is read ad hoc with `os.getenv()` across 12+ modules and frozen at import time in several
modules, wire-log futures/files grow without bounds, CA generation errors are silently swallowed, and Dockerfile asset
resolution and dependency installation diverge from `uv.lock` and wheel packaging.

## Evidence

- Scattered `os.getenv()` across 12+ modules with inconsistent bool/port parsing and import-time freezes in
  `src/holon_coherence/wire_log.py:41`, `src/holon_coherence/mitm_addon.py:87`, and
  `src/holon_coherence/web_token.py:23`.
- `src/holon_coherence/wire_log.py:137-140`: unbounded `_pending_wire_log_futures` queue, plus 2× duplicated disk
  storage (`turn_*.json` + `transactions.jsonl`) with no rotation.
- Silent exception suppression around CA setup: `src/holon_coherence/container/lifecycle.py:419-421`
  (`suppress(Exception)` on `generate_root_ca`) and `src/holon_coherence/ca_generator.py:144-153` (`OSError` on
  `_sync_mitmproxy_ca`).
- Fragile 4-level `__file__` traversal to find `Dockerfile` (`src/holon_coherence/commands/docker_ops.py:56`,
  `src/holon_coherence/container/image.py:22`), breaking under non-editable wheel installs.
- `Dockerfile` uses `pip` (ignoring `uv.lock`), leaves base image digest unpinned, lacks `HEALTHCHECK`, and
  `.dockerignore` is incomplete.

## Proposed Change

1. Introduce a frozen, typed `CoherenceSettings.from_env()` configuration object with uniform bool/int/path parsing and
   eliminate import-time env freezes.
2. Bound `_pending_wire_log_futures` (with backpressure or drop counter), remove duplicate `turn_*.json` /
   `transactions.jsonl` write overhead where redundant, and add size/age rotation.
3. Replace silent CA `suppress(Exception)`/`OSError` catches with explicit logging or propagated startup errors.
4. Resolve container/Dockerfile assets via `importlib.resources` (with editable checkout fallback), align `Dockerfile`
   with `uv.lock`, pin the base digest, add a `HEALTHCHECK`, and complete `.dockerignore`.

## Acceptance Criteria

- All environment variables are parsed through `CoherenceSettings.from_env()` with unit-tested bool/port defaults.
- Wire-log futures queue and disk usage are bounded and rotatable; CA setup failures are logged loudly or surfaced.
- `holon-coherence` can locate Docker/build assets cleanly when installed as a wheel, and `Dockerfile` locks
  dependencies against `uv.lock`.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
