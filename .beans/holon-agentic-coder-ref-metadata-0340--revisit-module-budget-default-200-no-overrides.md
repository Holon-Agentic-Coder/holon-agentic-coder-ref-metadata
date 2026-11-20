---
# holon-agentic-coder-ref-metadata-0340
title: "Revisit the module budget: implications of a strict 200-line default with no overrides"
status: draft
type: task
priority: high
tags:
  - flow
  - lint
  - configuration
  - refactoring
  - holon-agentic-coder
created_at: 2026-11-20T19:30:00+11:00
updated_at: 2026-11-20T19:30:00+11:00
---

## Context

Bean 0264 (flow `freeze-module-budgets-split`) moves the module budgets to `holon-config/hygiene/module_budgets.json`
with a 200-line default and freezes them: every existing value becomes an override, copied unchanged, and nothing
changes without the maintainer's explicit instruction. The maintainer wants to revisit that end state: what it would
take, and what it would cost, to keep only the 200-line default and get rid of the overrides.

This bean is an analysis and decision record first. Removing or changing any override is a budget change, so each step
that comes out of it needs the maintainer's explicit instruction (Bean 0264's `module_budget_change` authorisation).

## Facts (measured 2026-11-20 on `main` `a450005`)

- **Every override sits exactly at its module's current size.** None has headroom, so from Bean 0264 on, adding one line
  to any of these 22 modules already forces a split.
- **Covered today: only `sandbox_executor/flow/`**, 71 modules, 22 of them over 200 lines (3,331 lines above the
  ceiling). Bringing all 22 under 200 needs at least 30 new modules (each file split into ⌈lines / 200⌉ parts):

| Module (under `flow/`)    | Lines | Parts at ≤ 200 |
| ------------------------- | ----- | -------------- |
| `review/loop.py`          | 952   | 5              |
| `__init__.py`             | 562   | 3              |
| `github/pr.py`            | 515   | 3              |
| `pipeline.py`             | 431   | 3              |
| `stages/execute.py`       | 431   | 3              |
| `git_refs.py`             | 407   | 3              |
| `stages/calibrate.py`     | 349   | 2              |
| `github/ci_final_head.py` | 344   | 2              |
| `github/merge.py`         | 343   | 2              |
| `stages/children.py`      | 330   | 2              |
| `review/resolver.py`      | 319   | 2              |
| `review/records.py`       | 316   | 2              |
| `stages/review.py`        | 305   | 2              |
| `calibrate_rerun.py`      | 287   | 2              |
| `context.py`              | 280   | 2              |
| `in_flight.py`            | 233   | 2              |
| `checkpoint.py`           | 228   | 2              |
| `partial_salvage.py`      | 226   | 2              |
| `ledger_reconcile.py`     | 224   | 2              |
| `stages/intent.py`        | 220   | 2              |
| `github/review_post.py`   | 216   | 2              |
| `stages/plan.py`          | 213   | 2              |

- **Not covered: the rest of `sandbox_executor`**, 101 more modules, of which 39 are over 200 lines and unbudgeted. The
  largest are `cli/__init__.py` (1,755), `calibration.py` (1,638), `entrypoint/executor.py` (1,584),
  `token_reduction/mitm_addon.py` (1,358), `review_ensemble.py` (1,055), `local_llm.py` (1,049), `ledger.py` (1,035) and
  `git_flow.py` (1,008). Extending the check to the whole package with no overrides would fail on 61 modules.

## Questions to answer

1. **One-shot or incremental?** Dropping all overrides at once fails lint on 22 modules, so it needs one very large
   refactor whose touch set overlaps nearly every other flow (it would block or conflict with all concurrent work). The
   alternative is one split per module (or per cluster), each removing its own override with explicit authorisation, run
   sequentially and ordered by size or churn.
2. **Is 200 the right ceiling for every kind of module?** `flow/__init__.py` (562) is mostly re-exports;
   `review/loop.py` (952) is one state machine. Decide whether package `__init__` files, re-export lists or generated
   code are measured differently or excluded.
3. **What is counted?** Physical lines include docstrings, comments and blank lines, so a strict ceiling rewards
   stripping documentation (compare Bean 0153). Consider counting logical lines (statements) or excluding docstrings and
   comments, and decide before any split work.
4. **Which packages are in scope?** Only `flow/` today. Decide whether and when `cli/`, `entrypoint/`,
   `token_reduction/` and the top-level modules join, and whether they start frozen at current size (as `flow/` does) or
   must be split first.
5. **Cost to everyday work.** With zero headroom, small fixes in the 22 large modules now carry a split. Estimate the
   effect on plan size, EV and review load; consider whether the planner should schedule pending splits explicitly
   rather than fold them into unrelated fixes.
6. **Concurrency.** Each split moves code and touches every importer and its tests, so split flows overlap each other
   and most feature flows at Stage 3. Decide an order and whether splits run as a dedicated, serial lane.
7. **Tests.** Test modules are not budgeted. Decide whether they should be.

## Deliverable

A short decision written into this bean (maintainer-approved): the ceiling, what is counted, the packages in scope, the
order of splits, and whether overrides go away entirely or remain as a frozen exception list. Then one follow-up bean
per split (or cluster) carrying the explicit authorisation to remove its override.

## Notes

- Depends on Bean 0264 merging (the configuration file and the freeze must exist first).
- Related: Bean 0153 (comments and docstrings), Bean 0264.
