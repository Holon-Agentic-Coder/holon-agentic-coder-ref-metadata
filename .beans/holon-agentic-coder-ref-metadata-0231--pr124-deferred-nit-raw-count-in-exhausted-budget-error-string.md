---
# holon-agentic-coder-ref-metadata-0231
title: "PR #124 deferred nit: exhausted-budget error string interpolates raw (possibly negative) review_iterations_done"
status: todo
type: task
priority: low
tags:
  - holon-agentic-coder
  - pr124
  - deferred-findings
  - review-loop
created_at: 2026-11-05T06:55:05Z
updated_at: 2026-11-05T06:55:05Z
---

Deferral bean for the PR #124 review loop (Bean 0170 convergence rule 1: nits on code the increment did not change are
deferred, not fixed mid-loop).

## Deferred finding

- **D4-F1 (nit, cosmetic)** — `apps/sandbox-executor/src/sandbox_executor/flow.py:~4300-4304` (exhausted-engine-budget
  path in `_run_engine_review_loop`): the error message interpolates the raw `context.review_iterations_done`, so a
  malformed checkpoint (negative count) logs "exhausted after -2 iteration(s)" while the synthetic consensus payload
  reports the clamped 0 (`first_label - 1`). Fix: interpolate the clamped value in the message too.
- Flagged independently by all 3 ensemble reviewers at iteration 4, head `5e23608`, as an out-of-increment deferral
  candidate (reports: `.subagent/holon-agentic-coder_pr124_ensemble_review_iter_4_reviewer_{1,2,3}_5e23608.md`).
- Disposition: `rejected: deferred: unchanged code -> 0231`. Cosmetic log-text inconsistency only; no behavioural
  impact.

## Notes

- Target: holon-agentic-coder (via a future Holon flow intent, never hand-edited).
