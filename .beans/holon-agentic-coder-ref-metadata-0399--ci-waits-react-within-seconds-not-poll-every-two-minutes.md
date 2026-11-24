---
# holon-agentic-coder-ref-metadata-0399
title: "CI waits react within seconds of a check finishing instead of polling every two minutes"
status: in-progress
type: feature
priority: high
tags:
  - flow
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-24T11:34:00Z
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
