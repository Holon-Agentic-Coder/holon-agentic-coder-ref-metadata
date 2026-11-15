---
# holon-agentic-coder-ref-metadata-0301
title: "Empty-diff guard compares a decomposed flow's combined execution branch against the right base"
status: completed
type: bug
priority: critical
tags:
  - holon-flow
  - decomposition
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-15T09:00:00Z
updated_at: 2026-11-15T21:51:04Z
---

## Problem

Stage 4 refuses to open the final pull request of a decomposed flow:
`Execution produced no changes outside holon-knowledge/ledger/, plans/ and executions/ relative to <plan branch> (compared on origin)`.
The guard (`flow/git_refs.py`, using `git.empty_diff_summary` and `EMPTY_DIFF_EXCLUDES`) compares the combined execution
branch against the plan branch. In plan-owned decomposition the child pull requests are merged into that very plan
branch, and the combined execution branch integrates it, so the diff against the plan branch is ledger and plan files
only, even though 71 non-ledger files differ from `main`. Seen on the touchset flow (2026-11-15): both child PRs (#194,
#200) merged, Stage 3 completed, and Stage 4 refused at once, so the flow cannot reach review.

## Scope

1. For a decomposed flow, compare the combined execution branch against the plan's base on `main` (the merge base with
   `origin/main`, or the plan branch's first-parent base before any child merged), not against the plan branch that
   absorbed the children. The guard for a plain (non-decomposed) execution is unchanged.
2. Keep the guard failing closed: a combined branch whose diff against that base is ledger-only is still refused.
3. Hermetic tests: decomposed layout with children merged into the plan branch (guard passes), the same layout with only
   ledger changes (guard refuses), a plain execution (unchanged), and the compared-on-origin path.

## Notes

- Run through the Holon flow on holon-agentic-coder. Blocks Bean 0151 (its combined branch is pushed and conflict-free,
  at merge commit `9840611b`, and only needs this guard fixed to open its final PR).
- Related: Bean 0297 (Stage 5 reruns when the head moves), and the engine findings from 2026-11-15 (sticky skip flags
  across resumes, halt-after-approval skipping Stage 5, calibrate refusing a local branch ahead of origin).

## Resolution

Delivered via [PR #201](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/201) and merged into `main`
(`05bd8bab`):

- **Key Architectural Deliverables**: the empty-diff guard now compares a decomposed flow's combined execution branch
  against the plan's base on `main` (new `flow/combined_base.py`; changes in `flow/git_refs.py`, `git.py` and
  `review_target.py`; module budgets updated). The guard stays fail-closed: a combined branch whose diff against that
  base is ledger-only is still refused. Plain executions are unchanged.
- **Verification & Tests**: hermetic `test_combined_base.py` and `test_git.py` cover the decomposed layout with children
  merged (passes), ledger-only changes (refused), a plain execution, and the compared-on-origin path. Full suite: 4085
  tests passed. Calibration report is in the PR diff (EV predicted 53.71, actual 71.50).
- **Holon Flow Traversal**: all 5 stages completed. Consensus review 3/3 (score 1.0, 3 iterations).
- **Unblocks**: Bean 0151 (combined branch at merge commit `9840611b`, now resumable from review; stays in-progress).
