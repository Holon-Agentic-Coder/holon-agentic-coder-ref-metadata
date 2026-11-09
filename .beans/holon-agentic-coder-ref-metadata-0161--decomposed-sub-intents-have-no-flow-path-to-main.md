---
# holon-agentic-coder-ref-metadata-0161
title: "Decomposed sub-intents have no flow path to main and do not build on each other"
status: in-progress
type: feature
priority: critical
tags:
  - holon-flow
  - decomposition
  - holon-agentic-coder
created_at: 2026-10-26T07:16:04Z
updated_at: 2026-11-09T13:00:00Z
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

## Corrected design (maintainer ruling, 2026-11-09)

Found while running Bean 0262 (decomposed into 4 sub-intents; PRs #152 and #155). **The decision to split belongs to the
plan, and the execution only executes the children.** The current flow decides it in the execution and cuts children
from the wrong branch.

### What the Bean 0262 run did (evidence)

- Parent chain: `main` → `I-1794214501-…/_` → `I-…/P-1794214522-…/_` (plan, with a prose `## Sub-intent list`) →
  `I-…/P-…/E-1794214787-…/_` (execution: one commit adding 2 rows to `executions.jsonl`, a summary row with
  `status: decomposed` and the machine-readable `sub_intents` list, plus an action row). `_run_decomposed_plan` reads
  the list from that **execution** row.
- Each child (`I-…--1-add-host…/_`) was cut from the parent **intent** branch, a sibling of the parent plan, and its PR
  (#152) targets that intent branch. Neither the parent plan branch nor the parent execution branch is an ancestor of
  the child, so the parent plan file never appears in a child PR and never reaches `main`.
- Stage 2 already evaluates the rule: `_plan_budget_decision` calls the executor's own `should_decompose` on the plan
  row and plan file, which parses the plan's sub-intent list, before the executor container is dispatched. The decision
  exists at plan time; it is just recorded late, by the executor.
- Resuming the decomposed flow from the parent checkpoint re-ran sub-intent 1 from scratch (a new intent, plan and
  execution) instead of resuming its review, opened a duplicate PR (#155) and overwrote the child's checkpoint.

### Required behaviour

1. **Stage 2 records the decision.** After the planner writes the plan, the plan stage records the decomposition
   decision (decision, entropy, budget and the `sub_intents` list: slug, description, goal) on the plan's `plans.jsonl`
   row, on the plan branch, using the single existing `should_decompose` rule. The plan branch is self-describing.
2. **Stage 3 only executes.** For a decomposed plan the executor container does not re-decide or write the sub-intent
   list. The execution runs the recorded child sub-intents, and its summary row refers to the children and to the plan's
   recorded decision.
3. **Children nest under and target the plan branch.** Each child intent is cut from the plan branch (`I-…/P-…/_`), its
   branch nests under the plan, and its PR targets the plan branch, not the intent branch and never `main`.
4. **Children build on each other.** Child N+1 sees child N's work (see the open decision below).
5. **A combined PR reaches `main`.** After all children, the integration PR from the plan's branch to `main` is raised
   with the review loop and calibration on the combined diff, carrying the parent plan, the parent execution record and
   every child plan and execution, and stops at the human merge boundary.
6. **Resume safety.** A resume continues an existing child (its execution branch and PR) at the stage it stopped, and
   never re-dispatches a child that already has an execution branch or PR, never opens a duplicate PR and never
   overwrites a child's checkpoint. Deterministic child names stay.
7. **Docs.** `docs/architecture.md` and `docs/git_flow.md` stop describing the interim "parent intent branch" behaviour.

### Decision (maintainer, 2026-11-09): the flow merges child PRs into the plan branch

After a child's Stage 4 consensus and Stage 5 calibration (the calibration report is in the child PR first), the flow
engine merges that child PR into the plan branch with a merge commit (not squash or rebase, so the child's commits stay
ancestors), only when CI is green and the PR is mergeable. The engine refuses to merge any PR whose base is `main` or
another default branch. `AGENTS.md` carries the matching narrow exception; agents still never merge by hand. The
combined PR from the plan branch into `main` stops for the human maintainer.

**Widened by the maintainer on 2026-11-09:** any PR that does not target `main` may be merged autonomously, by the flow
engine or by an agent. `AGENTS.md` carries the ruling and its pre-merge checks. The combined PR from the plan branch
into `main` still stops for the human maintainer.

## Run on the old engine, fixed up by hand (maintainer instruction, 2026-11-09)

The Bean 0161 flow (`I-1794224634-plan-owned-decomposition-with-plan-branch-children`) was itself over the entropy
budget (18.6 against 15.0) and the plan split it into two child intents, so it runs on the old engine it is meant to
replace:

1. Record the decomposition decision on the plan row, and make Stage 3 execute only that recorded decision.
2. Nest decomposed children under the plan branch, merge each child PR into it, raise the combined PR and resume safely.

Both children are cut from the parent **intent** branch, child 2 before child 1 has merged, and neither PR has a route
to `main`. The maintainer chose to let the flow run and to fix it up by hand:

- When a child reaches consensus and calibration, merge its PR into the parent intent branch (allowed: its base is not
  `main`), resolving ledger-only conflicts by interleaving on `created_at`. Child 2 may have been written blind to child
  1; expect and resolve overlap in the shared files.
- When both are in, raise the combined PR from the parent intent branch into `main` by hand, with the parent plan and
  execution records and both children's plans and executions, then stop for the maintainer.

**Exception to the sole-change-path rule:** the child merges and the combined PR are done outside the flow at the
maintainer's explicit instruction, and this bean and the commit messages name it.

**Review of the combined PR (maintainer instruction, 2026-11-09):** the single PR into `main` goes through the review
loop (reviewer ensemble and resolver, iterating to unanimous consensus with every nit actioned) before it is handed
over, even though it was assembled by hand. The `pr-review-loop` skill drives it, since `holon review-loop` alone runs
one pass and has no resolver. Hand over only after consensus, with CI green and the PR mergeable against `main`.

## Progress (2026-11-10)

Both children finished and were merged by hand into the parent intent branch with merge commits: child 1 (PR #156, plan
records the decision) and child 2 (PR #157, nest under the plan branch, merge, combined PR, resume safety). The parent
plan and execution record were merged in first. Overlap resolved by hand (ledger rows interleaved; two hunks kept
plan-owned; snapshot regenerated on Python 3.13; one child 1 test adapted). **Combined
[PR #158](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/158) into `main` is open** and is in the
`pr-review-loop` (reviewer ensemble and resolver). Deferrals from that loop are in Bean 0269. Hand over only after
unanimous consensus with CI green; merging into `main` stays with the maintainer.
