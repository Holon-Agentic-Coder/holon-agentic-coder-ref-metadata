---
# holon-agentic-coder-ref-metadata-0604
title:
  "Queue order: critical and high harness beans (0590, 0596, 0600, 0579, 0581) are untouched while about 25 self-doc
  slices ran"
status: todo
type: task
priority: high
tags:
  - harness
  - scheduling
  - prioritisation
  - holon-flow
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T04:33:33Z
---

## Evidence

- Status and last update at audit time: 0590 (critical) todo, last edit 00:55Z; 0596 todo, 01:07Z; 0592 todo, 01:07Z;
  0579 and 0581 todo, 23:51Z; 0600 todo, 03:52Z; 0595 todo (edited 04:31Z with evidence only). None is progressing in 3
  to 5 hours.
- `todo/slot-keeper.log` shows launches growing from 13 (01:17Z) to 36 (03:32Z), nearly all 0153 slices (src-e..j,
  21..28, tests-45..53, plus package slices). Meanwhile intent-scope failures kept recurring (CF-0028 to CF-0034, seven
  rows in under two hours) and 0590 (generate intents from beans in the flow) is the stated root cause of them (audit
  00:57Z).
- The keeper only fills slots with flows. Beans 0590, 0596, 0600, 0579, 0581, 0592, 0595 are harness or engine work with
  no automatic owner, so they never enter the queue and nothing reports their age.
- Cost of the imbalance: each 0153 slice needs about 60 minutes of flow plus a review round for a change with no
  behaviour value, while the recurring errors it stands next to (CF-0037 duplicate driver, CF-0028b double Stage 3) cost
  duplicate runs.

## Goal

1. The coordinator keeps an "age of untouched critical or high harness beans" line in the triage matrix; any critical
   bean older than 2 hours without an owner is launched next, ahead of any 0153 slice (the maintainer already ranks them
   higher).
2. Cap 0153 slices at a quarter of the slots (2 of 8) while a critical or high flow or harness bean is ready.
3. Report to the maintainer at each audit which of those beans moved.

## Expected gain and cost

Gain: removes the cause of the intent-scope repeats (0590) and the duplicate-driver and push-retry runs (0592, 0600)
sooner; slices still finish, 2 slots slower. Cost: a rule in coordination.md and the matrix; no code.

## Notes

- Source: self-improvement audit 2026-11-27. Related: 0590, 0592, 0596, 0600, 0579, 0581, 0153. Extends the maintainer's
  "slots always working" rule: slots are filled by value, not by arrival order.
