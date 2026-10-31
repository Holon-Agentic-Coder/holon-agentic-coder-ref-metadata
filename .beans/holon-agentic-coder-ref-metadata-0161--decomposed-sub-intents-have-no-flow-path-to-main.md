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
updated_at: 2026-10-30T01:41:00Z
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

- **2026-10-27, PR #97 (Bean 0159) delivered part of the groundwork:**
  - children run sequentially under a depth cap;
  - child branches are named `{parent}--{n}-{slug}`, and are reused only when the recorded goal and description match;
  - a sub-intent's checkpoint is keyed by its intent branch;
  - the flow summary lists child and grandchild PRs and the pending parent-to-target step.

  Still open: chaining children so each builds on the previous one, raising the parent PR automatically, and full resume
  safety of the decomposed Stage 3.

- Run through the Holon flow on holon-agentic-coder after Bean 0159 merges. It overlaps `flow.py`, so run it
  sequentially.
- 2026-10-30: the 0159 prerequisite is satisfied. Bean 0159 is completed (holon-agentic-coder PR #97, merged as
  `fbd3b35`); the `flow.py` overlap still makes it sequential (see Bean 0187).

## Maintainer decisions to implement (2026-10-29, from Bean 0180)

- Sub-intent branches nest under the node that decided the split (`I-…/P-…/I-…/_`, no `child` or index segment); in
  practice the plan decides. Record `deciding_branch` (name kept), `parent_intent_id`, `parent_plan_id` and, for an
  execution- or review-decided split, `parent_execution_id`.
- A review-decided split may nest under the reviewed plan or the reviewed execution.
- Merge target is the deciding node's branch: a plan-decided sub-intent merges into the plan branch, an
  execution-decided one into the execution branch (not the parent intent branch).
- Nested PRs need no human: the agent raises each sub-intent's PR and merges it automatically into the deciding
  plan/execution branch. Only the root intent's PR to `main` stops for a human.
- Sibling sub-intents under one deciding node always have different slugs, so ids cannot collide; no sequence suffix.
- Documented in PR #103 (merged, `e187393`), follow-up docs PR #110 (merged as `85ef122`, 2026-10-29T14:37:07Z), and
  remaining-docs sweep PR #113 (Bean 0210, merged as `760ee87`, 2026-10-30T01:27:16Z).
