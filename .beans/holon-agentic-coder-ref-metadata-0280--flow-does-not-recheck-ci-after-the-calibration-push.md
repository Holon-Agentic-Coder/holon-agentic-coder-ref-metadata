---
# holon-agentic-coder-ref-metadata-0280
title: "The flow does not re-check CI after the calibration push; the macOS timing gate is flaky near 300 s"
status: todo
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
