---
# holon-agentic-coder-ref-metadata-0521
title: "Main-push gate runs the full suite when the merged PR head job is still running; wait for it instead"
status: todo
type: task
priority: normal
tags:
  - ci
  - pipeline
  - holon-agentic-coder
created_at: 2026-11-26T13:40:00Z
updated_at: 2026-11-26T13:40:00Z
---

## Evidence

Self-improvement audit 2026-11-26T13:40Z, question (5).

- #333 (per-SHA concurrency): in order, no cancelled main run since 10:51Z; every main push in the window ran to
  completion.
- #337 (tested-tree skip): works for an isolated merge. #345 (`1567b6b`, 13:32Z) logged
  `decision=SKIP rule=main-push-tested-tree detail=#345 head d5e31a2d3849` on both unit legs, the run took 19 s.
- It did not skip #334 (`20687d4`), #340 (`72de702`) and #343 (`f1e18bc`): all three logged
  `decision=RUN rule=main-push-head-job-not-finished` (`in_progress in run 2176`, `in_progress in run 2181`,
  `queued in run 2184`). The PR was merged while its head's unit job was still running, so the gate fell back to the
  full suite: unit 8.6 min (macOS) on `72de702`, 5.9 min on `f1e18bc`, survival and stress as well, about 17
  runner-minutes each.
- 0514 (burst coalescing) covers back-to-back merges; this is the single-merge case where the head run is simply not
  finished yet. Of the 5 merges in this audit window, 1 skipped and 4 ran full.

## Proposed change

- When the head job is queued or in progress, the gate polls it (up to the head job's own timeout, say 15 min, 30 s
  interval) and decides on its result: success on an equal tree skips, failure or cancel runs. Only a missing head run
  runs at once.
- Better: run the gate step first so a waiting main job holds no macOS runner while it polls (the check is a few API
  calls).

## Expected gain

Up to 17 runner-minutes on each merge made before the head CI finishes (3 of 5 here). Cost: a job that waits instead of
runs; worst case it waits as long as the full suite would have taken. Keep the daily scheduled full run. Related: 0514,
0510 (completed), 0461.
