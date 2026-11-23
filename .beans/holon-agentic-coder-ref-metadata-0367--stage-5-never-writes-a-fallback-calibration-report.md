---
# holon-agentic-coder-ref-metadata-0367
title: "Stage 5 never writes a fallback calibration report: retry, then fail the stage"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-5
  - calibration
  - holon-agentic-coder
created_at: 2026-11-23T05:50:00Z
updated_at: 2026-11-23T07:58:00Z
---

## Problem

When `run_calibrate` raises, `flow/stages/calibrate.py::_fallback_report` writes a stub report
(`# Calibration Report for <plan>\n\nFallback calibration generated.`), records an `outcome="failure"` ACT-CAL row, and
the stage still exits `status=success`. The flow logs `calibrate: ok` and finishes at the merge boundary as if Stage 5
had passed. A stub report carries no EV numbers, so it is not a calibration (maintainer, 2026-11-23: "there shouldn't be
a fallback calibration report; if the agent failed to generate one it should retry or stop").

Seen on PR #249 (2026-11-23 05:44:15Z, `todo/flow-remove-token-reduction-copy.log` lines 526–538): checkout of the
`/calibrated` branch failed with `fatal: gitfile does not point to a valid repository: holon-coherence/.git` (Bean
0368), the stub was written, and the run reported success. The real report on `main` came from a later hand re-run after
the gitfile was repaired.

## Goal

1. **No fallback report, ever.** Remove `_fallback_report` and the `on_calibrate_error` hook path in `flow/stage5.py`;
   the stub text and `fallback_report_written` disappear from `calibration.py::record_calibration_action`.
2. **Retry transient failures.** Retry `run_calibrate` a bounded number of times (agent/API errors, timeouts,
   named-reset usage limits waited out as elsewhere) before giving up.
3. **Otherwise fail the stage.** A non-retryable or exhausted failure returns `StageStatus.FAILED`: nothing is committed
   or pushed, the `/calibrated` branch is discarded if empty, the checkpoint stays at CALIBRATE so
   `--from-stage calibrate` resumes, and the run summary says `calibrate: failed` with the redacted cause. The failure
   ACT-CAL row is still appended to the ledger (append-only).
4. Tests: an exception with no retries left fails the stage and writes no report; a transient error retries and then
   succeeds; no code path writes "Fallback calibration generated".

## Touch set

`apps/sandbox-executor/src/sandbox_executor/flow/stages/calibrate.py`,
`apps/sandbox-executor/src/sandbox_executor/flow/stage5.py`,
`apps/sandbox-executor/src/sandbox_executor/calibration.py`, their tests (`tests/test_calibrate_*.py`,
`tests/test_stage5*.py`).
