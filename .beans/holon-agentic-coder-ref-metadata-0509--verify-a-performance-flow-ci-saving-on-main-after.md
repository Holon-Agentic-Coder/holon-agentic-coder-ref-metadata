---
# holon-agentic-coder-ref-metadata-0509
title: "Verify a performance flow CI saving on main after it merges and record it"
status: todo
type: task
priority: high
tags:
  - flow
  - ci
  - measurement
  - calibration
  - holon-agentic-coder
created_at: 2026-11-26T10:50:00Z
updated_at: 2026-11-26T10:50:00Z
---

## Problem

Self-improvement audit 2026-11-26T10:50Z. Today's test batches (#323, #325, #327; unit-only refactors) were asked to cut
CI time, but nothing measures the result after merge. Job times on `main` pushes (seconds, from `gh run view` jobs):

| Job                         | Before (pushes 22:51Z to 08:46Z, n=6) | After (pushes 08:47Z to 09:54Z, n=5) | Change      |
| :-------------------------- | :------------------------------------ | :----------------------------------- | :---------- |
| unit (macos-latest)         | 478 to 647, median 560                | 347 to 575, median 445               | about -20 % |
| unit (ubuntu-latest)        | 159 to 260, median 238                | 153 to 230, median 171               | about -28 % |
| Workspace survival (ubuntu) | 204 to 341, median 268                | 251 to 326, median 269               | **0 %**     |

The 40 percent targets of the test intents were not met on macOS, survival did not move at all and is now the longest
ubuntu job (it re-runs the whole unit selection, bean 0447), and the run-to-run spread on macOS (347 to 575 after) is as
large as the saving. No flow, calibration report or bean records this comparison, so the next batch is planned from
impressions.

## Proposed fix

- A post-merge step (in the `post-pr-merge` skill) for any bean tagged performance: read the three job medians for the
  five `main` pushes before and after the merge, write the table into the bean's Resolution, and open a follow-up bean
  when the target is missed.
- Raise bean 0447 (survival shares the unit run) to high: it is the one job the batches did not touch.

## Expected gain

Stops spending flows on changes with no measured effect; points the next batch at survival (about 270 s) and macOS
variance. Cost: one read-only script and a skill step. Related: 0482 (estimate before launch), 0499, 0447, 0400.
