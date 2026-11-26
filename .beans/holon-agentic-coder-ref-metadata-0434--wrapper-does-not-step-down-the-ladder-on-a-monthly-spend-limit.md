---
# holon-agentic-coder-ref-metadata-0434
title: "The flow wrapper does not step down the model ladder on a monthly spend limit"
status: completed
type: bug
priority: high
tags:
  - harness
  - wrapper
  - flow
  - quota
created_at: 2026-11-24T20:50:00Z
updated_at: 2026-11-25T05:30:00Z
---

## Problem

On 2026-11-24 the flow of Bean 0405 (pull request #275) stopped in Stage 4: every reviewer on `claude-agent` /
`claude-fable-5-2` exited 1 with "You've hit your monthly spend limit. Switch to another model to continue." The review
loop ran to its iteration cap with the ensemble FAILED and the wrapper exited 1, leaving the flow stopped until the
maintainer intervened.

The skill's rule for a limit that names no reset time is to step down the ladder on the same runner (`claude-fable-5-2`
then `claude-opus-5-5`). `run_holon_flow.py` has that ladder (`FALLBACK_LADDER_CLAUDE`, `resolve_next_model`), but
`is_quota_error` only matches `QUOTA_ERROR_PATTERNS` ("hit your session limit", "hit your usage limit", "hit your
limit", "quota exceeded" and similar). "hit your monthly spend limit" matches none of them, so the wrapper treated the
run as an ordinary failure and stopped instead of stepping down.

## Goal

- `QUOTA_ERROR_PATTERNS` recognises a spend limit ("spend limit", "hit your monthly spend limit") and the wrapper steps
  down to the next model on the same runner and resumes from the checkpoint; a test replays the exact message.
- A spend limit that names a reset time is waited out like any named reset.
- The engine's review loop does not spend all its iterations on a limit error: a reviewer that exits with a quota or
  spend message ends the stage at once with that reason (fail early), so the wrapper can act on it.

## Notes

- Resolved by hand on 2026-11-24 at about 20:47Z: the maintainer switched the session to Opus 5.5 and the flow was
  resumed from review on `claude-opus-5-5`.
- Related: Bean 0416 (quota reset parsing in the wrapper), Bean 0425 (review on Fable is three times slower than on
  Opus).

## Resolution

Added "monthly spend limit" and "spend limit" to `QUOTA_ERROR_PATTERNS` (tail-only scan unchanged). A spend limit with
no reset time steps down the Claude ladder on the same runner and resumes from the checkpoint; one that names a reset
time (for example "Resets in 51m58s") is waited out on the same model. Tests in `tests/test_flow_completion.py` replay
the exact message. Not done: the engine-side fail-early of the review loop (a target-repository change, outside this
harness-only fix). Full suite: 179 passed.
