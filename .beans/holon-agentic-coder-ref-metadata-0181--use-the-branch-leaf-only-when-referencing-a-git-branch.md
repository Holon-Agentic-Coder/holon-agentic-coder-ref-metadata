---
# holon-agentic-coder-ref-metadata-0181
title: "Use the /_ leaf only when referencing a git branch, never on intent, plan or execution ids"
status: todo
type: bug
priority: normal
tags:
  - holon-flow
  - ledger
  - provenance
  - documentation
  - holon-agentic-coder
created_at: 2026-10-29T01:01:35Z
updated_at: 2026-10-29T01:01:35Z
---

## Principle (maintainer, 2026-10-29)

The `/_` leaf exists only so git can hold child branches under a node: `I-…/_` sits next to `I-…/P-…/_`, which sits next
to `I-…/P-…/E-…/_` and `I-…/P-…/I-…/_`. The intent (or plan, or execution) itself does not need `_`; the leaf is
required **only when referencing a git branch**.

Consequences:

- An id is a bare node id with no `/_` and no path: `I-1771890389-refactor-metrics`,
  `P-1771890510-claude-code-claude-sonnet-4.6`, `E-1771890398-init-project`.
- A git branch reference is the full ref with the leaf: `I-1771890389-refactor-metrics/_`, `I-…/P-…/_`, `I-…/P-…/E-…/_`.
  It is what you pass to `git checkout` / `git push`.
- Field names say which one they hold: `…_id` is a bare id; `…_branch` is a full branch ref.
- Ids, slugs, file names (`plans/P-….md`, `executions/E-….md`) and intent hierarchy trees never carry `/_`.

## Problem

`holon-agentic-coder` mixes the two today (observed on `main` `f09ca5e`):

| Field                                                               | Where                              | Holds today                                                           | Rule says                                                             |
| ------------------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `branch`                                                            | `intents.jsonl`, intent JSON input | base name `I-{ts}-{slug}` (no leaf); `intent_creator.py` appends `/_` | ambiguous name: either an id (`intent_id`) or a ref (`intent_branch`) |
| `parent_intent_id`                                                  | sub-intent rows (`flow.py`)        | the parent's branch ref `I-…/_`                                       | a bare id; the ref belongs in `parent_intent_branch`                  |
| `intent_branch`, `plan_branch`, `execution_branch`, `target_branch` | plans, executions, calibration     | full refs with `/_`                                                   | correct                                                               |
| `plan_id`, `execution_id`                                           | plans, executions                  | bare ids                                                              | correct                                                               |

The docs inherited both quirks: the intent spec documents `branch` as a base name, while other examples use
`"branch": "I-…/_"` for a real ref (PR #103 follow-up discussion).

## Scope

Through the Holon flow on `holon-agentic-coder` (code change), after Bean 0161 / Bean 0179 if they overlap `flow.py`:

1. Define the naming rule once (`docs/git_flow.md` section 2 and `docs/ledger_schema.md`): ids bare, `…_branch` fields
   full refs, `/_` only on refs.
2. New `intents.jsonl` rows record `intent_id` (bare) and `intent_branch` (with `/_`); the intent JSON input accepts
   `intent_id` (or keeps `branch` as a deprecated alias, documented as a bare id). Readers keep accepting the legacy
   `branch` field on old rows.
3. New sub-intent rows record a bare `parent_intent_id` plus `parent_intent_branch` (the ref); readers accept the old
   ref-shaped `parent_intent_id` on existing rows. Same for `deciding_branch` / `parent_plan_id` / `parent_execution_id`
   from Bean 0180.
4. Audit every producer and consumer (`intent_creator.py`, `planner.py`, `executor.py`, `flow.py`, `calibration.py`,
   `cli.py`, ledger query) for code that adds or strips `/_` ad hoc; route it through one small helper pair (id → branch
   ref, branch ref → id).
5. Docs: every example follows the rule (refs with `/_`, ids without); list the legacy fields and their old meaning.
6. Tests (pytest, fixtures only): round-trip id ↔ branch ref; old and new row shapes both read; no id ever ends in `/_`;
   every `…_branch` value ends in `/_`.

## Constraints

- The three ledgers stay append-only: old rows are never rewritten; compatibility lives in the readers.
- No harness paths, bean ids or review ids in target files.

## Notes

- Raised while reviewing PR #103 (Bean 0180, documentation only). PR #103 may adopt the documented rule early; the code
  and ledger changes are this bean's.
- Related: Bean 0161 (sub-intent implementation), Bean 0180 (nested sub-intent docs).
