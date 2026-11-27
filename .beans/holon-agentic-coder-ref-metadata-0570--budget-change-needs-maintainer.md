---
# holon-agentic-coder-ref-metadata-0570
title: "Check: module budget changes only with explicit maintainer authorisation"
status: completed
type: task
priority: critical
tags:
  - harness
  - module-budget
  - invariants
  - holon-agentic-coder
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-27T01:19:03Z
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

2026-11-26T23:52:52Z: target half launched as flow module-budget-label-actor (intent in the scratchpad; label-actor
check in the hygiene job). 0560 was skipped: parked 0216 plans pr_metadata.py and its test.

2026-11-27T00:29:22Z: target half done: flow module-budget-label-actor completed (claude-agent, claude-opus-5-5 after
the fable spend-limit step-down); PR #366 APPROVED 3/3 at iteration 1, CI 11/11 green, calibration in diff,
MERGEABLE/CLEAN; awaiting maintainer merge. Diff scan: no docstrings; one tool pragma (`# type: ignore[arg-type]`) in
scripts/check_module_budget_label_actor.py flagged for the maintainer, not edited.

2026-11-27T00:32:54Z: PR #366 (flow module-budget-label-actor) merged into main at f006e79b (2026-11-27T00:29:24Z). The
check reads the label's actor and that actor's admin permission, and runs on labeled/unlabeled pull_request events.
Still open: the CI bullet also requires the intent to carry `module_budget_change`;
`scripts/check_module_budget_label_actor.py` reads no intent and no CI step checks it, so this bean stays in-progress.
Harness gate tests pass (budget tests in `tests/test_flow_gates.py`). Measured #366 additions: 0 docstrings;
non-`# why:` comment tokens are a shebang and one `# type: ignore` pragma (noted on bean 0153); one `# why:` line in the
workflow. Slug worktree and branches removed. Open PR #365 does not change `holon-config/hygiene/module_budgets.json`,
so the check does not gate it.

## Resolution

Delivered via [PR #373](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/373) and merged into `main`
(`45672ecb`) at 2026-11-27T01:16:57Z, closing the target half:

- **Key Architectural Deliverables**: `scripts/check_module_budget_label_actor.py` also requires an added intent row in
  `holon-knowledge/ledger/intents.jsonl` or `holon-knowledge/ledger/pending/intents/*.jsonl` with a non-empty string
  `module_budget_change` whenever `holon-config/hygiene/module_budgets.json` changes. The hygiene job already runs with
  `fetch-depth: 0`, so the workflow needed no change. The harness half (auto-injection removed from the flow wrapper)
  landed earlier and is excluded per `todo/intent-coverage-0570.json`.
- **Verification & Tests**: eight tests in `apps/sandbox-executor/tests/test_check_module_budget_label_actor.py` use
  real temporary git repositories: a missing, empty, whitespace-only or non-string field is refused; an admin label with
  a non-empty field passes; an unchanged budget file passes without an intent row. A temporary revert of the refusal
  failed 8 tests. `uv run task test` passed (9537 passed, 7 skipped) and `uv run task lint` exited 0 in the flow
  execution record. Remote unit, integration and workspace-survival jobs were still running at merge time, with no
  failures reported.
- **Holon Flow Traversal**: flow `budget-change-intent-field-ci` (intent, plan, execution and calibration records)
  merged; its branches and worktree are removed.
