---
# holon-agentic-coder-ref-metadata-0180
title: "Document sub-intent branches nested under the plan that decided the split"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - decomposition
  - documentation
  - holon-agentic-coder
created_at: 2026-10-29T00:38:39Z
updated_at: 2026-10-30T02:00:00Z
---

## Problem

The Bean 0144 split run showed that sub-intent provenance is weak:

- The current flow names a child `{parent}--{n}-{slug}/_`, a flat sibling of the root intent, cut from the root intent
  branch.
- Only `parent_intent_id` is recorded. Nothing records which plan decided the split (`P-1793188831`) or the child's
  position in that plan's `## Sub-intent list`.

`docs/git_flow.md`'s target model nests sub-intents under the parent intent (`I-root/I-sub/_`). An intent can have
several competing plans, though, so that path does not say which plan spawned the sub-intent.

## Decision (maintainer, 2026-10-29)

- Sub-intents nest under the plan that decided the split, with no "child" marker:
  `I-{ts}-{slug}/P-{ts}-{agent}-{model}/I-{ts}-{slug}/_`, recursively.
- **Documentation only** (the target model), **hand-authored in a direct worktree outside the Holon flow** at the
  maintainer's explicit instruction. The maintainer runs the PR review loop manually.

## Scope

In `holon-agentic-coder` docs (`docs/git_flow.md`, `README.md`, `docs/examples.md` and any other doc showing sub-intent
branch names), describe the target model:

1. Nested sub-intent names under the deciding plan; the sub-intent's own plans and executions below it.
2. Provenance: `parent_intent_id` plus `parent_plan_id` and `sub_intent_index` on the sub-intent's intent row and plan
   header.
3. Dependent sub-intents build on earlier siblings' merged work (no blind children).
4. The parent intent's PR to its target after all sub-intents merge.
5. A sub-intent promoted to a root intent records its source plan and index.
6. Splitting is not limited to the plan stage. In practice so far the split happened after planning (the plan's
   `## Sub-intent list`), but a sub-intent may be spawned at any stage (intent, plan, execution, review) as long as the
   hierarchy is honoured: it nests under the node whose stage decided the split (`I-root/I-sub/_`, `I-root/P-…/I-sub/_`,
   `I-root/P-…/E-…/I-sub/_`) and its provenance records that node.

Remove the current-flow notes about flat `{parent}--{n}-{slug}/_` naming and `parent_intent_id`-only provenance
(maintainer, 2026-10-29): the docs describe the nested hierarchy as the rule. No code, tests, prompts or ledgers change.
Implementing the model stays in Bean 0161; until it lands, the code still uses the flat naming.

## Notes

- Worktree: `apps/holon-agentic-coder/docs-0180-nested-sub-intent-branches`, branch
  `docs/0180-nested-sub-intent-branches` from `origin/main` `f09ca5e`.
- Related: Bean 0144 (the split run and its audit branches), Bean 0161 (implementation).

## Progress (2026-10-29)

- Docs change committed as `c27879b` on `docs/0180-nested-sub-intent-branches` and pushed (no PR; the maintainer runs
  the review loop). PR #103 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/103). Four files:
  `docs/git_flow.md`, `README.md`, `docs/examples.md`, `docs/ledger_schema.md`. The commit message names the
  outside-the-flow exception; `uv run task lint-docs` passes.
- Open design questions for the maintainer:
  1. Field name `deciding_branch` (not `parent_branch`, which `flow.py` already uses for the parent intent branch).
  2. A split decided in review nests under the reviewed execution and records `parent_execution_id`.
  3. Branch base and merge target stay the parent intent branch whatever node decided the split. Should an
     execution-decided split start from the execution branch (partial work), or a plan-decided one from the plan branch?
  4. Does a nested parent's combined-diff PR stop for a human, or only a root intent's?
  5. Same-second, same-slug siblings under one deciding node would collide on timestamped ids; add a sequence suffix?
