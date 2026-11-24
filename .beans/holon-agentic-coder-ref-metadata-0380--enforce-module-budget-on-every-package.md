---
# holon-agentic-coder-ref-metadata-0380
title: "Enforce the module line budget on every package, including new ones, not just flow/"
status: in-progress
type: task
priority: high
tags:
  - hygiene
  - module-budget
  - architecture
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-23T09:35:00Z
updated_at: 2026-11-24T11:34:00Z
---

## Instruction (maintainer, 2026-11-23)

"Budget should be enforced to all packages, including new packages, not just to `flow`."

This is the maintainer's explicit instruction to change the frozen budget configuration
(`holon-config/hygiene/module_budgets.json`); the flow's intent carries the `module_budget_change` field for this change
only.

## Problem

`scripts/check_module_budgets.py` checks only the directories listed under `packages` in the configuration, and the list
holds one entry: `apps/sandbox-executor/src/sandbox_executor/flow` (added by PR #214 on 2026-11-20, right after the
`flow.py` split). On `main` at `84b70c1a`:

| Scope                                  | Python files | Over 200 lines | Checked                                     |
| :------------------------------------- | -----------: | -------------: | :------------------------------------------ |
| `sandbox_executor/flow/`               |          109 |             21 | yes (200-line default, 22 frozen overrides) |
| rest of `sandbox_executor/`            |          147 |             44 | no                                          |
| `scripts/`                             |           11 |              4 | no                                          |
| tests (`apps/sandbox-executor/tests/`) |          256 |            114 | no                                          |

So `cli/__init__.py` (690 lines), `calibration.py` (1,637), `review_ensemble.py` (1,055), `local_llm.py` (1,049),
`git_flow.py` (1,008), `entrypoint/review_loop.py` (923) and 38 more oversized modules are never measured, and a new
package added anywhere outside `flow/` has no limit at all.

## Goal

1. **Coverage by discovery, not by list.** The check covers every tracked Python source file in the repository (all of
   `apps/*/src/`, `scripts/` and any package added later) without naming packages. The `packages` list is replaced by an
   explicit, short `exclude` list (generated files, vendored code), so a new package is budgeted the moment it exists.
   An excluded path needs a stated reason in the configuration.
2. **Existing oversized modules are frozen, not waved through.** Each module currently over the default gets an override
   equal to its current line count. Overrides only ratchet down: growing past an override fails; a module that has
   shrunk below its override produces a notice to lower it (or the check lowers it in a dedicated mode); an override can
   never be raised or added later without the maintainer's instruction. New modules get the 200-line default with no
   override.
3. **`__init__.py` files are covered like any other module** (and Bean 0379 empties them of logic).
4. **Same rule in `holon-coherence`**: the same script and a configuration of its own, as a follow-up flow there.
5. The check stays in `uv run task lint`, the pre-commit hook and CI; the frozen-configuration rule (byte-for-byte
   comparison with the merge base, changed only on the maintainer's instruction) is unchanged.

## Decisions (defaults; change here if the maintainer decides otherwise)

- **Tests**: not budgeted in this change (114 of 256 test files are over 200 lines; test files are long by nature and
  the review cost is different). A later bean can add a separate, larger limit for tests.
- **Default stays 200 lines.** Whether overrides should exist at all is Bean 0340 (draft); this bean only extends
  coverage and freezes today's sizes.
- **Paydown**: the 48 newly frozen modules are split over time by their own beans (largest first: `calibration.py` is
  Bean 0197; `cli/__init__.py` is Bean 0379; `review_ensemble.py`, `local_llm.py`, `git_flow.py`,
  `entrypoint/review_loop.py` need beans).

## Acceptance criteria

- A new Python package created anywhere in the repository (outside the exclude list) is checked with no configuration
  change; a test creates one with a 201-line module and the check fails.
- Every source module is either within 200 lines or has an override equal to its line count at the time of this change;
  the check passes on the resulting tree.
- Growing any frozen module by one line fails the check; shrinking one produces the ratchet notice.
- The configuration lists exclusions with reasons and no `packages` list; the script's docstring and the developer docs
  describe the new behaviour.
- All tests pass via `uv run pytest`; `uv run task lint` and `uv run task lint-docs` pass.

## Notes

- The intent must set `module_budget_change` (the maintainer's instruction above is the authorisation) and must not
  mention bean ids or harness paths.
- Every open flow that grows a newly frozen module will fail lint once this lands: land it when few PRs are open, and
  tell running flows.
- Related: Bean 0264 / PR #214 (budget introduced for `flow/`), Bean 0340 (draft: strict default, no overrides), Bean
  0379 (no logic in `__init__.py`), Bean 0197 (split `calibration.py`).

## Measured (self-improvement audit 2026-11-24)

Reviewers raised 25 findings in the period 2026-11-21 to 2026-11-24 that a file already over 1,000 lines grew (for
example `executor.py` from 1,580 to 1,852 lines, `test_review_loop.py` from 2,679 to 2,723); 12 percent of all 249
findings, each settled by a resolver pass and a full re-review. A mechanical check before the push (Bean 0408) would
catch them in Stage 3.

> 2026-11-24: launched the `holon-coherence` half (`coherence-module-line-budget-all-packages`, intent
> `todo/intent-0380-coherence-module-line-budget-all-packages.json`) via `antigravity-agent` / `gemini-4-neon`. The
> `holon-agentic-coder` half stays queued behind `0376` and `0265`.
