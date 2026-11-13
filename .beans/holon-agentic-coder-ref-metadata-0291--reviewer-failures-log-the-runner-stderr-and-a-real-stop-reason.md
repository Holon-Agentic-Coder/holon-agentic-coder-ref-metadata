---
# holon-agentic-coder-ref-metadata-0291
title: "A failed Stage 4 reviewer logs its runner stderr and a real stop reason, not 'unknown'"
status: completed
type: bug
priority: high
tags:
  - review-loop
  - diagnostics
  - holon-agentic-coder
created_at: 2026-11-12T22:00:00Z
updated_at: 2026-11-13T00:20:00Z
---

## Problem

When a reviewer process exits non-zero without writing a usable report, `_log_turn_completion` in `review_ensemble.py`
logs only `Reviewer agent command failed with code 1 (stop reason: unknown).` The runner's stderr and any authentication
or quota message are dropped, so a missing credential, an expired token and a rate limit look identical. Diagnosing the
`ids` flow (PR #169) took several launches and host-side reproductions for what was a missing credential route.

## Goal

1. On a failed reviewer turn, log a bounded, redacted excerpt of the runner's stderr and last output (credentials and
   `sk-ant-` strings redacted) and include it in the ensemble result and the flow summary.
2. Classify the common causes into a stop reason that names them: authentication, quota or rate limit (with the reset
   time when the message gives one), timeout, and other; `unknown` only when nothing is recoverable.
3. A quota message that names a reset time reaches the flow's existing wait-out-the-reset handling instead of a generic
   failure.
4. Hermetic tests with fake runner output for each class; no new dependencies; `uv run pytest`, `uv run task lint` and
   `uv run task lint-docs` pass.

## Notes

- Target repository change in `holon-agentic-coder`: deliver through the 5-stage Holon flow. The intent JSON must not
  mention bean ids or harness paths.
- Touches `review_ensemble.py` and the turn result types; do not run beside another flow editing the review loop (for
  example PR #169).
- Related: Bean 0290; Bean 0258 (resolver failure handling).

## Resolution (completed, 2026-11-13)

Delivered by flow `revlog` as holon-agentic-coder PR #181, merged 2026-11-13T00:08:12Z (merge commit `e71beb1`, review
`PRR_kwDORMmd1c8AAAABXq6qSQ`). Calibration report
`plans/P-1794523633-edd36e36-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
+15.58 (actual 50.78). The PR needed a conflict merge with `origin/main` (ledgers and the failure-modes index) after PR
#180 landed first.
