---
# holon-agentic-coder-ref-metadata-0520
title: "Stage 3 admission blocks on shared file paths, not on a real merge conflict; one open PR parks several flows"
status: todo
type: feature
priority: high
tags:
  - flow
  - admission
  - coordination
  - holon-agentic-coder
created_at: 2026-11-26T13:40:00Z
updated_at: 2026-11-26T13:40:00Z
---

## Evidence

Self-improvement audit 2026-11-26T13:40Z, question (1).

- `module-budget-default-350` (bean 0489) was refused at 13:18:56Z because its touch set overlaps open PR #342
  (`ledgers-sorted-chronologically`, 34 files, open since 12:19Z, 79 min) on `flow/lazy_exports.py` and
  `docs/architecture.md`. Both are registry or prose hubs where two flows usually add different lines.
- `single-runner-per-checkpoint` (beans 0390/0472) was parked three times on 11-26: 09:35Z behind
  `tests-fewer-git-stage-pipeline` on `tests/flow/conftest.py`, 10:56Z behind PR #334 on the same `conftest.py`, and
  13:04Z behind the older waiting flow `split-calibration-package`, which is itself parked. Each refusal ends the run
  and needs a manual relaunch with `--checkpoint` (bean 0476 stopped the polling).
- Admission compares path sets, so one wide PR (#342 touches the three ledgers, 4 flow modules, 3 docs) blocks every
  flow that shares even one hub path, whether or not the edits could conflict. Beans 0481 (pre-launch check), 0337
  (waiting flows block each other, completed), 0410 (hand-edited conflict magnets) and 0519 (stale refs) do not change
  this.

## Proposed change

1. Replace "paths overlap" with a trial merge: for each overlapping flow or open PR, run `git merge-tree --write-tree`
   of the candidate execution base against that PR head (after `git fetch --prune`). Refuse only on a real conflict; log
   the conflicting hunks. Overlap on a path that merges clean is admitted and logged.
2. Keep the path-set check as the cheap pre-filter and as the answer when the trial merge cannot run.
3. Let the planner shrink the touch set: split hub edits (`lazy_exports.py`, `docs/architecture.md`, `conftest.py`) into
   a final small step or out of the plan when the intent does not need them (relates to 0502, 0508).
4. A small PR should not wait on a wide one: when the blocker is an open PR older than the candidate, report its age and
   size in the refusal so the maintainer can order merges (merge #342 first, or split it).

## Expected gain

Admission and overlap waits were 343 of 3260 flow-minutes in the 11-26 time audit (worst 300 min). A trial merge turns
the hub-file refusals (3 of the 4 refusals above) into admissions. Cost: one `merge-tree` per candidate, no worktree.

## Notes

Related: 0481, 0519, 0410, 0502, 0508, 0151. The `conftest.py` split in the question is already the shape of 0410; this
bean makes the engine stop needing it first.
