---
# holon-agentic-coder-ref-metadata-0401
title: "The CI registration wait ends unknown when the pull request head lags the pushed head"
status: completed
type: bug
priority: normal
tags:
  - flow
  - ci
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-26T12:10:00Z
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

## Progress

- 2026-11-26: flow ci-final-head-wait-on-pushed-commit launched (intent
  todo/intent-0401-ci-final-head-wait-on-pushed-commit.json, log todo/flow-ci-final-head-wait-on-pushed-commit.log).
- 2026-11-26: PR #335 open, review approved 3/3, Stage 5 calibration included, MERGEABLE/CLEAN; awaiting maintainer
  merge.

## Resolution

Delivered via [PR #335](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/335) and merged into `main`
(`f0d6c56d`):

- **Key Architectural Deliverables**: the final-head check in `flow/github/ci_final_head.py` probes the check runs of
  the pushed commit itself instead of waiting for the pull request head to catch up. When no checks have registered, it
  retries once with a fresh read; the unknown reason names which case occurred. An unknown result is reported at once as
  a failure to verify.
- **Verification & Tests**: `tests/flow/github/test_ci_final_head_registration.py`,
  `tests/test_calibrate_final_head_ci.py`.
- **Holon Flow Traversal**: flow `ci-final-head-wait-on-pushed` completed all 5 stages (review 3/3 approved, calibration
  included). Flow worktree and its `I-*` branches removed locally and on origin.
- **Follow-up**: `ci_final_head.py` is 368 lines on `main`, over the 350 step-2 budget; bean 0489 records it.
