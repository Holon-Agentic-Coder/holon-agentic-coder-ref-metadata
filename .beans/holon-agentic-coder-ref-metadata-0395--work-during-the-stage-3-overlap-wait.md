---
# holon-agentic-coder-ref-metadata-0395
title: "Stage 3 works during an overlap wait instead of idling until the blocking pull request merges"
status: todo
type: feature
priority: high
tags:
  - flow
  - stage-3
  - admission
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

When a plan's touch set overlaps a pull request in flight, Stage 3 admission refuses it and the flow does nothing until
that pull request merges or closes. On 2026-11-24 three flows (Beans 0197, 0216, 0225) idled for about 3.5 hours behind
PR #268, which was approved and calibrated and only needed the maintainer's merge. Part of the overlap was `README.md`
alone.

## Goal

- An overlap no longer stops the work, only the push. Stage 3 executes at once on the current base and keeps the result
  local (or on a branch that opens no pull request).
- When the blocking pull request merges or closes, the flow syncs with the target, resolves any conflict on discovery
  (Bean 0376's resolver), re-runs the tests, and publishes.
- First step: apply this to low-risk overlaps (documentation, registries, generated lists). Overlaps on core engine
  files keep the strict wait until the first step has proved itself; the maintainer found sequential runs cheaper there.
- The class of an overlap (low-risk or strict) is decided by rule from the overlapping paths and shown in the refusal.

## Notes

- Overlap: Bean 0394 recommendation 1 is the same change. This bean owns the fix.
- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Depends on Bean 0376 (conflict resolution at every stage).
- Fail early applies: a conflict the resolver cannot settle is reported at once, not at the end.

## Measured (self-improvement audit 2026-11-24)

In the period 2026-11-21 to 2026-11-24, 50 of 140 flow runs ended at a Stage 3 overlap refusal and were launched again;
the 48 measured waits total 39.8 hours of flow time (median 1.1 minutes, longest 17.5 hours on execute-stage-object).
Each wait is a full relaunch (pre-flight, admission) rather than a wait inside one run, and its time cannot be read from
the logs as a wait (Bean 0412). The files behind most refusals are a handful of shared files (README 106 refusal lines,
`flow_module_budgets.json` 67, `flow/__init__.py` 53); Bean 0410 removes them from touch sets.
