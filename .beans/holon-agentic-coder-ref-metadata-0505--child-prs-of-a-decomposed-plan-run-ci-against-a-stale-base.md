---
# holon-agentic-coder-ref-metadata-0505
title: "Child PRs of a decomposed plan run CI against the plan branch's stale copy of main"
status: todo
type: bug
priority: high
tags:
  - flow
  - decomposition
  - ci
  - module-budget
  - holon-agentic-coder
created_at: 2026-11-26T10:30:00Z
updated_at: 2026-11-26T10:30:00Z
---

## Problem

The flow `no-unneeded-full-review` (decomposed into five children, PRs #316, #318, #322, #324, #328 into its plan
branch) cut its plan branch before #317 and #326 changed `holon-config/hygiene/module_budgets.json` on `main`. Child PR
#328's head (1e221bed) has `entrypoint/review_loop.py` 927, `env_registry.py` 954 and `flow/__init__.py` 562 lines, over
`main`'s frozen overrides (913, 931, 522), yet its hygiene check passes because the plan branch still carries the old
budget file. The children's CI therefore validates against a stale base, the budget growth accumulates across children
unnoticed, and the breach surfaces only when the parent PR into `main` syncs, after hours of work.

## Proposed fix

- Before each child starts and before each child PR's CI gate, merge `origin/main` into the plan branch (mechanical
  sync; ledger/KB conflicts resolved as today), so children run CI against current `main` config.
- At minimum, run the budget check of the child head merged with `origin/main` in the child's CI gate and raise it as a
  finding.
- Related: Bean 0493 (approved PR goes stale when main tightens budgets), Bean 0479 (parent PR re-reviewed in full).
