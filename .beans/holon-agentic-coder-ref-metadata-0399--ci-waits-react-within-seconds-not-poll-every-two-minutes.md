---
# holon-agentic-coder-ref-metadata-0399
title: "CI waits react within seconds of a check finishing instead of polling every two minutes"
status: completed
type: feature
priority: high
tags:
  - flow
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-25T00:20:30Z
---

## Problem

`wait_for_pending_ci` doubles its poll interval up to `CI_WAIT_POLL_CEILING_SECONDS = 120`. Once a wait has run a few
minutes the engine looks at CI once every two minutes, so it can idle up to two minutes after the pipeline has finished
or a check has failed. The flow logs show check results arriving in two-minute steps (for example 08:02:44, 08:04:45,
08:06:47, 08:08:48 on 2026-11-21). A flow has two or three such waits. The Stage 3 overlap wait in the wrapper polls
every 60 s in the same way.

## Goal

- The engine learns of a finished or failed check within about 15 seconds: cap the backoff at 15 s now, and use the pull
  request event stream when it is available (Bean 0352).
- A failed check ends the wait at once (fail early); this already holds in the review loop and must hold in the
  merged-head gate and the final-head check too.
- The overlap wait in the wrapper wakes on the merge event, with the 60 s poll kept as the fallback.

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Small engine change (`flow/github/ci_wait.py`, `flow/github/ci_final_head.py`); the event stream is Bean 0352.
- Watch the GitHub API rate limit when lowering the cap; one checks call every 15 s per flow is well inside it.

> 2026-11-24: launched `ci-wait-fast-poll-and-early-fail` (intent
> `todo/intent-0399-ci-wait-fast-poll-and-early-fail.json`) via `antigravity-agent` / `gemini-4-neon`.

## Resolution

Delivered via [PR #277](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/277) and merged into `main`
(`29e28f52cf1e6c7a77411dcfc67f18038f7aeabc`, `2026-11-25T00:18:17Z`):

- **Fast 15 s CI Poll Backoff Cap**: Lowered `CI_WAIT_POLL_CEILING_SECONDS` from `120.0` to `15.0` in
  `sandbox_executor/flow/github/ci_wait.py` and clamped initial poll intervals to `policy.ceiling` in both
  `wait_for_pending_ci` and `merged_head_gate._poll_head`.
- **Consistent Fail-Early CI Waits**: Enabled `stop_on_failure=True` (default) in `ci_final_head._settled_status` and
  guarded `_eligible_run_ids` when checks remain pending, matching the review-loop and merged-head gates.
- **Verification & Follow-up**: Expanded hermetic unit tests in `test_review_ci_wait.py`, `test_merged_head_ci_gate.py`,
  and `test_calibrate_final_head_ci.py` across the 5-stage Holon flow. Follow-up event-stream / `gh webhook forward`
  subscription remains tracked under Bean `0352`.
