---
# holon-agentic-coder-ref-metadata-0543
title: "Derive flow/lazy_exports.py from the flow modules instead of hand-editing a hub file"
status: todo
type: task
priority: high
tags:
  - flow
  - architecture
  - admission
  - holon-agentic-coder
created_at: 2026-11-26T21:10:00Z
updated_at: 2026-11-26T21:10:00Z
---

## Problem

`apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py` (188 lines, plus `lazy_exports_review.py` and
`lazy_exports_sync.py`) is a hand-written table "owning module -> exported names". Every flow that adds, renames or
moves a flow function must edit it, so it is a hub file that no intent scope can predict.

## Evidence (2026-11-26 13:40Z to 21:05Z audit window)

- 3 Stage 3 refusals name `lazy_exports.py` as the overlapping path on open PR #342 (13:18:56Z
  `module-budget-default-350`, 14:28:21Z `admission-remote-in-flight`, 14:50:04Z `single-runner-per-checkpoint`); a
  fourth, at 20:59:41Z, is against the parked `module-budget-default-350` flow. Those 3 flows parked for 7.7 h, 6.5 h
  and 6.2 h (13:18Z/14:28Z/14:50Z until PR #342 merged at 20:58Z), about 20 flow-hours, on this file (plus
  `docs/architecture.md` and `docs/git_flow.md` for two of them).
- Today's earlier logs show 4 more Stage 3 discards for the same file or its siblings being edited outside the plan's
  touch set (04:31Z, 05:13Z, 06:53Z, 14:47Z; "the execution changed N file(s) outside the plan's touch set ...
  lazy_exports.py"), each throwing away a finished execution (bean 0414) and forcing a re-plan.
- 9 flow logs under `todo/` mention the file; PR #342 and #283 and #263 touched it in the last four days.
- The table duplicates information the modules already hold (their public names / `__all__`), so a wrong or missing
  entry is only caught when the lazy `__getattr__` fails at import time.

## Proposed change

1. Generate the map: a deterministic script (and a unit test that fails on drift) builds `LAZY_EXPORTS` by scanning each
   `flow/*.py` module's `__all__` (or its public top-level names where `__all__` is absent), written into one generated
   file that is excluded from hand edits and from touch-set overlap (like a lockfile), or computed at import time from a
   committed one-line-per-module manifest that is itself regenerated, never edited by flows.
2. Add the generated file to the admission "mechanical paths" list so overlap on it never refuses a flow and the flow
   resolver regenerates it after a merge (it is a pure function of the tree).
3. Planner/executor: a flow that adds a flow function must not list the generated file in its touch set.

## Expected gain

Removes the most frequent hub overlap: about 20 parked flow-hours and 4 discarded executions in this window. Compatible
with beans 0379 and 0410 (architecture conflict magnets); extends 0410 rather than replacing it.

## Cost

One script, one test, a small import-time or generated file; low risk because the output is verifiable against the
current table byte for byte.

## Acceptance

- A test regenerates the map and asserts it equals the committed file; adding a function to a flow module without
  regenerating fails the test with the command to run.
- Admission ignores the generated file when computing overlap.
