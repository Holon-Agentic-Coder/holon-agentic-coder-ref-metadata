---
# holon-agentic-coder-ref-metadata-0630
title: "Holon flow self-recovers and auto-resumes broken stages instead of halting"
status: todo
type: feature
priority: high
tags:
  - flow
  - reliability
  - orchestration
  - holon-agentic-coder
created_at: 2026-11-27T11:53:10Z
updated_at: 2026-11-27T11:54:38Z
---

## Problem

When `holon flow` hits a recoverable mid-flow breakage (Stage 4 `touch_set_violation` stranding unpushed local commits,
transient infrastructure/DNS/proxy or `docker run` exit `125` glitches, intra-runner quota `exit 3`, stale superseded
`execution_branch` pointers on resume, or clean-tree/merge sync glitches), it halts with exit code `1` and stays idle
until an operator manually kicks off resumes or re-cuts the branch.

## Goal

Make `holon flow` classify recoverable mid-flow breakages and automatically clean or roll back stranded local state,
step down the intra-runner model ladder (or wait out a named reset), clear superseded execution-branch pointers when
resuming a newer plan, and auto-resume from the failed stage (up to a bounded recovery cap) until all 5 stages complete
— never bypassing Stage 4 review or advancing to Stage 5 on failure.

## Acceptance Criteria

- `holon flow` automatically recovers and resumes from recoverable stage breakages (cleaning stranded unpushed commits
  or stale superseded `execution_branch` refs before retrying) up to a bounded recovery cap.
- Unrecoverable failures halt fail-closed with a structured recovery diagnostic (`failure_class`, `checkpoint`,
  `resume_command`) and never bypass Stage 4 review or run Stage 5 calibration on an unapproved PR.
- Hermetic unit tests pass under `uv run pytest` covering automatic recovery/resume after a recoverable stage failure,
  stale `execution_branch` cleanup on resume, and fail-closed halt once the recovery budget is exhausted.

## Notes

- Maintainer directive (2026-11-27): until the flow engine self-recovers automatically, operators manually kick off
  resumes whenever a flow breaks until the whole 5-stage flow completes.
- Related: Beans `0424`, `0618`, `0624`, `0625`, `0396`, `0397`.

## Resolution
