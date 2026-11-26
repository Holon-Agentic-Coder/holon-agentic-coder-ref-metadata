---
# holon-agentic-coder-ref-metadata-0486
title: "CI's frozen budget-config check fails an authorised module budget change, so its flow loops in review"
status: todo
type: bug
priority: high
tags:
  - hygiene
  - module-budget
  - ci
  - flow
  - holon-agentic-coder
created_at: 2026-11-26T06:15:00Z
updated_at: 2026-11-26T06:15:00Z
---

## Problem

PR #317 (bean 0380, flow `module-line-budget-all-packages`) changes `holon-config/hygiene/module_budgets.json` under the
maintainer's authorisation, carried in the intent's `module_budget_change` field. The flow's own guards honour that
field, but CI's `hygiene (ubuntu-latest)` step "Check module budgets" compares the file byte-for-byte with the merge
base and has no way to see the authorisation. It failed on all four PR heads (runs 45763358922, 45764785555,
45765449520, 45766269700), and the review loop reached iteration 8 because the resolver cannot make CI green without
weakening the guard or reverting the authorised change.

## Proposed fix

Give CI a verifiable signal for an authorised budget change, decided by the maintainer. Options: a PR label only the
maintainer applies; the check reading the PR's intent row (`module_budget_change`) from the ledger; or a signed commit
trailer. The review loop should also classify a failure the resolver must not fix as a halt-and-report, not another
iteration (see Bean 0407, Bean 0409).

## Notes

- Found 2026-11-26 while checking why #317 was on review iteration 8.
