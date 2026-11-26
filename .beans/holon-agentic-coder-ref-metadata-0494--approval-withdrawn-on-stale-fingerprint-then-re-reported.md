---
# holon-agentic-coder-ref-metadata-0494
title: "A fresh iteration-4 approval was withdrawn at the merged-head gate on a stale fingerprint and then re-reported"
status: todo
type: bug
priority: normal
tags:
  - flow
  - review
  - holon-agentic-coder
created_at: 2026-11-26T08:30:00Z
updated_at: 2026-11-26T08:30:00Z
---

## Problem

Flow for intent `timing-gate-runner-variance` (PR #321) re-ran from `--from-stage review` on head f79e57f7 (main merged
in). The review loop reached 3/3 approval at iteration 4 on head f2f0b8da, but the approval was posted through the
fallback review-comment path (HTTP 422 on self-approval), so its approval fingerprint was not refreshed. Stage 5's
merged-head gate then compared it with the fingerprint recorded for the older approval on 8cd7d557 and withdrew it:
"PR-own change changed since approval". The only later commits were ledger, KB and calibration files. The wrapper then
printed "Stage 4 approved (0/0/0)" four seconds later without a fresh review.

## Why it matters

The gate withdrew a valid approval, and the re-approval that followed came without evidence that the withdrawal was
resolved. The state is correct only because the PR-own diff after f2f0b8da is ledger/KB/calibration only, which was
checked by hand. A future run could take either path with no clear record of which approval covers the head.

## Next step

Record the approval fingerprint when a review is approved through the fallback comment path, and make the wrapper log
which approval (iteration, head, fingerprint) covers the final head. Check that a withdrawal followed by an immediate
approval does not reuse verdicts from before the withdrawal.
