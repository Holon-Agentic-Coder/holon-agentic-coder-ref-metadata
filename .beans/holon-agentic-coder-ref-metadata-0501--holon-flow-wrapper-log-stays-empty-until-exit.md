---
# holon-agentic-coder-ref-metadata-0501
title: "holon flow wrapper log stays empty until the flow exits"
status: todo
type: bug
priority: normal
tags:
  - harness
  - holon-flow
created_at: 2026-11-26T09:21:00Z
updated_at: 2026-11-26T09:21:00Z
---

## Problem

Found while driving `tests-constant-time-tmp-dirs` (2026-11-26) with `scripts/run_holon_flow.py` launched in the
background with `> todo/flow-<slug>.log 2>&1`. The log file stayed at 0 bytes for the whole run (about 2 h 10 min,
through Stages 3, 4 and 5), while the flow process and its Docker containers were alive and the checkpoint advanced. The
text only appeared after the flow exited.

## Why it matters

The driving subagent can only follow progress through the checkpoint and `git log` in the flow worktree. A stalled
stage, a refusal or a limit wait is invisible in the log while it happens. Monitoring also cannot tell a hung wrapper
from a healthy one.

## Next step

Find where the wrapper's output is buffered (the wrapper's own stdout is not flushed, or the flow's output is captured
and written at the end) and flush each stage transition and `holon flow` line as it happens. Check with a short
background run that the log grows during Stage 3.
