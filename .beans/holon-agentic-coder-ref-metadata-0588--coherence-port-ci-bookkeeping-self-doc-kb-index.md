---
# holon-agentic-coder-ref-metadata-0588
title: "Port ci_bookkeeping_gate, self-explaining check, budget-label actor check, and remove KB index.json"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - ci
  - hygiene
  - invariants
created_at: 2026-11-27T00:33:33Z
updated_at: 2026-11-27T07:27:06Z
---

## Problem

`holon-agentic-coder` now enforces `scripts/ci_bookkeeping_gate.py` (PR `#346`), AST-based
`scripts/check_self_explaining.py` (PR `#357`), maintainer-actor verification on `module-budget-change` labels in
`scripts/check_module_budgets.py` (PR `#366`), and derived KB indexing with no committed `index.json`. `holon-coherence`
(`HEAD 18084f3`) still lacks these CI/hygiene guardrails and continues committing legacy
`holon-knowledge/kb/*/index.json` conflict magnets.

## Evidence

- `apps/holon-coherence/main/scripts/` contains only `check_ci_runtime_budget.py`, `check_module_budgets.py`,
  `ci_timing_gate.py`, `module_budget_base.py`, and `pre_commit_check.py` (no `ci_bookkeeping_gate.py`, no
  `check_self_explaining.py`, and no actor check on `module-budget-change`).
- `apps/holon-coherence/main/holon-knowledge/kb/failure_modes/index.json` and `patterns/index.json` remain tracked on
  `main` (unlike `holon-agentic-coder`, which uses derived indexing).
- Note: 3-ledger store/append-only checks and harness-reference checks for both repos are already tracked in Beans
  `0563` and `0564`.

## Proposed Change

1. Port `ci_bookkeeping_gate.py`, `check_self_explaining.py` (covering code + PR/ledger invariant rules cleanly), and
   `module-budget-change` maintainer-actor verification into `holon-coherence/scripts/` and `.github/workflows/`.
2. Remove the tracked legacy `holon-knowledge/kb/{failure_modes,patterns}/index.json` files (and ignore derived
   `index.json` if needed) so concurrent KB additions never collide.

## Acceptance Criteria

- `holon-coherence` CI enforces bookkeeping gating, self-explaining checks, and authorised budget-label checks on every
  PR.
- `holon-knowledge/kb/*/index.json` files are no longer tracked in `holon-coherence`.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Related shared-invariant beans: Bean `0563` (3 append-only ledgers check), Bean `0564` (no harness refs in targets),
  Bean `0558` (self-explaining gate), Bean `0570` (budget-change authorisation).
- Source: 2026-11-27 architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
