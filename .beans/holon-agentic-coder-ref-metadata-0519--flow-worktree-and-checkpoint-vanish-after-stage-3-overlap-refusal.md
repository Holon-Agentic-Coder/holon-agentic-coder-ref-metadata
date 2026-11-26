---
# holon-agentic-coder-ref-metadata-0519
title: "Flow worktree, checkpoint and intent/plan branches vanish after a Stage 3 overlap refusal"
status: todo
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - holon-agentic-coder
created_at: 2026-11-27T00:10:00+11:00
updated_at: 2026-11-27T00:10:00+11:00
---

## Problem

On 2026-11-26 the flow `module-budget-default-350` (bean 0489) ran intent and plan, then Stage 3 refused on a touch-set
overlap with `I-1795665991-no-unneeded-full-review` (run with `--no-wait-on-overlap`, so it stopped as designed).
Afterwards the flow worktree `apps/holon-agentic-coder/flow-module-budget-default-350` was gone, with its
`.holon/flow/checkpoint-module-budget-default-350.json`, and the local `I-1795686809-module-budget-default-350/*`
branches were gone too. The intent and plan commits (5ac9ddd9, ac3712c8) survive only as unreferenced objects. The
overlapping flow's worktree (`flow-no-unneeded-full-review`) was also absent when checked, though its PR #334 merged
only later.

Parking a refused flow (per the holon-flow skill) depends on keeping the worktree, branches and checkpoint. Nothing in
the harness or the wrapper printed a removal, so the cause is not confirmed; a concurrent cleanup run (for example a
clean-branches or post-merge pass) is one candidate, and the flow engine's own failure path is another.

## Expected

A refused Stage 3 leaves the worktree, the I-/P- branches and the checkpoint in place, so the flow resumes with
`--checkpoint` once the blocker merges.

## Acceptance

- Identify what removed the worktree and branches (check the holon CLI failure path and the clean-branches / post-merge
  skills for `worktree remove` or `branch -D` of `I-*` refs).
- A test or wrapper guard that refuses to delete a parked flow's worktree or checkpoint.
