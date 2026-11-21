---
# holon-agentic-coder-ref-metadata-0347
title:
  "Stage 4 reports 'halted for human review' after consensus approval although the flow continues and the PR is ready to
  merge"
status: todo
type: bug
priority: normal
tags:
  - flow
  - stage-4
  - review-loop
  - reporting
  - holon-agentic-coder
created_at: 2026-11-21T01:20:00+11:00
updated_at: 2026-11-21T01:20:00+11:00
---

## Problem

When the Stage 4 ensemble reaches consensus approval, the flow carries on to Stage 5 (calibration) and ends with a pull
request that is approved and ready for the maintainer to merge. The output says the opposite:

- the log prints `[SAFETY HALT] ... Pipeline halted for human review` (`flow/stages/review.py` around lines 282-295,
  also `flow/review/cli.py` lines 77-78, `entrypoint/review_loop.py` lines 914-915 and `cli/commands/flow.py` lines
  336-337);
- the stage summary shows `review: halted` (`StageStatus.HALTED_FOR_HUMAN` and its label in `flow/context.py`), and the
  review loop payload and ledger summary carry `status=halted_for_human` and `halted_for_human: true`
  (`flow/review/loop.py` around lines 810 and 877).

Nothing halts: the stage succeeded. The wording suggests the flow stopped for a human decision, which hides the real
state: approved, calibrated, waiting only for the maintainer's merge (a rule, not a halt).

## Action

Through the Holon flow on `holon-agentic-coder`:

- Name the outcome for what it is: the log line and stage summary say approved and ready for maintainer merge (for
  example `review: approved`), not halted. A real halt (a failed gate, a budget stop, no consensus) keeps the halt
  wording.
- Use a status that says approved/ready for merge instead of `halted_for_human`. Readers of existing rows must keep
  working: `calibration_outcome.py` and `flow/checkpoint.py` and `flow/stages/children.py` accept the old
  `halted_for_human` value in historical ledger rows and checkpoints, and treat the new value as converged.
- Update the docstring in `flow/stages/review.py` ("halts unconditionally with status HALTED_FOR_HUMAN") and the flow
  docs.
- Tests: a consensus approval logs the approved wording and shows no `SAFETY HALT`; a real halt still does; old
  checkpoints and ledger rows with `halted_for_human` still resume and calibrate.

## Notes

- Keep exactly the three ledgers; rows stay append-only, so the old value is never rewritten.
- Touches `entrypoint/review_loop.py`, which open PR #219 edits slightly; start after it merges. Overlaps Bean 0345 and
  0192 on `flow/review/loop.py`.
- Related: Bean 0288 (posting only on a terminal exit), which this bean complements but does not reopen.
