---
# holon-agentic-coder-ref-metadata-0196
title: "Decompose entrypoint executor main into an ExecutionRun with named steps; split the module into a package"
status: todo
type: task
priority: high
tags:
  - refactor
  - complexity
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0195
  - holon-agentic-coder-ref-metadata-0190
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `entrypoint/executor.main` (`993b686`) is **798 lines, CC 178**: the most complex function in
either repository. `parse_sub_intent_list` is CC 35. The module was changed by 23 commits (17 since 2026-10-01) and by
five of the flow PRs #94-#109 (#94 #95 #96 #97 #108).

## Scope

1. `entrypoint/executor/` package: `run.py` (`ExecutionRun` with steps: prepare workspace, load plan, run turns, commit
   steps, salvage, pre-push sync, push, record ledger), `sub_intents.py`, `pre_push.py`, `repair.py`.
2. `main` parses arguments and calls `ExecutionRun(...).run()` (about 20 lines).
3. Split `tests/test_executor.py` to mirror the package.
4. All functions within the 0185 limits; behaviour, exit codes and ledger rows unchanged.

## Touch set

`entrypoint/executor.py` (becomes a package), `tests/test_executor.py` (split), the container entrypoint path in
`apps/sandbox-executor/Dockerfile` / `role_dispatcher.sh` only if the module path changes (keep `python -m` target
stable to avoid it).

## Dependencies

Blocked by 0195 (git adapter) and 0190 (entrypoint stops importing the engine). Sequence with 0161 and 0183.

## Notes

- Run through the Holon flow on holon-agentic-coder, alone on `executor.py`.
