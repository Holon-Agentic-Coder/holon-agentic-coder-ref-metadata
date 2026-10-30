---
# holon-agentic-coder-ref-metadata-0193
title:
  "Decompose the intent and plan stage modules (validate_intent_questions, run_plan_stage, decomposition, stage
  conflicts)"
status: todo
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0187
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. Measured on `993b686` (radon): `validate_intent_questions` CC **59**,
`check_and_resolve_stage_conflicts` CC 44, `run_plan_stage` CC 30, `_run_decomposed_plan` CC 30, `run_intent_stage`
CC 23. The plan budget and sub-intent helpers (`_plan_budget_decision`, `_sub_intent_depth`, `_child_context`,
`_child_intent_branch` ...) are free functions over the same context.

## Scope

1. `IntentQuestions` (rules as a table of small named checks instead of one 59-branch function).
2. `PlanStage` and `PlanDecomposition` objects owning their budget decision and child-branch naming.
3. `check_and_resolve_stage_conflicts` split into detect / classify / resolve steps.
4. All touched functions within the 0185 limits; behaviour and messages unchanged.

## Touch set

`flow/intent_questions.py`, `flow/stages/intent.py`, `flow/stages/plan.py`, `flow/stages/decomposition.py`,
`flow/stage_conflicts.py` and their mirrored tests.

## Dependencies

Blocked by 0187; if 0190 moves `stage_conflicts`, run after 0190. Parallel-safe with 0191, 0194 and 0197. Sequence with
0161 (sub-intent flow path), which edits the decomposition code.

## Notes

- Run through the Holon flow on holon-agentic-coder.
