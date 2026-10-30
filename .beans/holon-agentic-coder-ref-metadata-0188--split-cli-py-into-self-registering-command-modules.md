---
# holon-agentic-coder-ref-metadata-0188
title: "Split cli.py into a cli/ package with one self-registering module per subcommand; main becomes a dispatcher"
status: completed
type: task
priority: high
tags:
  - refactor
  - cli
  - concurrency
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0185
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T21:17:00Z
---

## Problem

Spawned by Bean 0177. `sandbox_executor/cli.py` (`993b686`) is 2,962 lines; `main` alone is **1,097 lines, CC 114**,
defining all 21 sub-parsers and their handlers inline. 31 commits touched it (18 since 2026-10-01) and 6 of the flow PRs
#94-#109; `tests/test_cli.py` (2,293 lines) 7. Every new command or flag edits the same function, so any two CLI changes
conflict.

## Scope

1. `cli/__init__.py` keeps `main(argv)` at about 20 lines: build the parser, dispatch to the chosen command.
2. `cli/commands/<command>.py` per subcommand (`intent`, `plan`, `execute`, `flow`, `review`, `calibrate`, `doctor`,
   ledger query, and the rest), each exposing `register(subparsers)` and `run(args) -> int`.
3. Commands are discovered from the `cli/commands` package (`pkgutil.iter_modules`), not from a hand-written list, so
   adding a command adds one file. Choices such as stage names come from the domain enums (`FlowStage`), not literals.
4. Shared option groups (runner, model, credentials, repo dir) in `cli/options.py`.
5. Keep re-exports for names other modules import from `sandbox_executor.cli` until 0189 moves them.
6. Split `tests/test_cli.py` per command module; no test weakened; every function in the new modules within the 0185
   limits (remove the `noqa` on `main`).

## Touch set

`apps/sandbox-executor/src/sandbox_executor/cli.py` (becomes `cli/`), `tests/test_cli.py` (split), the console-script
entry point in `apps/sandbox-executor/pyproject.toml` if its target path changes.

## Dependencies

Blocked by 0185. Parallel-safe with 0187. Sequence with 0155, 0173 and 0175 (they edit `cli.py`).

## Resolution

Completed through the Holon flow on `holon-agentic-coder`:

- Pull Request: [#117](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/117)
- Review: 3/3 unanimous approval with zero findings.
- Calibration: Stage 5 completed and merged into PR head (`1424a26`).
- Merged into `main` at commit `76fe3ea`.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Docker launch and sidecar code (`run_docker_container` 227 lines CC 49, `setup_token_reduction_proxy` 186/25) stay
  where they are here; 0189 moves them.
