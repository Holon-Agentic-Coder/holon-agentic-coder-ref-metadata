---
# holon-agentic-coder-ref-metadata-0425
title: "Review iterations on claude-fable-5-2 take three times as long as on claude-opus-5-5"
status: todo
type: task
priority: medium
tags:
  - flow
  - review
  - models
  - holon-agentic-coder
created_at: 2026-11-24T12:58:00Z
updated_at: 2026-11-24T12:58:00Z
---

## Problem

Since the flow model moved to `claude-fable-5-2` (2026-11-23), each Stage 4 review iteration (three reviewers in
parallel) takes about three times as long, and the number of iterations a flow needs has not fallen.

## Evidence (self-improvement audit, 2026-11-24T12:58Z, `todo/self-improvement-audit-2026-11-24b/`)

| Reviewer model     | Iterations measured | Median (min) | Longest (min) |
| :----------------- | ------------------: | -----------: | ------------: |
| `claude-opus-5-5`  |                  95 |          5.9 |          23.0 |
| `gemini-3.8-flash` |                  18 |          7.8 |          13.0 |
| `claude-fable-5-2` |                  14 |         18.4 |          28.0 |

- PR #272 (Bean 0403): iterations of 27.9, 26.1 and 25.5 minutes; iteration 3 had two approvals and one documentation
  nit, and the full ensemble ran again for a one-line fix (12:47:53Z).
- PR #270 (Bean 0387): six iterations of 14.8 to 26.6 minutes.
- Flows reviewed on Fable so far needed 1, 2, 6 and (still running) 5 or more iterations; the 21 Opus flows since
  2026-11-21 needed a median of 3. The sample is small, but Fable has not reduced the count.

At the overall mean of 4.7 iterations a flow (131 iterations in 28 logged flows), Fable reviewers add roughly 50 minutes
of Stage 4 time per flow.

## Proposal (needs the maintainer's word; the flow model is the maintainer's choice)

- Keep Fable for the first full review and run later passes, which only check a resolver's fix, on the next tier down or
  on one reviewer (Bean 0407 point 4 gives the scoped re-review this would use).
- Or give the review stage its own model setting (`--review-model`), so the executor stays on Fable.
- Measure for a week: iterations to consensus and defects found per iteration, by model.

## Notes

- Related: Bean 0407 (full re-review when nothing reviewable changed), Bean 0384 (stall budget cuts long-thinking
  models).
