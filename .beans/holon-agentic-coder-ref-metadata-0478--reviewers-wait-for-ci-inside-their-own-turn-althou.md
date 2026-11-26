---
# holon-agentic-coder-ref-metadata-0478
title: "Reviewers wait for CI inside their own turn although the engine already gates on CI"
status: todo
type: bug
priority: normal
tags:
  - flow
  - stage-4
  - review
  - ci
  - holon-agentic-coder
created_at: 2026-11-26T05:25:00Z
updated_at: 2026-11-26T05:25:00Z
---

## Problem

The reviewer prompt makes each of the three reviewers verify CI before approving:
`holon-config/prompts/review_loop.template.md:19` ("every CI check passes (`gh pr checks` or the local test suite"). The
engine already owns that gate after the reviewers return (`flow/review/loop.py:388-410`: registration wait, then
`settle_pending_ci`). So on every approving iteration the three reviewer sessions sit in their turn until the pipeline
on the head finishes.

## Evidence

Evidence: flow time audit of 2026-11-26 (git-ignored `todo/flow-time-audit-2026-11-26.md`, scripts and data in
`todo/flow-time-audit-2026-11-26/`), sample PRs #296 to #316 of holon-agentic-coder.

- On all 11 approving iterations in the sample the ensemble container returned 2 to 30 s after the last CI job on the
  reviewed head finished (for example #311 01:59:49 vs CI end 01:59:32; #313 03:28:22 vs 03:28:15; #314 03:58:33 vs
  03:58:31; #309 05:57:32 vs 05:57:26; #316 04:55:56 vs CI end on its head).
- Approving iterations take 6.5 to 10.3 min; blocked iterations of the same flows take 2.8 to 4.8 min (median 3.9 min).
  The difference (median 5.8 min per flow, 58 min over 9 flows) is three agent sessions idling on CI.
- The engine's own CI wait right after them settles in 1 to 3 s, because the reviewers already waited.
- In #308 four blocked iterations carried a reviewer "CI role CHANGES" vote while CI was still pending or the host test
  run (`review_local`) had failed, so the reviewer-side CI check also produces blockers on CI noise the engine gate
  already handles.

## Proposed change

1. Reviewers judge the diff only: drop the CI clause from the reviewer approval rule and the CI role from the reviewer
   verdict; the engine's post-review CI gate stays the single CI authority (it already withdraws consensus on a red
   head).
2. Pass the current CI state to reviewers as information only (a failing check's log excerpt is still useful context).
3. Optionally start Stage 5 preparation (calibration report generation) while the engine waits on the final head's CI.

## Expected gain

About 5.8 min x 3 agent sessions (about 17 agent-minutes) per flow, fewer quota stops (limit waits are flow time), and
no blocked iterations from a reviewer's CI vote. Wall time per flow changes little (the CI gate still bounds the
approving iteration) unless point 3 is done.

## Cost

Small: prompt change and verdict parsing in the review container; tests for the verdict.

## Notes

- Related: Bean 0407 (review rerun only when the reviewable diff changes), Bean 0400 (shorter pipeline sets the
  approving iteration), Bean 0450 (`review_local` host runs).
