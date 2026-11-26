---
# holon-agentic-coder-ref-metadata-0401
title: "The CI registration wait ends unknown when the pull request head lags the pushed head"
status: todo
type: bug
priority: normal
tags:
  - flow
  - ci
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-24T08:30:00Z
---

## Problem

After Stage 5 pushes, the final-head check waits up to 180 s for the pull request to show the pushed commit and for
checks to register. Twice on 2026-11-23 it gave up with "final head CI: unknown (the PR head did not match the pushed
head before the registration wait ran out)", so the flow finished with CI on its final head not verified, after waiting
three minutes for nothing.

## Goal

- The check waits for the pushed commit itself (the commit's check runs), not for the pull request object to catch up,
  so a lagging pull request head does not hide checks that are already running.
- When registration truly has not happened, one retry with a fresh read before reporting unknown; the report says which
  of the two it was.
- An unknown result is treated as a failure to verify and reported at once (fail early), not folded into a success.

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Code: `flow/github/ci_final_head.py`, `flow/github/ci.py` (`CI_REGISTRATION_TIMEOUT_SECONDS = 180`,
  `CI_REGISTRATION_POLL_SECONDS = 15`).
