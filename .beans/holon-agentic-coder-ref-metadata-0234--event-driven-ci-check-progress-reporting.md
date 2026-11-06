---
# holon-agentic-coder-ref-metadata-0234
title: "Event-driven CI check progress reporting during Stage 4 review"
status: todo
type: feature
priority: normal
tags:
  - flow
  - review-loop
  - ci
  - logging
  - holon-agentic-coder
created_at: 2026-11-05T14:25:00Z
updated_at: 2026-11-05T14:25:00Z
---

## Problem

During Stage 4 review loop execution, `_wait_for_pending_ci()` in `sandbox_executor.flow` polls GitHub CI checks at
fixed 15-second intervals and emits a log message on every tick:

```text
[2026-11-05T14:19:13Z] [Review Loop] Waiting for 10 pending GitHub CI check(s)...
[2026-11-05T14:19:30Z] [Review Loop] Waiting for 7 pending GitHub CI check(s)...
[2026-11-05T14:19:46Z] [Review Loop] Waiting for 7 pending GitHub CI check(s)...
[2026-11-05T14:20:03Z] [Review Loop] Waiting for 6 pending GitHub CI check(s)...
[2026-11-05T14:20:19Z] [Review Loop] Waiting for 5 pending GitHub CI check(s)...
```

This causes two issues:

1. **Polling Noise**: It prints repetitive heartbeat messages (e.g. repeated `Waiting for 7 pending...`) even when no
   pipeline or check status has changed.
2. **Lack of Specificity**: It does not report the total number of pipelines/checks being tracked at the start, nor
   which specific check finished when the counter decrements.

## Decision

Transform CI check waiting into clean, event-driven progress reporting:

1. **Initial Announcement**: At the start of waiting, report the total number of discovered checks once:
   ```text
   [Review Loop] Tracking 10 GitHub CI check(s) (10 pending)...
   ```
2. **Transition-Driven Logging**: Poll quietly in the background without emitting heartbeats at every sleep interval.
   Log only when one or more checks finish or transition state:
   ```text
   [Review Loop] CI check 'Lint and Format' completed (passed) — 9 pending
   [Review Loop] CI check 'Unit Tests (Python 3.13)' completed (passed) — 8 pending
   ```
3. **No Noise on Unchanged State**: If a poll interval elapses and no check has changed state, emit no log line.
4. **Final Summary**: When all checks finish or the deadline expires, report the final outcome once.

## Scope

1. **Update `_wait_for_pending_ci` in `sandbox_executor.flow`**:
   - Maintain a map of check names and their previous states.
   - Detect state transitions between polling intervals and log individual check completions.
   - Suppress redundant periodic poll messages when check counts are unchanged.
2. **Tests**:
   - Add unit tests in `apps/sandbox-executor/tests/test_flow.py` asserting that completions trigger log lines and quiet
     intervals emit no duplicate messages.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be delivered through the Holon flow (`holon flow`).
