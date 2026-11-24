---
# holon-agentic-coder-ref-metadata-0414
title: "An edit outside the plan's touch set is caught during the executor turn, not after it"
status: todo
type: feature
priority: normal
tags:
  - flow
  - stage-3
  - touch-set
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

Fail early: a breach of the touch set is knowable the moment the executor writes the file, but the flow learns of it
only after the turn, discards the whole execution and plans again.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

Six executions in the period were discarded with "the execution changed N file(s) outside the plan's touch set;
returning to Stage 2 (re-plan attempt N of N)":

| Flow                           | Executor time discarded |
| :----------------------------- | ----------------------: |
| approval-survives-main-merge   |                26.3 min |
| layered-env-config-v2          |                19.1 min |
| execute-stage-object           |                18.5 min |
| resolve-conflicts-in-flow      |                15.6 min |
| no-fallback-calibration-report |                13.9 min |
| claude-code-mode-default-on    |                 8.6 min |

Total about 102 minutes of executor time, plus a re-plan (median 4.0 minutes) and a second execution each. The files
outside the touch set were mostly companions of the planned change: `flow/__init__.py`, `README.md`,
`flow_module_budgets.json`, test helpers.

## Proposed change

1. The executor is given the touch set and a write guard that refuses a write outside it during the turn, with a message
   that names the file; the executor either stays inside it or ends the turn asking for a re-plan with the reason.
2. The planner adds the usual companions of a change to the touch set (the package's `__init__.py` re-exports, the
   budget entry, the README section) when it touches a module that has them.

## Expected gain

About 102 minutes of executor time and six re-plans in the period; more as flows grow.

## Cost

Medium engine change in Stage 3 and the planner prompt.

## Notes

- Related: Bean 0410 (fewer shared companion files), Bean 0151 (planner touch set).

## Audit evidence (`2026-11-24T11:05Z–12:47Z`)

- `holon-agentic-coder#273` (`route-stage-4-and-stage-5`, Bean `0376` child 4): at `2026-11-24T11:07:42Z`, Stage 3
  execution (`21.3 min`) was discarded by `touch_set_guard` over 18 out-of-set files (`flow/__init__.py`,
  `lazy_exports_sync.py`, and 16 test files), forcing a `4.7 min` Stage 2 re-plan (`P-1795518467-ANA-G4N`) and a
  `25.2 min` Stage 3 re-execution.
