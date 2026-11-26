---
# holon-agentic-coder-ref-metadata-0570
title: "Check: module budget changes only with explicit maintainer authorisation"
status: in-progress
type: task
priority: critical
tags:
  - harness
  - module-budget
  - invariants
  - holon-agentic-coder
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:15:08Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

`holon-config/hygiene/module_budgets.json` changes only with an explicit `module_budget_change` intent field written by
the maintainer's instruction and the maintainer-only `module-budget-change` PR label.

## Violation today

`.agents/skills/holon_flow/scripts/run_holon_flow.py` (around line 613) auto-injects `module_budget_change` when the
intent filename contains `0380` or the scope mentions `module_budgets.json`, so agents stamp the maintainer's
authorisation themselves.

## Check

- Remove the auto-injection; a test proves an intent touching the budget file without the field is refused.
- Target CI: a PR changing the budget file fails unless it carries the `module-budget-change` label applied by the
  maintainer account (check the label event actor), and the intent has the field.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.

## Progress

2026-11-26T23:15:08Z: harness half done: auto-injection removed; an intent whose scope lists `module_budgets.json`
without a non-empty `module_budget_change` is refused (exit 2); tests in `tests/test_flow_gates.py`. The
module-budget-default-350 and default-400 intents already carry the maintainer's quoted instruction. Old 0380 coherence
intents lack the field and would now be refused (already done flows). Remaining: target CI label-actor check (maintainer
applies `module-budget-change`) needs a `holon flow`.
