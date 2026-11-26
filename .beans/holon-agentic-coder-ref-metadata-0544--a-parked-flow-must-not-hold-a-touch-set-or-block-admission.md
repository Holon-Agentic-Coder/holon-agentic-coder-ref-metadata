---
# holon-agentic-coder-ref-metadata-0544
title: "A parked flow holds no touch set: admission blocks only on open PRs and running flows"
status: todo
type: task
priority: high
tags:
  - flow
  - admission
  - stage-3
  - holon-agentic-coder
created_at: 2026-11-26T21:10:00Z
updated_at: 2026-11-26T21:10:00Z
---

## Problem

Stage 3 admission refuses a candidate when its touch set overlaps an "older waiting flow", even when that flow is parked
(refused, process gone, worktree idle). A parked flow does no work and writes nothing, yet blocks younger flows, so
parks chain: the oldest parked flow holds the others.

## Evidence

- `admission-remote-in-flight` (0519) at 20:59:41Z: "overlaps an older waiting flow ...
  `flow-module-budget-default-350`, blocked since 2026-11-26T13:18:56Z" on `lazy_exports.py`, i.e. behind a flow that
  was itself parked since 13:18Z.
- `single-runner-per-checkpoint` at 13:04:41Z: refused behind parked `split-calibration-package`.
- `module-budget-default-350` at 21:04:46Z: after PR #349 merged and it resumed, it refused again on the running
  `single-runner-per-checkpoint` ("local flow"), which in turn waited on #342 at 14:50Z. Three flows form a chain in
  which each is parked behind a flow that is parked or has only just resumed.
- Aggregate park time on 11-26: `module-budget-default-350` 7.7 h, `flow-references-github-issues` 7.5 h,
  `admission-remote-in-flight` 6.5 h, `single-runner-per-checkpoint` 6.2 h plus 1.4 h earlier, about 29 flow-hours. All
  four parked on the same wide PR #342 (open from before 13:18Z to 20:58Z), then resumed together at 21:00Z.

## Proposed change

- A parked flow releases its touch set: admission counts only (a) open PRs and (b) flows with a live runner process.
- Order parked flows by their original admission order and let the first resume claim the set on resume (the resume
  re-runs admission), so no deadlock cycle can form.
- A trial merge, not path overlap (bean 0520), stays the preferred fix for the PR case; this bean is the cheaper first
  step for the parked-flow case and is needed even after 0520 because two ready flows that really conflict still need
  one winner.

## Expected gain

Cuts the chain waits of the 4 flows above (about 29 flow-hours of parked slots, of which at least the last-stage waits
behind other parked flows disappear).

## Cost

Admission change in `flow/admission*.py` plus tests; touches the area of beans 0520 and 0523, so run it sequentially
with them.

## Acceptance

- A test: candidate overlapping a parked (no live runner) flow is admitted.
- A test: two parked flows resuming at once admit exactly one, the other refuses with a named live blocker.
