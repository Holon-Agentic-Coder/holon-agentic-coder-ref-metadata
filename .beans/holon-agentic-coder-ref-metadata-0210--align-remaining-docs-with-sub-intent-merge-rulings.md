---
# holon-agentic-coder-ref-metadata-0210
title: "Align the remaining holon-agentic-coder docs with the sub-intent merge rulings"
status: completed
type: task
priority: normal
tags:
  - documentation
  - holon-flow
  - sub-intents
  - holon-agentic-coder
created_at: 2026-10-30T00:10:00Z
updated_at: 2026-10-30T01:41:00Z
---

## Problem

holon-agentic-coder PR #110 (Bean 0180) applied the maintainer's five sub-intent rulings to README.md,
`docs/git_flow.md`, `docs/examples.md`, `docs/core_concepts.md` and `docs/ledger_schema.md`. Its review loop (iteration
1, Important) found five more documents outside that change's touch set that still state the old rules (a sub-intent
merges into the parent intent branch; whether a nested parent's PR stops for a human is open):

- `docs/agent_design.md`
- `docs/architecture.md`
- `docs/faq.md`
- `docs/safety.md`
- `docs/planner/planning_architecture_specification.md`

## Scope

- Apply the same rulings to those five documents (merge into the deciding plan or execution branch; nested PRs raised
  and merged automatically by the agent, only the root PR to `main` stops for a human; sibling slugs always differ; keep
  `deciding_branch`), consistent with the wording PR #110 established.
- Sweep the whole `docs/` tree once more for any other statement of the old rules.
- Documentation only; run through the Holon flow on holon-agentic-coder. Unblocked: PR #110 merged as `85ef122`
  (2026-10-29T14:37:07Z).

## Notes

- Related: Bean 0180 (PR #110), Bean 0161 (implementation of the rulings).

## Resolution (2026-10-30)

- Delivered through the full 5-stage Holon flow on `holon-agentic-coder` via PR #113
  (`I-1793319507-remaining-docs-follow-sub-intent-merge-rulings/P-1793319521-claude-agent-claude-opus-5-5/E-1793319691-claude-agent-claude-opus-5-5/_`).
- Updated `docs/agent_design.md`, `docs/architecture.md`, `docs/faq.md`, `docs/safety.md`,
  `docs/planner/planning_architecture_specification.md`, and `docs/planning_and_evaluation.md` to align with the five
  sub-intent rulings established in PR #110 (`85ef122`).
- Passed 3/3 ensemble consensus review in 5 iterations at head `cb4457f` (posted 2026-10-30T01:14:02Z), completed Stage
  5 calibration (`9dc6e92`, Prettier-formatted `450b445`), and merged into `main` as `760ee87` (2026-10-30T01:27:16Z).
