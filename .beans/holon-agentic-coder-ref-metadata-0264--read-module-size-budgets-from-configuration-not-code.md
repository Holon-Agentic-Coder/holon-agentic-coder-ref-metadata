---
# holon-agentic-coder-ref-metadata-0264
title:
  "Module size budgets force a split: forbid raising a budget, default ceiling for new modules, no shared edit per flow"
status: in-progress
type: task
priority: high
tags:
  - flow
  - lint
  - configuration
  - admission
  - holon-agentic-coder
created_at: 2026-11-09T10:00:00Z
updated_at: 2026-11-20T17:20:00+11:00
---

## Intent of the budget (maintainer, 2026-11-20)

A module budget is a ceiling that forces a big module to be **divided**. It is not a number to raise whenever a file
gets bigger. When a change would push a module past its budget, the module is split; the budget is never raised to fit.

**The budget is strictly off-limits.** No agent or flow touches the budget configuration in any way (raise, lower, add,
delete) unless the maintainer has given an explicit instruction for that change.

## Problem

The per-module size ratchet from Bean 0254 (PR #147) stops a module from growing past its budget, but nothing stops a
pull request from raising the budget, so flows take the cheapest path to a green lint and edit the JSON:

- `apps/sandbox-executor/flow_module_budgets.json` has changed in 34 commits. It went from 28 modules and 6,937 budgeted
  lines to 70 modules and 12,091. Some of that is splitting, as intended, but the number of modules over 200 lines still
  rose from 18 to 22, and the largest is 952.
- Its `description` string has become a running log of raises ("raised by 1, 1 and 3 lines for …"), which every flow
  appends to.
- Every module needs an entry, so a split must also add rows to the file.

Because almost every flow on `flow/` code edits this one file, Stage 3 admission sees it in every touch set and refuses
or serialises flows that otherwise share nothing (2026-11-20: `review-keeps-worktree-on-branch` waited on PR #210 only
for this file), and the shared `description` line makes the merges conflict textually (PRs #206, #208, #209).

## Goal

Through the Holon flow on `holon-agentic-coder`:

1. **The budget configuration is frozen: nothing may change it without the maintainer's explicit instruction.** No
   agent, flow stage, resolver or reviewer may raise, lower, add, delete or reformat any budget, override or the default
   ceiling on its own judgement, not even to lower a limit after a split. Any difference between the budget
   configuration and the merge base's copy (`git merge-base HEAD origin/main`) fails the check, unless the change is
   explicitly authorised:
   - **In the flow:** the intent carries a `module_budget_change` field quoting the maintainer's instruction. Only then
     does the flow set `HOLON_ALLOW_MODULE_BUDGET_CHANGE=1` for the check. Without the field, Stage 3 and the Stage 4
     resolver refuse to commit any change to the budget configuration, and the planner must not list it in the touch
     set.
   - **In CI:** the check fails on any change to the budget configuration unless the pull request carries the
     `module-budget-change` label, which only the maintainer applies (agents never add or remove it).
   - The one authorised change is this flow itself, which creates the new configuration from the existing budgets at
     their current values (maintainer instruction, 2026-11-20). Every value is copied unchanged.
2. **New modules need no entry.** A default ceiling of 200 lines (the guideline in the repository's agent rules) applies
   to every module without an override, so a split adds no entries. An override that names a missing module, or sits at
   or below the default, is reported as a `::warning::` for the maintainer, never as a failure, because fixing it would
   mean touching the configuration.
3. **Over budget means split.** The check's failure message says to split the module and that the budget may not be
   changed. The planner, executor and Stage 4 resolver prompts (`holon-config/prompts/`) say the same: when a planned
   change would push a module past its limit, plan and perform the extraction into new modules as part of the change.
   Reviewers treat any change to the budget configuration without the authorisation above as a Critical finding.
4. **Settings in configuration, no history prose.** Move the settings to `holon-config/hygiene/module_budgets.json`
   (`default_max_lines`, `packages`, `overrides` keyed by repository-relative path, sorted, one per line, plain
   integers). No free-text history: reasons for changes belong in commit messages and the ledgers. Rename the check to
   `scripts/check_module_budgets.py`, make it generic over the configured packages with no hardcoded path, package or
   line count (optional `--config` and `--base` for tests), and delete `apps/sandbox-executor/flow_module_budgets.json`
   and `scripts/check_flow_module_budgets.py` with every reference to them (lint task, CI, docs). No fallback.
5. **Tests and docs.** Move the test to `tests/test_module_budgets.py` and cover: the default ceiling for a module with
   no entry; an override; a new module under 200 lines passing with no entry; any change to the configuration against a
   base copy failing (a raise, a lower, an added or deleted override, a changed default); the same change passing when
   explicitly authorised; an override naming a missing module and a redundant override producing warnings, not failures;
   multiple packages; a custom `--config`. Hermetic flow tests: without the intent field, Stage 3 and the resolver
   refuse to commit a budget change and the planner leaves the configuration out of the touch set. Update
   `docs/architecture.md` to state the rule (split; the budget is frozen and changes only on the maintainer's explicit
   instruction) and where the settings live.
6. **Constraints:** `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies; exactly
   the three ledgers.

## Expected effect

No flow touches the budget configuration unless the maintainer has asked for that change, so it drops out of touch sets
and stops causing Stage 3 overlap waits and Stage 4 merge conflicts.

## Sequencing

- Start after the in-flight flows that edit `flow_module_budgets.json` (Beans 0336 and 0338) have merged; this flow
  deletes that file.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.

## History

- 2026-11-09: first written as "read module size budgets from configuration", which let agents raise limits with a
  warning. Rewritten 2026-11-20 after the maintainer restated the intent: budgets force a split and are never raised.
  Tightened the same day: the budget configuration is frozen, and any change at all needs the maintainer's explicit
  instruction.
