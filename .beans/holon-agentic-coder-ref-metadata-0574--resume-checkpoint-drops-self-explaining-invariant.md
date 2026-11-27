---
# holon-agentic-coder-ref-metadata-0574
title: "Flow resumed from a checkpoint whose intent lacks the self-explaining-code invariant"
status: in-progress
type: bug
priority: high
tags:
  - harness
  - holon-flow
created_at: 2026-11-26T22:10:00Z
updated_at: 2026-11-27T00:12:19Z
---

## Problem

Bean 0491 resumed `flow-flow-fixtures-any-test-file` from its checkpoint. The checkpoint's `context.intent_data.goal`
predates the self-explaining-code invariant (maintainer, 2026-11-27), so the checkpoint carries no invariant. The
resumed Stage 3 executor (E-1795733989-CLA-CO5.5, pushed to
`I-1795699916-flow-fixtures-any-test-file/P-1795699971-CLA-CO5.5/E-1795733989-CLA-CO5.5/_`) added docstrings to
`apps/sandbox-executor/tests/conftest.py` and to the new regression test, and a block string after code. The intent copy
in `todo/intent-0491-flow-fixtures-any-test-file-subset.json` was patched with the invariant, but the checkpoint still
holds the old goal.

## Why it matters

Every intent must keep the self-explaining-code invariant. A resumed flow that reads its goal from the checkpoint
silently drops it, and the review loop judges the diff against that goal.

## Next step

Make the resume path take the invariant from the intent file (or re-stamp the checkpoint goal) before a checkpoint
resume, and check the executor output for docstrings. Fix the 0491 flow's diff through the flow, not by hand.

## Note (2026-11-26T23:25:08Z)

The checkpoint holds the intent goal in two places: `context.intent_data.goal` and
`context.stage_results.intent.payload.intent.goal`. A fix must refresh both (or derive one from the other) when a resume
re-reads the intent file. Seen on the 2026-11-26 resume of the subset-fixture flow (PR #358), which merged with three
docstrings and a `#:` comment because the resumed run used the pre-invariant goal.

## Note (2026-11-27T00:12:19Z): partial delivery by PR #361

PR #361 (merged 2026-11-27T00:05:38Z; consensus 3/3, calibration in the PR diff) delivered `intent_refresh.py`
`refresh_intent_text`. It refreshes `context.intent_data` from the intent file and refuses a goal without the
self-explaining-code sentence, but it does not touch the second copy,
`context.stage_results.intent.payload.intent.goal`. A resume can therefore still run stages against the stale goal. This
bean stays `in-progress`.

Remaining: refresh (or derive) `context.stage_results.intent.payload.intent.goal` in the same resume path, with a test
on a checkpoint whose stage_results goal lacks the sentence.

Follow-up: to be queued with the slot keeper; not yet queued at the time of this note.
