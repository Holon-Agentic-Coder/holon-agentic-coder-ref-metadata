---
# holon-agentic-coder-ref-metadata-0264
title: "Read module size budgets from configuration instead of hardcoding paths and numbers in the check"
status: todo
type: task
priority: normal
tags:
  - flow
  - lint
  - configuration
  - tests
  - holon-agentic-coder
created_at: 2026-11-09T10:00:00Z
updated_at: 2026-11-09T10:00:00Z
---

## Problem

The per-module size ratchet from Bean 0254 (PR #147) has its settings baked into code and into a one-off data file:

- `scripts/check_flow_module_budgets.py` hardcodes both paths (`DEFAULT_PACKAGE_DIR` is
  `apps/sandbox-executor/src/sandbox_executor/flow` and `DEFAULT_BUDGETS` is
  `apps/sandbox-executor/flow_module_budgets.json`), the JSON shape (`["budgets"]`), and its rules (a module with no
  entry is a violation, an entry with no module is a violation).
- The script and its message strings are named for the `flow` package, so applying the same ratchet to another package
  (`cli/commands/`, `proxy/`, `executor/`, as `AGENTS.md` rule 15 suggests) means copying the script.
- The 200-line guideline from `AGENTS.md` rule 15 appears nowhere in the check. Every module needs a budget entry at its
  creation size, so the file holds 28 numbers, 18 of them above 200 lines (the largest, `review/loop.py`, is 962).
- `tests/flow/test_module_budgets.py` builds temporary packages against the same hardcoded layout.

Settings that people tune belong in configuration that tools read, not in script constants or a bespoke JSON file that
sits beside the source.

## Goal

1. **Define the settings as configuration** in the repository's existing `pyproject.toml` (read with the standard
   library `tomllib`, so no new dependency), for example:

   ```toml
   [tool.holon.module-budgets]
   default-max-lines = 200
   packages = ["apps/sandbox-executor/src/sandbox_executor/flow"]

   [tool.holon.module-budgets.overrides]
   "apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py" = 962
   ```

   The exact table and key names may differ, but the shape must give three things: which packages are checked, one
   default ceiling, and per-module overrides keyed by repository-relative path, recorded at the modules' current sizes.

2. **Make the check generic and free of hardcoded values.** Rename it to `scripts/check_module_budgets.py`. It reads the
   configuration (with an optional `--config` path used by tests), checks every `.py` file under each configured
   package, and reports one message per violation:
   - a module above its override, or above the default ceiling when it has no override;
   - an override naming a missing module (remove it);
   - an override above the default ceiling is allowed (that is what an override is for), but an override at or below the
     default ceiling is redundant and reported.

   No path, package name or line count appears in the script.

3. **Agents can change the configuration, with changes made visible.** The settings are ordinary configuration that flow
   agents and people edit in a PR like any other file: nothing blocks lowering, raising, adding or removing an override,
   or changing the default ceiling. What the check adds is visibility, not a veto: it compares the configuration with
   the merge base's copy (`git show <base>:pyproject.toml`, skipped quietly when there is no base) and prints a
   `::warning::` line for every effective limit that went up, naming the module, the old and new limit and the number of
   lines it now allows. Each override carries a short `reason` (a table with `max-lines` and `reason`, or an adjacent
   comment convention the check can read), and the check reports an override with no reason as a violation so a raise is
   never silent. Reviewers see the warnings in CI output and the reason in the diff, and decide.

4. **Remove the old pieces.** Delete `apps/sandbox-executor/flow_module_budgets.json` and
   `scripts/check_flow_module_budgets.py`, update the `lint` task and any CI hygiene step that calls the script, and
   delete every reference to the old names (code, docs, CI configuration). No fallback to the JSON file.

5. **Tests and docs.** Rework `tests/flow/test_module_budgets.py` (move it to `tests/test_module_budgets.py`, since the
   check is no longer flow-specific) to cover: the default ceiling, an override, a missing module, a redundant override,
   an override without a reason, multiple packages, a raised limit producing a warning (and still passing) against a
   base copy, a lowered limit producing none, and reading a custom `--config`. Update `docs/architecture.md` and the
   contributing notes to describe where the settings live and how to lower a budget.

6. **Constraints**: `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies.

## Sequencing

- **Do not start yet.** PR #152 (Bean 0262) lowers entries in `flow_module_budgets.json`, and Bean 0263 edits
  `tests/flow/` and `docs/architecture.md`. Run this after both have merged, to avoid conflicts on the same files.
- It touches `pyproject.toml`, `scripts/`, `tests/`, the CI hygiene configuration and `docs/`, and no source modules, so
  it can run alongside beans that change `src/`.

## Trade-offs to note

- The overrides still live in one shared file, so two PRs that change different modules can touch adjacent lines of the
  same table. Configuration was chosen deliberately over per-module header comments. Sorted keys and one entry per line
  keep any such conflict trivial, and the default ceiling means most new modules need no entry at all.
- Letting agents raise limits means the ratchet no longer forbids growth: it records it. Earlier flow intents told
  agents never to raise a budget; that instruction was a choice made for those runs, not part of this design, and
  intents written after this bean lands should not repeat it.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.
