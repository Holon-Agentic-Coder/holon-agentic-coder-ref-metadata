---
# holon-agentic-coder-ref-metadata-0446
title: "Stage 3 admission blocks SPLIT parent plans on union touch set before decomposition"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - decomposition
  - holon-agentic-coder
created_at: 2026-11-25T04:02:00Z
updated_at: 2026-11-25T05:45:00Z
---

## Problem

In `ExecuteStage.admit_and_refresh_plan` (`flow/stages/execute.py:213-223`), when `_plan_budget_decision(context)`
returns `DECISION_DECOMPOSED` (`SPLIT`), Stage 3 still runs `admission_stage_failure(context, state.start_time)` against
the parent plan's union touch set before `_run_decomposed_plan` runs. A `SPLIT` parent never executes code directly —
each sequential child plans and runs its own Stage 3 admission on its narrow subset — so blocking on the parent's broad
union (especially when `intent.scope` includes a directory prefix such as `apps/sandbox-executor/tests/`) serializes the
entire decomposed flow behind unrelated PRs that touch any file under that prefix or belong only to later children.

## Evidence (`2026-11-25T02:54Z–03:54:45Z` fifth-merge audit)

- Bean `0407` (`no-unneeded-full-review`, `P-1795574132-ANA-G4N`) decided `SPLIT` into 4 sequential child intents
  (`max child entropy 5.25`) at `2026-11-25T02:41:03Z`, with child 1 scoped to `flow/review/` (`gate_state.py`,
  `approval_fingerprint.py`, etc.) and new `test_gate_state.py`.
- Because `admit_and_refresh_plan` checked the parent touch set (`apps/sandbox-executor/tests/` + `budgets.py`), Stage 3
  refused `0407` at `02:41:40Z` on **7** in-flight items (`#299`, `#296`, `#292`, `#290`, `#289`, `#287`,
  `workspace-survival-job-parallel`), idling **`60.75 min`** across the `02:54:00Z–03:54:45Z` window (`73.08 min` total
  since `02:41:40Z`).

## Proposed change

1. In `ExecuteStage.admit_and_refresh_plan` (`flow/stages/execute.py`), when `precheck.decision == DECISION_DECOMPOSED`
   and `_sub_intent_depth_error(context) is None`, skip parent-level touch-set admission and delegate admission to each
   child's own Stage 3 (while still refreshing the parent plan branch against `origin/<target>` if needed).
2. Add a hermetic unit test in `tests/flow/stages/test_decomposition.py` verifying a `DECISION_DECOMPOSED` parent whose
   union touch set overlaps an in-flight PR proceeds into child 1 rather than halting the parent at Stage 3.
3. In the harness, clarify in intent-authoring guidance that `scope` should list concrete file paths rather than broad
   directory prefixes like `apps/sandbox-executor/tests/`.

## Expected gain

Eliminates false-positive Stage 3 blocks on decomposed multi-child flows (`60.75+ min` wait saved on `0407` in this
window alone) and prevents unrelated PRs in broad directories from stalling child 1.

## Cost

Small: guard in `flow/stages/execute.py` + unit test, delivered via the Holon flow (`holon-agentic-coder`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0348` (PR #226 actual PR files), Bean `0407` (`no-unneeded-full-review`), Bean `0395` (Stage 3 overlap
  work).

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- 0407 is still refused at 05:41Z, about 180 min after 02:41:40Z. No wrapper is alive to relaunch it, so it stays
  stopped until someone relaunches it by hand.
- Proposed change 3 (scope lists files) has no home in the harness today. The rule exists only in Claude Code's private
  memory, so the Antigravity session that wrote the 0407 intent could not see it (Bean 0459).
