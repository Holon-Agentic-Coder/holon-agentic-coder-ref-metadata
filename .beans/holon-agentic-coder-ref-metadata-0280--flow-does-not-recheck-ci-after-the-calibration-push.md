---
# holon-agentic-coder-ref-metadata-0280
title: "The flow does not re-check CI after the calibration push; the macOS timing gate is flaky near 300 s"
status: completed
type: bug
priority: normal
tags:
  - flow
  - ci
  - calibration
  - holon-agentic-coder
created_at: 2026-11-12T09:00:00Z
updated_at: 2026-11-12T09:00:00Z
---

## Problem

Stage 5 pushes calibration commits after the review loop has checked CI, which re-triggers CI on a head the reviewers
did not vote on. On PR #164 the post-calibration run failed only in `unit (macos-latest)`'s "CI Timing Gate (Check <= 5
min)" (313.1 s against 300 s) while all 3,594 tests passed, after the review had said "CI passing". The same job passed
in the earlier run. Nothing in the flow notices a CI result on the final head.

## Action

Run through the Holon flow. After calibration is pushed, wait for CI on the final head (not a polling loop typed into a
shell: the shared wait primitive), report a failure with the failed check names, and distinguish a timing-gate failure
from a test failure. Separately decide whether the 300 s gate needs headroom or a rerun policy (a bean-level decision
for the maintainer, not changed here).

## Resolution

Delivered via [PR #173](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/173) and merged into `main`
(`37c59e5`):

- **Fix**: Stage 5 now reports CI on the final head after the calibration push, so the flow no longer leaves a PR whose
  last commits were never checked.
- **Review**: 3/3 ensemble consensus approval. The resume ran iteration 3 and the resolver applied one documentation
  Nit. Its pre-push gate (`uv run task lint` and `uv run task test`) passed in the review container for the first time,
  after Beans 0285 and 0289. Calibration head `a4cd36d`; all 11 CI checks green.
- **Calibration**: `plans/P-1794456566-07246b8e-claude-agent-claude-sonnet-5-5_calibration.md` in the PR; EV predicted
  36.39 vs actual -14.80.
- **Flow**: all five stages traversed through `holon flow`. The macOS timing-gate half of the title was not addressed by
  this PR.
