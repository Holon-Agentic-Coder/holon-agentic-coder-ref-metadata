---
# holon-agentic-coder-ref-metadata-0379
title: "No logic in __init__.py: package files only expose public names"
status: todo
type: task
priority: high
tags:
  - refactor
  - architecture
  - hygiene
  - holon-agentic-coder
created_at: 2026-11-23T09:30:00Z
updated_at: 2026-11-23T09:30:00Z
---

## Rule (maintainer, 2026-11-23)

An `__init__.py` is used only to expose a package's public functions and variables. It holds no logic: no function or
class definitions, no constants that are not re-exports, no code that runs work at import time.

## Problem

Four of the ten package `__init__.py` files in `apps/sandbox-executor/src/sandbox_executor` (`main` at `84b70c1a`) hold
logic:

| File                              | Lines | What is defined there                                                                                                                                                                                                                                                                                                                                                    |
| :-------------------------------- | ----: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cli/__init__.py`                 |   690 | 14 definitions: `_CurrentStderrHandler`, `configure_cli_logging`, `run_doctor`, `report_budgets_and_envelope`, `_report_budgets`, `_report_gateways`, `resolve_runner_and_model`, `flow_dispatches_agent`, `preflight_gate`, `_configuration_section`, `build_parser`, `resolve_layered_configuration`, `main`, plus constants and mid-file imports under `# noqa: E402` |
| `entrypoint/executor/__init__.py` |   161 | `main()` and four module-level assignments                                                                                                                                                                                                                                                                                                                               |
| `cli/commands/__init__.py`        |    21 | `discover()` (command module discovery)                                                                                                                                                                                                                                                                                                                                  |
| `flow/__init__.py`                |   411 | the lazy-export machinery (`__getattr__`, `__dir__`) and a very long `__all__`; it went over its frozen module budget during the bean 0191 merge                                                                                                                                                                                                                         |

Costs: importing the package runs or defines application logic (slow imports, import cycles hidden behind mid-file
imports); the CLI entry point and `holon doctor` live in a file nobody looks for them in; tests patch names on the
package object; and these files are merge-conflict hotspots because every feature adds a line to them.

The other six (`knowledge`, `launcher`, `ledger`, `flow/stages`, `flow/review`, `flow/github`) only import and
re-export, or are empty.

## Goal

1. Move every definition out of the four files into named modules of the same package, for example
   `cli/logging_setup.py` (`configure_cli_logging`), `cli/doctor.py` (`run_doctor` and its report helpers),
   `cli/runner_resolution.py`, `cli/preflight_gate.py`, `cli/parser.py` (`build_parser`), `cli/main.py` (`main`,
   `resolve_layered_configuration`), `entrypoint/executor/main.py`, `cli/commands/discovery.py`. Move only; no behaviour
   change.
2. Each `__init__.py` then holds a docstring, imports of the public names and `__all__`, nothing else. Console script
   entry points in `pyproject.toml` point at the new modules (`sandbox_executor.cli.main:main`).
3. `flow/__init__.py`: the lazy-export map already lives in `flow/lazy_exports*.py`; reduce the file to the re-export
   surface. Decision for the maintainer: a module-level `__getattr__`/`__dir__` pair that only forwards to that map is
   an exposing mechanism, not logic, and may stay; if "no logic" is meant strictly, replace it with explicit imports
   (which costs import time and risks cycles) or have callers import from the submodules.
4. **Enforce it.** A hygiene test parses every `__init__.py` with `ast` and fails on anything other than a docstring,
   `import`/`from … import`, an `__all__` assignment and (if the maintainer allows it) the forwarding
   `__getattr__`/`__dir__`. No `# noqa: E402` mid-file imports remain in these files.
5. Tests that patch `sandbox_executor.cli.<name>` are updated to patch the defining module.

## Notes

- `cli/__init__.py` (690 lines) is not checked by the module budget at all: `holon-config/hygiene/module_budgets.json`
  lists only the `flow/` package. `flow/__init__.py` is covered and carries a grandfathered override of 562 lines.
- Large, mechanical, and touches the CLI entry points: run it on its own, not beside flows that edit `cli/` or
  `flow/__init__.py`, and likely as a split flow (cli, entrypoint/executor + cli/commands, flow, enforcement test).
- The intent JSON must not mention bean ids or harness paths.
