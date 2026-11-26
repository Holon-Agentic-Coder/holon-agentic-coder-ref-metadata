---
# holon-agentic-coder-ref-metadata-0481
title:
  "A flow whose intent scope overlaps a flow in flight is launched anyway and holds a concurrency slot while it waits"
status: todo
type: feature
priority: high
tags:
  - flow
  - harness
  - coordination
  - admission
  - holon-agentic-coder
created_at: 2026-11-26T05:25:00Z
updated_at: 2026-11-26T05:25:00Z
---

## Problem

The harness backfills up to four concurrent flows (`.agents/coordination.md`, 4-flow cap, "honouring ... disjoint touch
sets (`run_holon_flow.py` waits out Stage 3 overlaps automatically)"). In practice disjointness is only checked by the
engine at Stage 3, after intent and plan have run, so a bean whose scope overlaps a flow in flight is started, plans,
and then occupies one of the four slots for hours while a disjoint ready bean waits.

## Evidence

Evidence: flow time audit of 2026-11-26 (git-ignored `todo/flow-time-audit-2026-11-26.md`, scripts and data in
`todo/flow-time-audit-2026-11-26/`), sample PRs #296 to #316 of holon-agentic-coder.

- `macos-unit-only-when-relevant` (PR #315) planned at 2026-11-25 22:57-23:02Z, then waited at Stage 3 from 23:02:29Z to
  04:02:54Z (**300 min**, about 217 refused relaunches) behind the local flow `ledger-fragments-and-promotion`, mostly
  on `.github/workflows/README.md` (one stretch on `tests/test_ci_bookkeeping_wiring.py`).
- Live on 2026-11-26: `flow-references-github-issues` and `split-calibration-package` both wait at Stage 3 behind the
  local flow `no-unneeded-full-review` (calibration.py, flow/context.py); the first has waited 56+ min so far, the
  second restarted from intent four times (Bean 0477).
- Admission and overlap waits are 343 of 3260 measured flow-minutes in the sample (p90 per flow 52 min, worst 300 min).

## Proposed change

1. Before launching a bean, the harness compares the intent's `scope` files with the touch sets of the flows in flight
   (their plan files and checkpoints) and with the files of open flow PRs; an overlapping bean is not launched while a
   disjoint ready bean exists.
2. A flow that is refused at Stage 3 releases its slot: it is parked (checkpoint kept, no wrapper process) and
   relaunched from its checkpoint when the blocker merges; the freed slot backfills with the next disjoint bean.
3. The triage matrix shows parked flows and what blocks them.

## Expected gain

The 4 slots stay busy with work that can progress; in this sample about 5 h of one slot (PR #315) and about 1 h each of
two slots now. Does not shorten an individual flow; raises throughput.

## Cost

Small to medium in `run_holon_flow.py` and the backfill step of `post-pr-merge`/coordination rules.

## Notes

- Related: Bean 0395 (do useful work during the overlap wait), Bean 0410 (generated README files as conflict magnets:
  the #315 wait was mostly on one), Bean 0463 (directory touch sets widen overlap), Bean 0476 (overlap poll relaunches
  every minute), Bean 0477 (relaunch after overlap exit restarts from intent), Bean 0423 (shared flow registry).
