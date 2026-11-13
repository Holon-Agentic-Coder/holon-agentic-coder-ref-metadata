---
# holon-agentic-coder-ref-metadata-0288
title:
  "Stage 4 posts a changes-requested review to the PR whenever the review loop exits, including when it halts without
  consensus"
status: completed
type: bug
priority: high
tags:
  - flow
  - review-loop
  - github
  - holon-agentic-coder
created_at: 2026-11-12T06:00:00Z
updated_at: 2026-11-12T06:00:00Z
---

## Problem

Intermediate review results must stay local until the ensemble approves (or the iteration cap is reached). On
holon-agentic-coder PR #175 (2026-11-12, flow `failnames`) the engine posted an "Ensemble Consensus Review - CHANGES
REQUESTED (Iteration 1) - 2/3 approved" to GitHub at 05:38:08Z, minutes after Stage 3, although the loop had not
converged and the Stage 4 resolver then halted on its pre-push gate. The posting is `post_pr_review_consensus()` in
`flow/review/loop.py` (around line 703). It runs at loop exit and is skipped only for a dry run, `--skip-post`, a
refused diff or host run, an infrastructure error, or no completed reviewer. A halt caused by a resolver error
(`resolver_error`) or by a stage that simply stopped short of consensus is not excluded, so a non-final,
changes-requested review reaches the PR thread. The same class has been raised before: the rule is that nothing is
posted until all findings are resolved or consensus is approved.

## Action

Run through the Holon flow. Post to GitHub only when the loop ends in a clean consensus approval or when the configured
iteration cap is reached with findings still open. Treat a resolver failure, a halted gate, a stage budget stop and any
other non-terminal exit as "no post" (log that nothing was posted and why), and keep the report local. Tests: a loop
that halts on a resolver error posts nothing; a clean approval posts once; the cap posts the changes-requested form
once; the posting ledger action (ACT-POST) is only written when a post was attempted. Keep exactly the three ledgers; no
new dependencies.

## Notes

Touches `flow/review/loop.py`, so it must not run concurrently with another flow on that file.

## Resolution

Delivered via [PR #177](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/177) and merged into `main`
(`89b2530`):

- **Fix**: the Stage 4 review loop posts its consensus review only on a clean approval or at the iteration cap. A
  resolver error, a failed gate, a budget stop or any other non-terminal exit posts nothing, logs why, and writes no
  `ACT-POST`.
- **Review**: 3/3 ensemble approval in 2 iterations with zero findings; one `COMMENTED` review on the PR and no
  premature changes-requested review. Final head CI green.
- **Calibration**: `plans/P-1794476365-334a8266-claude-agent-claude-sonnet-5-5_calibration.md` in the PR; EV predicted
  40.70 vs actual 52.47.
- **Flow**: all five stages traversed through `holon flow`, uninterrupted.
