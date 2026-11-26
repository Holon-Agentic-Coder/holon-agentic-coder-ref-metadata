---
# holon-agentic-coder-ref-metadata-0398
title: "A flow blocked only by an approved pull request can start from that pull request's head"
status: draft
type: feature
priority: low
tags:
  - flow
  - stage-3
  - admission
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-25T05:45:00Z
---

## Problem

A flow that depends on, or overlaps, a pull request that is already approved and calibrated waits for the maintainer's
merge before it starts, although the code it needs is final in all but name.

## Goal (needs a maintainer decision before any work)

- Such a flow may take the approved pull request's head as its base, run all five stages, and open its own pull request
  stacked on the first.
- When the first pull request merges, the stacked one is retargeted to `main` and synced; if the first is changed or
  closed, the stacked flow is told at once and re-syncs or stops.

## Open questions

- Whether the maintainer wants stacked pull requests into `main` at all; review and merge order become coupled.
- Whether Bean 0395 (work during the overlap wait) already removes enough of the wait to make this unnecessary.

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24. Recorded as
  a draft: it changes what a flow's base is.
- Related: Bean 0266 (CI on pull requests into any branch).

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- 0371 (Claude Code) was refused at 05:32:48Z only because approved PR #305 (Antigravity, ready since 01:49Z) touches
  `flow/git_refs.py`. In the period, ready PRs waited a median of 335.7 min for the merge, and 8 approved self-doc
  slices (#300 to #307) held 8 to 15 files each while they waited.
