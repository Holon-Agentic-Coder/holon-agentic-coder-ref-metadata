---
# holon-agentic-coder-ref-metadata-0485
title: "A flow's module_budget_change intent field does not clear the CI hygiene budget gate"
status: todo
type: bug
priority: high
tags:
  - hygiene
  - module-budget
  - flow
  - holon-agentic-coder
created_at: 2026-11-26T06:10:00Z
updated_at: 2026-11-26T06:10:00Z
---

## Problem

Flow `module-line-budget-all-packages` (bean 0380, holon-agentic-coder half) carries the `module_budget_change` intent
field. The flow authorised the change to `holon-config/hygiene/module_budgets.json` and its PR (#317) passes the unit,
build, integration and analysis checks. The `hygiene (ubuntu-latest)` job still fails at "Check module budgets" with
"differs from the merge-base copy", because `scripts/module_budget_freeze.py` in CI only accepts the change when the
`module-budget-change` pull request label is set (or `HOLON_ALLOW_MODULE_BUDGET_CHANGE=1`). The intent field is not
carried to the CI job.

## Expected

Either the flow applies the CI authorisation (label or env) for an intent that carries `module_budget_change`, or the
flow stops with a clear "needs the module-budget-change label" notice before Stage 5, rather than leaving a PR whose
required check is red. The maintainer decides whether the label is added by hand.

## Notes

- Found while driving PR #317 (2026-11-26). The label was not applied by the agent: the label is the maintainer's
  CI-side authorisation channel.

## Correction (coordinator, 2026-11-26)

The claim that CI does not read the label is wrong: `test-hygiene.yml` on `main` already passes the
`module-budget-change` label to `scripts/check_module_budgets.py` (see Bean 0486 resolution). What remains true and is
this bean's scope: the Stage 4 review loop has no input path for a maintainer decision (no PR comment or label is read),
so a decision such as "use a 400-line default" can only reach a running flow by stopping it and resuming with an amended
intent.
