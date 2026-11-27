---
# holon-agentic-coder-ref-metadata-0531
title: "Break flow/entrypoint and ledger/knowledge import cycles and decompose ExecutionRun, planner, turns"
status: in-progress
type: task
priority: high
tags:
  - holon-agentic-coder
  - architecture
  - complexity
  - refactor
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T17:47:32Z
---

## Problem

Bidirectional import cycles link `flow` ↔ `entrypoint` (11 imports each way) and `ledger` ↔ `knowledge`, while
`FlowContext.__post_init__` triggers proxy-resolution side effects during dataclass instantiation and `ExecutionRun`,
`entrypoint/planner.py:main`, and `turns.py:run_turn` carry extreme state/complexity counts.

## Evidence

- Bidirectional `flow` ↔ `entrypoint` cycle (11 imports in each direction, e.g.
  `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py:51-56`, `flow/review/loop.py:16`,
  `flow/stages/execute.py:20`).
- `ledger` ↔ `knowledge` cycle (`ledger/rows.py:324` imports `CredentialRedactor` from `knowledge.records`).
- `review_target.py:12,127,159,186,223`: deferred private imports from `flow`.
- `flow/github/token_scopes.py:7`: imports from `launcher.mounts`.
- `flow/context.py:189-194`: `FlowContext.__post_init__` calls side-effecting `coherence.resolve_flow_proxy_choice()`.
- `entrypoint/executor/run.py:89-141`: 5-mixin god object `ExecutionRun` holding 42 mutable attributes.
- Complexity hotspots outside `run_review_loop` (Bean `0192`) and `calibration.py` (Bean `0197`):
  `entrypoint/planner.py:329` (`main`, CC=50, 321 lines) and `turns.py:543` (`run_turn`, CC=49, 189 lines, 18
  parameters).

## Proposed Change

1. Extract shared contracts, redaction interfaces, and review-target models into leaf modules to break `flow` ↔
   `entrypoint`, `ledger` ↔ `knowledge`, `flow/github` → `launcher`, and `review_target` → `flow._*` cycles, guarded by
   an automated import-layer test.
2. Move `coherence.resolve_flow_proxy_choice()` out of `FlowContext.__post_init__` into an explicit factory/builder.
3. Replace `ExecutionRun`'s 5-mixin inheritance with composed collaborators, and decompose `entrypoint/planner.py:main`
   and `turns.py:run_turn` using typed config/request parameter objects.

## Acceptance Criteria

- Automated import-layer test verifies zero circular dependencies across `flow`, `entrypoint`, `ledger`, `knowledge`,
  `launcher`, and `runners`.
- `FlowContext(...)` construction is pure (zero proxy/network/subprocess side effects).
- `planner.py:main`, `turns.py:run_turn`, and `ExecutionRun` meet Ruff complexity limits without bloated parameter lists
  or 5-mixin state bags.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`; re-verified at `2a83e4cc7`).
- Related existing beans: Bean `0192` (`run_review_loop`/`run_review_stage`), Bean `0197` (`calibration.py`), Bean
  `0152`/`0489` (module budgets).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- **Audit update (2026-11-27T11:52Z, `2a83e4cc7`):** `entrypoint <-> flow` (`12<->15`) and `knowledge <-> ledger`
  (`4<->1`) cycles remain (PR `#415` / `0615` import-cycle ratchet is `3/3 APPROVED` + `CLEAN`, awaiting merge);
  `flow/review/loop.py` (`run_review_loop`) grew after `#412` to `947` lines (`3` lines below its `950`-line budget
  override) and `CC=219` (up from `207`), while `planner.py:main` (`49`) and `turns.py:run_turn` (`49`) stay elevated.

## Flow

- **Slice 1 (`2026-11-27`, `hac-ledger-knowledge-cycle`):** Extracts `CredentialRedactor` into acyclic leaf module
  `sandbox_executor/credential_redactor.py`, re-exports it from `knowledge/records.py`, updates `ledger/rows.py` so
  `sandbox_executor.ledger` has zero imports from `sandbox_executor.knowledge`, and verifies via AST + parity tests in
  `tests/test_ledger_knowledge_acyclic.py` (`todo/intent-0531-hac-ledger-knowledge-cycle.json`,
  `todo/intent-coverage-0531.json`). Completed all 5 Holon stages (`antigravity-agent` / `gemini-4-neon`, predicted EV
  `36.82`, actual EV `45.40`, `ΔEV: +8.58`, 3/3 consensus `APPROVED`, `16/16` CI checks passing, `MERGEABLE`/`CLEAN`) at
  PR [`#439`](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/439) (branch
  `I-1795800327-hac-ledger-knowledge-cycle/P-1795800376-ANA-G4N/E-1795800568-ANA-G4N/_`, worktree
  `apps/holon-agentic-coder/flow-hac-ledger-knowledge-cycle`, checkpoint
  `apps/holon-agentic-coder/flow-hac-ledger-knowledge-cycle/.holon/flow/checkpoint-hac-ledger-knowledge-cycle.json`),
  awaiting human merge. Remaining cycles (`flow <-> entrypoint`, `flow/github -> launcher`), pure `FlowContext`, and
  hotspot decompositions are deferred to subsequent slices.
- **Slice 2 (`2026-11-27`, `hac-turns-run-turn-decompose`):** Decomposes `turns.py:run_turn` into cohesive helpers
  backed by a typed config/request dataclass while preserving 100% backward-compatible kwargs, verified in
  `tests/test_turns.py` and `tests/test_turn_supervisor.py` (`todo/intent-0531-hac-turns-run-turn-decompose.json`).
