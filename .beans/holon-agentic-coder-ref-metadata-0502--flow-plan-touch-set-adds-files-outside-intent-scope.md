---
# holon-agentic-coder-ref-metadata-0502
title: "Planner touch set adds files outside the intent scope and blocks admission on a sibling flow"
status: todo
type: bug
priority: normal
tags:
  - holon-flow
  - harness
  - admission
created_at: 2026-11-26T09:37:00Z
updated_at: 2026-11-26T09:37:00Z
---

## Problem

Flow `single-runner-per-checkpoint` (intent 0390 backfill) was refused at Stage 3 admission on
`apps/sandbox-executor/tests/flow/conftest.py`, which is not in its intent scope. The refusal names the sibling flow
`tests-fewer-git-stage-pipeline` (I-1795684868) as the overlap. The plan (P-1795685415) introduced the file into the
touch set, so the overlap came from the plan, not from the declared scope.

## Asks

- Decide whether the plan may widen the touch set beyond the intent scope; if not, reject the plan rather than admit it.
- If it may, report the added files in the refusal so the coordinator can see the cause.

## Notes

- Flow parked with its checkpoint kept; resumed only from the checkpoint once the sibling flow releases the file.

## Evidence (audit 2026-11-26T10:50Z)

Of PRs #325 to #331, #326 (`planner.template.md`), #327 (10 files, plan returned to Stage 2 at 08:28Z) and #330
(`flow/review/loop.py`) changed files outside the intent scope and were approved. See bean 0508 for the intent-side fix.
