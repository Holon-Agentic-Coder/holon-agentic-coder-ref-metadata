---
# holon-agentic-coder-ref-metadata-0161
title: "Decomposed sub-intents have no flow path to main and do not build on each other"
status: todo
type: feature
priority: high
tags:
  - holon-flow
  - decomposition
  - holon-agentic-coder
created_at: 2026-10-26T07:16:04Z
updated_at: 2026-10-26T07:16:04Z
---

## Problem

Raised by the PR #97 (Bean 0159) iteration-1 review as finding F2, and deferred here because it is bigger than that PR.
Once Bean 0159 runs decomposed sub-intents autonomously (`_run_decomposed_plan` in `sandbox_executor/flow.py`):

1. Each child intent targets the parent intent branch and is cut from it before the earlier child's PR is merged
   (merging is human-only). So "sequential" is only temporal, and dependent children are implemented blind to each
   other.
2. The parent's Stage 4/5 are skipped as `decomposed`, so no PR from the parent intent branch to `main` is ever raised.
   Only root intents reach `main`, so the combined work has no flow route there.

## Scope

- Chain children: child N+1 is cut from child N's execution head, or children are merged into the parent intent branch
  by the flow itself, since that branch is not `main` and merging into it is not a human-only merge to `main`. Decide
  which, and record the decision.
- After all children reach consensus, raise the parent intent branch's PR to its target, run the review loop and
  calibration on the combined diff, and stop at the human merge boundary.
- The flow summary lists every child PR and the parent PR.
- Make the decomposed Stage 3 resume-safe (PR #97 Nit F4): deterministic child branch names (parent branch + index) and
  recorded child progress in the checkpoint, so a resume does not re-dispatch children or duplicate child PRs.
- Tests with fixtures only.

## Notes

- Run through the Holon flow on holon-agentic-coder after Bean 0159 merges. It overlaps `flow.py`, so run it
  sequentially.