- Follow-ups: the docs are now ahead of the code (`_child_intent_branch` still builds `{parent}--{n}-{slug}`, and no new
  provenance fields are written), tracked for implementation in Bean 0161; the planner template only covers plan-decided
  splits.

- Follow-up commits on PR #103: `8a1e067` (convention-conforming plan and intent ids, no `intent/` prefix), `a4c1803`
  (dropped `sub_intent_index`, maintainer decision), `1ad8d6f` (remaining legacy ids, `/_` leaves, README plan/execution
  examples). Head `1ad8d6f`.
- `8ef9fa0`: every sub-intent tree shows the deciding plan between parent and sub-intents; plan-decided split stated as
  the practice (maintainer). Head `8ef9fa0`.

## Maintainer decisions on the open questions (2026-10-29)

1. **Field name:** keep `deciding_branch`.
2. **Review-decided split:** may nest under the reviewed plan or the reviewed execution; either is acceptable.
3. **Branch base and merge target:** a sub-intent split from a plan merges into that plan branch; one split from an
   execution merges into that execution branch. The deciding node's branch is the target, not the parent intent branch.
4. **Nested human stop:** none. Below the root, the agent raises the sub-intent's PR automatically and merges it
   automatically into the deciding plan or execution branch. Only the root intent's PR to `main` stops for a human.
5. **Sibling collisions:** cannot happen, because siblings under one deciding node always have different slugs.

PR #103 (approved at `2652b8e`, review 5691992073) documents the earlier wording: sub-intents merge into the parent
intent branch, question 4 is left open, and collisions are a question. Decisions 3-5 supersede that.

- Maintainer chose a **follow-up PR**: merge PR #103 as approved, then apply decisions 1-5 in a new docs-only PR cut
  from `origin/main` after the merge (same hand-authored, documentation-only exception as PR #103), reviewed with the
  pr-review-loop. Scope: merge target is the deciding plan/execution branch; nested PRs raised and merged automatically
  by the agent, only the root PR to `main` stops for a human; remove every "open question" pointer for questions 1-5;
  state that sibling slugs always differ.

- PR #103 review loop: 11 iterations, every finding applied (one rejected: iter-1 N3, maintainer ruling). 3/3 ensemble
  approval with zero findings and all 9 CI jobs green at `2652b8e`; consensus posted as COMMENT review 5691992073.
  Awaiting the maintainer's merge. Close this bean after the merge and the follow-up docs PR.
- PR #103 merged by the maintainer at 2026-10-29T02:11:22Z as `e187393`. Worktree and local branch removed. Remaining:
  the follow-up docs PR applying the five rulings.

- **Follow-up docs through the Holon flow (2026-10-29):** flow
  `I-1793275695-docs-sub-intent-merge-target-and-automatic-nested-prs` → `P-1793275710-claude-agent-claude-opus-5-5` →
  `E-1793275898-claude-agent-claude-opus-5-5`; PR #110
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/110) in Stage 4 review (iteration 3 at `06ff902`).
  Close this bean when it merges.
- PR #110 reviewed (consensus COMMENT review), calibrated
  (`plans/P-1793275710-claude-agent-claude-opus-5-5_calibration.md` in the PR) and merged by the maintainer as `85ef122`
  (2026-10-29T14:37:07Z). Ready to close. Its review loop found five more documents on the old rules; Bean 0210 carries
  them.

## Summary of Changes (2026-10-30)

PR #103 (nested sub-intent branches) and PR #110 (the five maintainer rulings: merge into the deciding plan or execution
branch, nested PRs automatic, sibling slugs distinct, keep `deciding_branch`, review-decided splits under plan or
execution) are both merged (`e187393`, `85ef122`). PR #110: 8 review iterations, 3/3 at `7ed151c` (review 5698216018),
calibrated (`9117677`, EV 43.92 / 60.51). Five docs outside its touch set still state the old rules: Bean 0210.
