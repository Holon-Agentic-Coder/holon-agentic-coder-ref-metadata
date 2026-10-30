---
# holon-agentic-coder-ref-metadata-0192
title: "Decompose run_review_loop and run_review_stage into a ReviewLoop object with named steps"
status: todo
type: task
priority: high
tags:
  - refactor
  - complexity
  - review-loop
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0191
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. `run_review_loop` (`993b686`) is **528 lines, CC 131**, the most complex function after the two
`main`s; `run_review_stage` is 258 lines, CC 36. Both were the most-collided functions in `flow.py`: four of the flow
PRs #94-#109 edited each. Their state is hundreds of lines of locals passed between ad-hoc helpers (`_loop_status`,
`_ensemble_iteration`, `_reviewers_objected`, `_record_reviewer_rows` and others).

## Scope

1. `ReviewLoop` class in `flow/review_loop.py` holding the loop state (iteration, voted head, findings, budget) with one
   method per step: `resolve_target`, `wait_for_ci`, `run_ensemble`, `record_findings`, `decide`, `post_consensus`.
   `run_review_loop` becomes a thin wrapper for compatibility.
2. `run_review_stage` delegates to it; `run_review_loop_cli` moves to the CLI review command.
3. Iteration verdicts are pure functions over the reviewer results (functional core) and tested without git or `gh`.
4. All functions within the 0185 limits; existing review-loop tests green; fail-closed behaviour unchanged.

## Touch set

`flow/review_loop.py`, `flow/stages/review.py`, `cli/commands/review*.py` (one import), `tests/flow/test_review_loop.py`
and `tests/test_review_loop.py`.

## Dependencies

Blocked by 0191. Sequence with 0160 and 0179, which change the same loop.

## Notes

- Run through the Holon flow on holon-agentic-coder.
