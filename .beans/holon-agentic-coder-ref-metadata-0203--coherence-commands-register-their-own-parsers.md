---
# holon-agentic-coder-ref-metadata-0203
title: "holon-coherence: each command module registers its own parser; drop the sys.modules dispatch locator"
status: todo
type: task
priority: high
tags:
  - refactor
  - cli
  - concurrency
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0186
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. holon-coherence (`68fdf67`) already has one handler module per command under `commands/`, but
every parser is still defined inline in `cli.main` (**349 lines, CC 31**). `cli.py` is the most-churned source file (18
commits) and `tests/test_cli.py` (3,728 lines) the most-churned test (16). Handlers find collaborators through
`commands/_dispatch.get_cli()`, a `sys.modules` lookup used 15 times in 8 command modules so that tests can patch
`holon_coherence.cli.<name>` (286 such patch targets in `test_cli.py`). That service locator couples every command and
test to the one CLI module.

## Scope

1. Each `commands/<command>.py` exposes `register(subparsers)` and `handle(args)`; `cli.main` discovers the modules and
   dispatches (about 20 lines).
2. Commands receive their collaborators explicitly (constructor or function arguments with defaults), and tests patch or
   inject at the defining module; remove `_dispatch.py`.
3. Split `tests/test_cli.py` into `tests/commands/test_<command>.py`; test count unchanged or higher.
4. All touched functions within the 0186 limits.

## Touch set

`src/holon_coherence/cli.py`, `src/holon_coherence/commands/*.py`, `tests/test_cli.py` (split).

## Dependencies

Blocked by 0186. Blocks 0207 and 0208 (same command modules). Parallel-safe with 0204.

## Notes

- Run through the Holon flow on holon-coherence.
