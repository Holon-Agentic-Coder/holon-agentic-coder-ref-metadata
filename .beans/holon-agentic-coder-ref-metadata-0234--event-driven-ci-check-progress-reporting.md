---
# holon-agentic-coder-ref-metadata-0234
title: "Event-driven CI check progress reporting during Stage 4 review"
status: completed
type: feature
priority: normal
tags:
  - flow
  - review-loop
  - ci
  - logging
  - holon-agentic-coder
created_at: 2026-11-05T14:25:00Z
updated_at: 2026-11-20T14:05:06Z
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

## Audit (2026-11-20)

The code moved: the poll loop is now `flow/github/ci_wait.py:wait_for_pending_ci` and the tests are in
`tests/test_review_ci_wait.py`. Still logs "Waiting for N pending..." on every poll with no transitions or summary.

## Progress

- 2026-11-20: Started holon flow `review-report-ci-log-redaction` (claude-agent, claude-opus-5-5), combined with beans
  0261, 0213, 0234 and 0148.
- 2026-11-20: Flow `review-report-ci-log-redaction` finished all 5 stages: 3/3 consensus approval at review iteration 3,
  calibration report in the diff (EV predicted 39.45, actual 59.09, delta +19.64), final-head CI green. PR
  [#220](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/220) was merged by the maintainer at 14:03Z.

## Resolution

Delivered via [PR #220](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/220) and merged into `main`
(`9a5454bf`), as part of the combined flow `review-report-ci-log-redaction`:

- **Key Deliverables**: `flow/github/ci_wait.py:wait_for_pending_ci` tracks per-check state and logs only transitions
  (`CI check '<name>' completed (<state>) — N pending`), with one initial tracking announcement and one final summary.
  Quiet poll intervals emit nothing.
- **Verification & Tests**: `apps/sandbox-executor/tests/test_review_ci_wait.py` asserts transition log lines and no
  duplicate heartbeats on unchanged state.
- **Holon Flow Traversal**: Intent -> Plan -> Execute -> Review Loop -> Calibration completed (predicted EV 39.45,
  actual 59.09).
