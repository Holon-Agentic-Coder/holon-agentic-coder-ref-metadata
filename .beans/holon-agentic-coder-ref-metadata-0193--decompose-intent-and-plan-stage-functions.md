---
# holon-agentic-coder-ref-metadata-0193
title:
  "Decompose the intent and plan stage modules (validate_intent_questions, run_plan_stage, decomposition, stage
  conflicts)"
status: completed
type: task
priority: normal
tags:
  - refactor
  - complexity
  - holon-agentic-coder
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-21T12:52:05Z
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

## Audit (2026-11-21)

Blocker Bean 0187 was scrapped (the `flow/` split landed), so it is unblocked. Files now: `flow/intent_questions.py`,
`flow/stage_conflicts.py`, `flow/stages/{intent,plan,decomposition,plan_decision,sync_conflict}.py`. Open PR #219
(Bean 0190) rewrites `flow/intent_questions.py` and `flow/stage_conflicts.py`, so start only after it merges.

## Progress

- 2026-11-21: Holon flow `intent-plan-stage-decomposition` started (claude-agent, claude-opus-5-5).
- 2026-11-21: Flow finished. PR #228 is calibrated (EV predicted 33.19, actual -21.46), CI is green and the PR is
  MERGEABLE/CLEAN. There is NO consensus approval: Stage 4 was skipped because `skip_review` was set in the checkpoint.
- 2026-11-21: Resumed from Stage 4 with `skip_review` cleared. The review reached 3/3 APPROVED consensus at iteration 4
  and was recalibrated (EV predicted 33.19, actual 58.66). PR #228 is MERGEABLE/CLEAN with CI green and is awaiting the
  human merge.

## Resolution

Delivered via [PR #228](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/228) and merged into `main`
(`5fbd2d06`):

- **Key Architectural Deliverables**: intent and plan stage code split into
  `flow/stages/{intent,plan,decomposition,plan_decision,plan_support,stage_support,decomposition_summary}.py` and
  `flow/stage_conflict_resolution.py`; `validate_intent_questions` rewritten as a table of named checks; touched
  functions within the 0185 limits; behaviour and messages unchanged.
- **Final calibration**: Predicted EV 33.19 | Actual EV 58.66 (ΔEV +25.47).
- **Process note**: an earlier antigravity run saved `skip_review` into the checkpoint, so a resume skipped Stage 4 and
  the PR had no consensus approval. The review was rerun on claude-opus-5-5 (3/3 APPROVED at iteration 4) and
  recalibrated. The fix for resumes inheriting `skip_review` and the agent is bean 0356.
