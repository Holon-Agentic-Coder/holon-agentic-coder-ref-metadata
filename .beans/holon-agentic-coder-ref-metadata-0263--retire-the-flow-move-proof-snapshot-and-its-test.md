---
# holon-agentic-coder-ref-metadata-0263
title: "Retire the `flow.py` move-proof snapshot and its test: it now blocks every change to a moved function"
status: todo
type: task
priority: normal
tags:
  - flow
  - tests
  - refactor
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-09T09:30:00Z
updated_at: 2026-11-09T09:30:00Z
---

## Problem

Bean 0254 (PR #147) split `flow.py` into the `flow/` package and proved it was a pure move with
`tests/flow/test_move_proof.py`. The test compares an `ast.dump` SHA-256 of every definition in the package with a
committed snapshot of the original file, `tests/flow/fixtures/flow_py_definitions.json` (source blob `aa8d5f1…`, 180
definitions: functions, classes, methods and `<const>:NAME` module constants, each with its hash).

That proof was complete when PR #147 merged. Since then it has only added friction:

- **Every PR that edits a moved function must edit this one JSON file.** The test fails until the hash is refreshed and
  an `amended_definitions` entry is added. This has happened on PR #148 (`_dispatch_review_resolver`,
  `_invoke_resolver_pass`), PR #151 (`_run_review_loop_iterations`) and PR #152. The flow agents for beans 0258, 0256
  and 0262 each recorded it as an "unplanned constraint" in their execution notes.
- **It recreates the collision hotspot Bean 0254 was meant to remove.** Concurrent flows that touch different `flow/`
  modules still all edit the same JSON file, so they conflict and force sync and re-review rounds.
- **A refresh is not reviewable.** Hashes cannot be checked by eye, so a mistaken refresh gives no useful signal.
- **It guards nothing that matters now.** The code is allowed to change; the structural checks that still catch real
  regressions are the patch-target guard and the module size budgets.

## References to the snapshot

- `apps/sandbox-executor/tests/flow/fixtures/flow_py_definitions.json` (the snapshot)
- `apps/sandbox-executor/tests/flow/move_proof.py` (digest helpers and `load_snapshot`)
- `apps/sandbox-executor/tests/flow/test_move_proof.py` (the proof)
- `apps/sandbox-executor/tests/flow/test_package_exports.py` also imports `load_snapshot` and `package_definitions` from
  `move_proof.py`, so the re-export test depends on the snapshot too.
- `docs/architecture.md` (around line 458) describes the proof.

## Goal

1. **Delete** the snapshot fixture, `move_proof.py` and `test_move_proof.py`, together with the `fixtures/` directory if
   it becomes empty.
2. **Rework `test_package_exports.py`** so its expectations come from the package itself rather than the snapshot. For
   example, for each submodule, parse it and require every public top-level function and class it defines to be
   re-exported by `flow/__init__.py` (and listed in `__all__`), and require every re-exported name to resolve to the
   object defined in its owning module. The test must still fail when a definition is added to a module without being
   re-exported.
3. **Keep** `test_patch_targets.py` and `test_module_budgets.py` unchanged.
4. **Update `docs/architecture.md`** to drop the move-proof paragraph and describe the remaining guards (patch targets,
   re-exports, module budgets).
5. **Search the whole repository** for remaining references (code, docs, CI configuration) and remove them. Do not leave
   a skipped test or a stub behind.
6. **Tests**: the full suite passes via `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass, and no
   `flow/` module budget is raised.

## Sequencing

- **Do not start yet.** PR #152 (Bean 0262) is in review and also edits the snapshot, so run this after it merges to
  avoid a conflict on the same file.
- It touches only `tests/flow/` and `docs/architecture.md`, so it can run alongside beans that change `src/` modules,
  once #152 has landed.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.
