---
# holon-agentic-coder-ref-metadata-0495
title: "Resumed flow wrote no progress to its log, and Stage 5 overran its budget by counting the CI wait"
status: todo
type: bug
priority: normal
tags:
  - flow
  - logs
  - holon-agentic-coder
created_at: 2026-11-26T08:30:00Z
updated_at: 2026-11-26T08:30:00Z
---

## Problem

While resuming PR #320 (preflight-outage-wait-resume) from `--from-stage review` with a checkpoint, two things were
observed. Both were seen once; the cause of the first is not confirmed.

1. The resumed `run_holon_flow.py` process, launched with `>> todo/flow-<slug>.log 2>&1`, wrote nothing to that log for
   about 35 minutes while review and calibration ran (file size and mtime unchanged). Progress was only visible in the
   flow worktree's commits and the background task output. Likely cause: the wrapper's stdout is block-buffered
   (PYTHONUNBUFFERED is set only for the `holon flow` child), but this is unverified.
2. Stage 5 logged `WARNING: Stage 'calibrate' ran 13.9 min against its 10 min budget; keeping its 'success' result.`
   Roughly 13 of those minutes were the Stage 4 CI wait (about 780 s) performed inside calibration, so the budget figure
   counts a wait the stage does not own.

## Next step

Confirm whether the wrapper's stdout is flushed (run with and without PYTHONUNBUFFERED=1 and compare the log). Decide
whether the calibrate budget should exclude the CI wait, and log that wait as its own stage line. Found 2026-11-26 while
resuming PR #320.
