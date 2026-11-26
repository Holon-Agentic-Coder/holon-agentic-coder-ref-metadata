---
# holon-agentic-coder-ref-metadata-0400
title: "Shorten the CI pipeline: the slowest jobs set every wait in the flow"
status: in-progress
type: task
priority: normal
tags:
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-25T23:05:00Z
---

## Problem

Every flow waits for the pipeline at least twice. Over 33 measured waits the median was 7.9 minutes and the longest 11.9
minutes. The checks that finish last are `Workspace survival (ubuntu-latest)` and `unit (macos-latest)`.

## Goal

- Measure each job's queue time and run time (Bean 0166 has the dashboard) and name the two that set the total.
- Bring the pipeline's wall-clock time down: dependency and image caching, sharding the unit suite, running the macOS
  unit job only for changes that can behave differently there, moving `Workspace survival` off the critical path if it
  cannot be made faster.
- Fail fast inside the pipeline: `fail-fast` is `false` on the unit, make and integration matrices today, so a failed
  leg lets its sibling run to the end. Decide per workflow whether that is still wanted. (Superseded runs are already
  cancelled on pull requests.)

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Related: Bean 0168 (unit suite runs 1.7x slower on macOS), Bean 0166 (pipeline duration dashboard), Bean 0300 (CI runs
  once per change).
- No target is set here; the first step is the measurement.

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- Measured after #275 and #278 (74 PR heads, 00:33Z to 05:30Z,
  `todo/self-improvement-audit-2026-11-25a/pipeline-fixes.md`): full pipeline wall median 7.6 min, p90 8.7 min, down
  from 10.8 / 24.2 min before #272. Bookkeeping heads are gated to 0.9 min.
- The critical path is now `unit (macos-latest)`: median 7.0 min, longest 9.5 min, against 3.2 min for
  `unit (ubuntu-latest)` on the same heads. `Test - Stress` (Workspace survival) is second at 6.3 min. Running the macOS
  leg only for changes that can behave differently there would take about 3 min off every code and main-merge head.
- Main-merge heads now cost more than code heads: 28 of 78 heads in the period, 409 runner-min, against 167 runner-min
  for the 13 code heads (see Bean 0458 for the hand syncs behind most of them).

## Progress

- In progress, 2026-11-25: holon flow `macos-unit-only-when-relevant` (scope: the macOS leg only, the
  `unit (macos-latest)` relevance gate), run by `run_holon_flow.py` with claude-agent / claude-opus-5-5 in worktree
  `flow-macos-unit-only-when-relevant`, log `todo/flow-macos-unit-only-when-relevant.log`.
- Stage 1 and Stage 2 done (plan P-1795647426-CLA-CO5.5, EV 34.1). Stage 3 refused for a touch-set overlap with the
  local flow `intent-0371-ledger-fragments-and-promotion` on `.github/workflows/README.md`; the wrapper exited instead
  of waiting (Bean 0468). Resume from the checkpoint once that flow finishes; no `--allow-overlap`.
- 2026-11-25 23:33Z: flow parked at Stage 3 admission. Overlap with `intent-0371-ledger-fragments-and-promotion` (PR
  #310, open, MERGEABLE) on `.github/workflows/README.md`. No `--allow-overlap`. Resume from
  `/Users/thomashan/git/holon-agentic-coder-ref-metadata/apps/holon-agentic-coder/flow-macos-unit-only-when-relevant/.holon/flow/checkpoint-macos-unit-only-when-relevant.json`
  after #310 merges (see Bean 0468 for the wrapper's missing overlap wait).
