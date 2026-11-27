---
# holon-agentic-coder-ref-metadata-0605
title: "Wrapper refuses a foreground flow run; the CF-0036 rule was broken again two hours later (CF-0038)"
status: todo
type: bug
priority: high
tags:
  - harness
  - holon-flow
  - wrapper
  - coordinator-failure
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T04:33:33Z
---

## Evidence

- CF-0036 (02:18Z): a flow resumed in a foreground script outlived the wall clock and killed the engine; rule: launch
  every flow run with a short timeout so it moves to the background.
- CF-0038 (04:23Z): self-doc-tests-45 started in a foreground script with a 600 s timeout; wrapper and engine were
  killed during Stage 3. Same rule, same failure, 2 hours apart. A recorded rule that is broken again is a high-priority
  repeat (audit rule).
- Related halts: second CF-0028 row (03:40Z, host push rejected then a duplicate Stage 3 and a second execution branch)
  and CF-0035 (push rejected, no retry guard) both ended in a hand resume; bean 0600 covers the engine retry but is
  still todo.

## Goal

1. `run_holon_flow.py` (or the `holon flow` wrapper) detaches itself: it forks to the background, writes the log path
   and PID, and returns within a few seconds, whatever timeout the caller gave. A foreground run needs an explicit
   `--foreground` for the maintainer's terminal.
2. The wrapper writes a heartbeat to the checkpoint so a killed engine is recognised as dead with a reason, and an
   orphaned executor container is adopted or stopped by a defined step, not by luck.
3. A test starts the wrapper with a 600 s timeout in a subprocess and asserts it returns quickly and the run survives
   the parent's death.

## Expected gain and cost

Gain: removes a failure class that cost about 10 minutes of orphaned work each time and a hand resume; no brief wording
can fail again. Cost: a wrapper change (touch set: the wrapper and its test only).

## Notes

- Source: self-improvement audit 2026-11-27. Related: CF-0036, CF-0038, 0600, 0592.
