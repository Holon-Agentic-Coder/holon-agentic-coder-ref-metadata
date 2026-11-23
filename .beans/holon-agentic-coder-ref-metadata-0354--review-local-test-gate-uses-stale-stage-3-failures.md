---
# holon-agentic-coder-ref-metadata-0354
title: "Review-loop local test gate keeps reporting stale Stage 3 test failures, so consensus can never close"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-4
  - review-loop
  - ci
  - holon-agentic-coder
created_at: 2026-11-21T18:26:00+11:00
updated_at: 2026-11-22T22:55:00Z
---

## Problem

On 2026-11-21, PR #219 (`checkpoint-and-ledger-ownership`) had 3/3 APPROVED reviews with no findings in iterations 11
and 13-19, and CI was green. Each approval was still followed by a "CI checks failed: local_tests" finding
(FIND-CI-0xx). The resolver rejected it with evidence every time, but it came back each iteration. The loop never posted
consensus and never reached Stage 5, so the flow ran until the iteration cap.

Cause: `_ReviewTestGate` in `flow/review/local_tests.py` reuses the test result Stage 3 recorded (here 4768 passed, 6
failed, 1 errored). `_applies()` re-measures only when Stage 3 recorded neither a rate nor a failure
(`stage_3_rate is None and not stage_3_failed`). Once Stage 3 fails tests, the gate keeps reporting that failure for the
rest of the loop, even after the resolver fixes it and the current tree passes 4992/4992.

## Action

Through the Holon flow on `holon-agentic-coder`:

- The gate judges the current head, not Stage 3's result. When Stage 3 recorded failures, or the head has changed since
  Stage 3, re-measure locally, or accept a green CI run on the current head SHA as evidence.
- A finding the resolver rejected with evidence of a passing run on the same head is not raised again for that head.
- Log which evidence the gate used: Stage 3, a local re-run, or CI on the current head.
- Hermetic tests:
  - Stage 3 failed and the current head passes, so there is no finding and consensus can close;
  - Stage 3 failed and the current head still fails, so the finding is raised;
  - green CI on the current SHA is accepted.

## Notes

- PR #219 also changes `flow/review/loop.py`, so this flow would overlap it until #219 merges.
- Seen alongside a one-off "branch is not fetched from origin" at iteration 20. The remote-tracking ref was rewritten at
  the moment the container checked it, which may be a race on the shared `.git`. Not proven; record it here if it
  happens again.

## Progress

- 2026-11-21: Started Holon flow `review-approved-and-fresh-tests` (claude-agent, claude-opus-5-5), shared with beans
  0347 and 0354.
- 2026-11-23: PR #230 (`flow-review-approved-and-fresh-tests`) is open, CI 11/11 pass, `CLEAN`, last commit `81525dfd`
  (iteration 5 fix), halted at Stage 4 iter 7 on resolver stall timeout (idle). Unblocked to resume now that PR #235
  (`134e333`, Bean `0358` Part 1) merged and images were rebuilt. Bean `0353` was scrapped as a duplicate of `0354`.

## Progress

- PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/230 (flow `review-approved-and-fresh-tests`,
  resumed at Stage 4)
- 2026-11-23: Stage 4 resumed; run 1 halted at iteration 12 when the in-container resolver's merge commit `2467c0fb`
  (origin/main merge) was on the remote but not in the host worktree, so the push was rejected (non-fast-forward).
  Reconciled by merging the remote tip and pushing `97b06fba` (no rewrite). Resume then stopped before Stage 4 dispatch:
  the branch conflicts with `origin/main` at `8afc215a` (#238) in `flow/pipeline.py`, `flow/stages/children.py`,
  `.agents/holon_flow.md`, `docs/git_flow.md` (review-boundary logic, the same code as this bean) and
  `holon-knowledge/ledger/executions.jsonl`. Stage 4 refuses unresolvable conflicts. Blocked on a conflict resolution
  decision; the merge was aborted, worktree clean at `97b06fba`.

- 2026-11-23: Resumed from `--from-stage review` after the conflict resolution (PR head `6a6f6e90`). Flow worktree
  fast-forwarded from `97b06fba` to origin, then the Stage 4 review loop was restarted (checkpoint
  `.holon/flow/checkpoint-review-approved-and-fresh-tests.json`).
