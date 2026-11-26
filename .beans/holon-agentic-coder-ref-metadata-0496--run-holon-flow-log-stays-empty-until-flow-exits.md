---
# holon-agentic-coder-ref-metadata-0496
title: "run_holon_flow.py writes nothing to its log file until the flow exits"
status: scrapped
type: bug
priority: normal
tags:
  - flow
  - harness
  - logs
created_at: 2026-11-26T08:29:54Z
updated_at: 2026-11-26T08:29:54Z
---

## Problem

Launched `scripts/run_holon_flow.py` for intent `tests-fewer-git-worktree-exec` with stdout and stderr redirected to
`todo/flow-tests-fewer-git-worktree-exec.log`. The file stayed at 0 bytes for the whole run (about 1 h 15 min, through
Stage 2 to Stage 5). Its contents appeared only when the process exited. Progress could only be followed through the
flow worktree's checkpoint file and git log, so a stall could not be seen from the log.

## Why it matters

The log is the first place a stall, a quota wait or an overlap refusal shows up. An empty log for the whole run hides
those states from whoever is monitoring, and the parked-flow rule depends on seeing the refusal promptly.

## Next step

Check whether the wrapper's output is block-buffered when redirected to a file (PYTHONUNBUFFERED is set only for the
flow process, not for the wrapper), and make the wrapper flush each stage line as it prints. Add a test that a stage
transition reaches the log file before the flow exits.

Found 2026-11-26 while running the batch 3 flow (bean 0405).

## Scrapped (coordinator, 2026-11-26)

Duplicate of Bean 0385 (flow log file stays empty until the run ends). Its evidence is folded into 0385.
